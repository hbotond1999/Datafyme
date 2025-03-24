import json
from uuid import uuid4

import anthropic
from django.core.files.storage import FileSystemStorage
from django.utils.translation import gettext_lazy as _
import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse, HttpResponseNotAllowed
from django.utils.translation import get_language
from langchain_google_genai import ChatGoogleGenerativeAI
import pandas as pd
from django.http import HttpResponse
import io
from datetime import datetime
import re
from common.db.manager.database_manager import DatabaseManager
from db_configurator.models import DatabaseSource
from reporter_agent.models import Chart, GenAIModel, GenAIModelTypes
from reporter_agent.reporter.subgraph.sql_statement_creator.ai.graph import create_sql_agent_graph
from reporter_agent.reporter.subgraph.visualisation_agent.chart_description.chart_description_agent import \
    create_description
from reporter_agent.utils.chart_data import create_chart_data


@login_required
def sql_agent(request):
    message = request.GET.get('message')
    database_id = request.GET.get('database_id')

    datasource = DatabaseSource.objects.get(id=database_id)

    sql_graph = create_sql_agent_graph()
    result = sql_graph.invoke({"message": message, "database_source": datasource})

    return JsonResponse(data={"sql_query": result["sql_query"], "query_description": result["query_description"]},
                        safe=False)

@login_required
def get_chart(request, chart_id: int):
    if request.method == 'GET':
        chart = Chart.objects.get(id=chart_id)
        chart_data = create_chart_data(chart)
        return JsonResponse(data={"chart_data": chart_data, "type": chart.type, "description": chart.description}, safe=False, status=200)
    else:
        return HttpResponseNotAllowed(['GET'])

