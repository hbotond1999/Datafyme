from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotAllowed

from db_configurator.models import DatabaseSource
from reporter_agent.models import Chart
from reporter_agent.reporter.subgraph.sql_statement_creator.ai.graph import create_sql_agent_graph
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
        return JsonResponse(data={"chart_data": chart_data, "type": chart.type}, safe=False, status=200)
    else:
        return HttpResponseNotAllowed(['GET'])