@login_required
def edit_chart(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        chart_id = body['id']

        chart = get_object_or_404(Chart, id=chart_id)

        chart.title = body['title']
        chart.save()

        return JsonResponse({'message': 'Chart updated successfully'})
    else:
        return HttpResponseNotAllowed(['POST'])


@login_required
def generate_description(request):
    if request.method == 'POST':
        chart_id = request.POST["chart_id"]
        chart_img_file = request.FILES.get("chart_img_file", None)
        fs = FileSystemStorage(location="files")
        if chart_img_file:
            file = fs.save(str(uuid4()) + ".png", chart_img_file)
            url = fs.path(file)
        else:
            url = None

        chart = Chart.objects.get(id=chart_id)
        chart.chart_img_url = url
        chart.save(update_fields=["chart_img_url"])

        result = create_description(chart_id, url, get_language())
        return JsonResponse(data={"description": result.description})
    else:
        return HttpResponseNotAllowed(['POST'])


@login_required(login_url='/login')
def download_chart(request, chart_id):


    chart = get_object_or_404(Chart, id=chart_id)

    data = DatabaseManager(db_source=chart.data_source).execute_sql(chart.sql_query, response_format="list")
    df = pd.DataFrame(data)

    buffer = io.BytesIO()
    df.to_excel(buffer, sheet_name='Chart Data', index=False, engine='xlsxwriter')

    buffer.seek(0)

    if hasattr(chart, 'title') and chart.title:
        sanitized_title = re.sub(r'[\\/*?:"<>|]', '', chart.title)
        sanitized_title = sanitized_title.replace(' ', '_')
        filename = f"{sanitized_title if sanitized_title else 'table'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    else:
        filename = f"chart_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


@permission_required("reporter_agent.add_genaimodel")
def genai_model_list(request):
    """GenAI modellek listázása"""
    models = GenAIModel.objects.all().order_by('-active', 'provider')
    return render(request, 'reporter_agent/model-list.html', {'models': models})


@permission_required("reporter_agent.add_genaimodel")
def genai_model_create(request):
    """Új GenAI modell létrehozása"""
    if request.method == 'POST':
        provider = request.POST.get('provider')
        name = request.POST.get('name')
        api_key = request.POST.get('api_key')
        active = request.POST.get('active') == 'on'

        # Ha az új modell aktív lesz, akkor a többit deaktiváljuk
        if active:
            GenAIModel.objects.filter(active=True).update(active=False)

        GenAIModel.objects.create(
            provider=provider,
            name=name,
            api_key=api_key,
            active=active
        )
        messages.success(request, 'GenAI modell sikeresen létrehozva!')
        return redirect('reporter_agent:genai_model_list')

    return render(request, 'reporter_agent/model_form.html', {
        'providers': GenAIModelTypes,
        'action': 'create'
    })

@permission_required("reporter_agent.add_genaimodel")
def genai_model_edit(request, model_id):
    """GenAI modell szerkesztése"""
    model = get_object_or_404(GenAIModel, id=model_id)

    if request.method == 'POST':
        model.provider = request.POST.get('provider')
        model.name = request.POST.get('name')
        model.api_key = request.POST.get('api_key')
        new_active = request.POST.get('active') == 'on'

        # Ha ez a modell aktív lesz, akkor a többit deaktiváljuk
        if new_active and not model.active:
            GenAIModel.objects.filter(active=True).update(active=False)
            model.active = True
        elif not new_active and model.active:
            # Ha ez volt az aktív modell és deaktiváljuk, figyelmeztetjük a felhasználót
            messages.warning(request, 'Figyelem: nincs aktív GenAI modell!')
            model.active = False

        model.save()
        messages.success(request, 'GenAI modell sikeresen frissítve!')
        return redirect('reporter_agent:genai_model_list')

    return render(request, 'reporter_agent/model_form.html', {
        'model': model,
        'providers': GenAIModelTypes,
        'action': 'edit'
    })

@permission_required("reporter_agent.add_genaimodel")
def genai_model_delete(request, model_id):
    """GenAI modell törlése"""
    model = get_object_or_404(GenAIModel, id=model_id)

    if request.method == 'POST':
        was_active = model.active
        model.delete()
        if was_active:
            messages.warning(request,
                             'Az aktív GenAI modell törölve lett. Kérjük, állítson be egy másik aktív modellt!')
        else:
            messages.success(request, 'GenAI modell sikeresen törölve!')
        return redirect('reporter_agent:genai_model_list')

    return render(request, 'reporter_agent/model-delete.html', {'model': model})


@permission_required("reporter_agent.add_genaimodel")
def test_api_key(request):
    """API endpoint to test API key by sending a simple test message to the model using LangChain"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            provider = data.get('provider')
            api_key = data.get('api_key')
            model_name = data.get('model_name', '')

            test_message = "Hello, world!"

            # Results of the test
            result = {
                'success': False,
                'message': '',
                'models': []
            }

            # Test the API key based on provider using LangChain
            if provider == 'openai':
                result = test_openai_with_langchain(api_key, model_name, test_message)
            elif provider == 'claude':
                result = test_claude_with_langchain(api_key, model_name, test_message)
            elif provider == 'google':
                result = test_google_with_langchain(api_key, model_name, test_message)
            else:
                return JsonResponse({'success': False, 'message': 'Ismeretlen szolgáltató'}, status=400)

            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Hiba: {str(e)}'}, status=400)

    return JsonResponse({'success': False, 'message': 'Érvénytelen kérés'}, status=400)


def test_openai_with_langchain(api_key, model_name, test_message):
    """Test OpenAI API key using LangChain"""
    try:
        from langchain_openai import ChatOpenAI

        test_model = model_name if model_name else 'gpt-4o-mini'

        chat = ChatOpenAI(
            model=test_model,
            openai_api_key=api_key,
            max_tokens=10
        )

        response = chat.invoke(test_message)
        return {
            'success': True,
            'message': 'API kulcs érvényes és működőképes.',
            'models': get_openai_models(api_key)
        }
    except Exception as e:
        return {'success': False, 'message': f'API kulcs teszt sikertelen: {str(e)}'}


def test_claude_with_langchain(api_key, model_name, test_message):
    """Test Claude API key using LangChain"""
    try:
        from langchain_anthropic import ChatAnthropic

        test_model = model_name if model_name else 'claude-3-7-sonnet-20250219'

        chat = ChatAnthropic(
            model=test_model,
            api_key=api_key,
            max_tokens=10
        )

        response = chat.invoke(test_message)

        return {
            'success': True,
            'message': 'API kulcs érvényes és működőképes.',
            'models': get_claude_models(api_key)
        }
    except Exception as e:
        return {'success': False, 'message': f'API kulcs teszt sikertelen: {str(e)}'}


def test_google_with_langchain(api_key, model_name, test_message):
    """Test Google API key using LangChain"""
    try:

        chat = ChatGoogleGenerativeAI(
            model="models/gemini-2.0-flash",
            api_key=api_key,
            max_output_tokens=10
        )

        response = chat.invoke(test_message)

        return {
            'success': True,
            'message': _('API kulcs érvényes és működőképes.'),
            'models': get_google_models(api_key)
        }
    except Exception as e:
        return {'success': False, 'message': _('API kulcs teszt sikertelen') + f': {str(e)}'}


def get_openai_models(api_key):
    """OpenAI modellek lekérdezése"""

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    response = requests.get('https://api.openai.com/v1/models', headers=headers)
    response.raise_for_status()
    data = response.json()
    return [model['id'] for model in data['data'] if 'gpt' in model['id']]



def get_claude_models(api_key):
    """Claude modellek lekérdezése"""

    client = anthropic.Anthropic(api_key=api_key)
    models = client.models.list(limit=100)
    return [model.id for model in models]


def get_google_models(api_key):
    """Google modellek lekérdezése"""
    import requests
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.get(
        "https://generativelanguage.googleapis.com/v1beta/models?key=" + api_key,
        headers=headers
    )
    models = []
    if response.status_code == 200:
        data = response.json()
        for model in data.get("models", []):
            if  "generateContent" in model["supportedGenerationMethods"]:
                models.append(model["name"])

    return models