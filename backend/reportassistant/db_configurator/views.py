import os
import uuid
from io import BytesIO
from uuid import uuid4

import pandas
import pandas as pd
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404

from common.db.manager.database_manager import DatabaseManager
from common.graph_db.graph_db import Neo4JInstance
from common.vectordb.db import COLLECTION_NAME
from common.vectordb.db.utils import delete_docs_from_collection
from .models import DatabaseSource, Status, SourceType
from .forms import DatabaseSourceForm
from .tasks import load_db, load_excel
from django.utils.translation import gettext as _



@permission_required("db_configurator.view_databasesource")
def manage_connections(request):
    databases = DatabaseSource.objects.filter(source_type=SourceType.DB.value)
    excels = DatabaseSource.objects.filter(source_type=SourceType.EXCEL.value)
    form = DatabaseSourceForm()
    return render(request, 'db_configurator/manage_connections.html', {
        'form': form,
        'excels': excels,
        'databases': databases,
    })

@permission_required("db_configurator.add_databasesource")
def connection(request):
    if request.method == 'POST':
        db_source = None
        if request.POST.get('id'):
            db_source = DatabaseSource.objects.get(pk=request.POST.get('id'))

        form = DatabaseSourceForm(request.POST, instance=db_source)
        form.user = request.user
        if not form.is_valid():
            return JsonResponse({"success": False, "errors": form.errors.as_json()})

        database_source = DatabaseSource(
            name=form.cleaned_data['name'],
            type=form.cleaned_data["type"],
            host=form.cleaned_data["host"],
            port=form.cleaned_data["port"],
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
            user=request.user
        )
        success = DatabaseManager(database_source).check_connection()
        if success:
            if request.POST.get('id'):
                form.save()
                return JsonResponse({"success": True})

            group_name = "database_source_group_" + form.cleaned_data["name"] + "_" + form.cleaned_data["type"]
            existing_groups = Group.objects.filter(name__startswith=group_name)

            if existing_groups.exists():
                latest_group = existing_groups.order_by('-id').first()
                unique_name = f"{group_name}_{latest_group.id + 1}"
            else:
                unique_name = group_name
            new_group = Group.objects.create(name=unique_name)

            form.instance.group = new_group
            saved_data = form.save()
            load_db.enqueue(saved_data.id, request.user.id)

            return JsonResponse({'success': True})
        else:
            for field in ['host', 'port', 'username', 'password', "name", "type"]:
                form.add_error(field, ValidationError(_("Could not connect to database"), code="ConnectionError"))
            return JsonResponse({'success': False, "errors": form.errors.as_json()})

@login_required()
def excel_to_database_source(request):
    if request.method == 'POST':
        display_name = request.POST.get('display_name')
        files = request.FILES.getlist('files')
        request_uuid = str(uuid.uuid4())
        files_dir = './files'
        if not os.path.exists(files_dir):
            os.makedirs(files_dir)

        uuid_dir = os.path.join(files_dir, request_uuid)
        os.makedirs(uuid_dir)
        for file in files:
            filename = file.name.lower()
            if not filename.endswith('.xlsx') and not filename.endswith('.csv'):
                return HttpResponseBadRequest(content="Only csv and xlsx are supported")
            file_path = os.path.join(uuid_dir, file.name)

            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

        group_name = "database_source_group_" + "excel" + "_" + files[0].name.lower()
        existing_groups = Group.objects.filter(name__startswith=group_name)
        if existing_groups.exists():
            latest_group = existing_groups.order_by('-id').first()
            unique_name = f"{group_name}_{latest_group.id + 1}"
        else:
            unique_name = group_name
        group = Group(name=unique_name)
        group.save()
        group.user_set.add(request.user)
        database_source = DatabaseSource(
            name=os.getenv("EXCEL_STORE_DB_NAME"),
            display_name=display_name,
            type=os.getenv("EXCEL_STORE_DB_TYPE"),
            host=os.getenv("EXCEL_STORE_DB_HOST"),
            port=os.getenv("EXCEL_STORE_DB_PORT"),
            username=os.getenv("EXCEL_STORE_DB_USER"),
            password=os.getenv("EXCEL_STORE_DB_PASSWORD"),
            group=group,
            user=request.user,
            source_type=SourceType.EXCEL
        )
        database_source.save()

        load_excel.enqueue(database_source.id, request.user.id, uuid_dir)
        return redirect('db_configurator:manage_connections')

@permission_required("db_configurator.delete_databasesource")
def delete_database(request, pk):
    database = get_object_or_404(DatabaseSource, pk=pk)
    delete_docs_from_collection(collection_name=COLLECTION_NAME, column_name="database_id", value=database.id)
    neo4j_instance = Neo4JInstance()
    neo4j_instance.clear_graph_database(database.id)
    if database.schema_name:
        DatabaseManager(database).drop_schema(database.schema_name)

    database.group.delete()
    database.delete()
    return redirect('db_configurator:manage_connections')

@permission_required("db_configurator.change_databasesource")
def pause_connection(request, pk):
    database = get_object_or_404(DatabaseSource, pk=pk)

    if database.status != Status.ERROR.value and database.status != Status.LOADING.value:
        database.status = Status.PAUSED.value if database.status == Status.READY.value else Status.READY.value
        database.save()
    return redirect('db_configurator:manage_connections')

@login_required
def get_user_databases(request):
    if request.method == 'GET':
        if not request.user.is_superuser:
            user_groups = request.user.groups.all()
            databases = DatabaseSource.objects.filter(group__in=user_groups, status=Status.READY.value)
        else:
            databases = DatabaseSource.objects.filter(status=Status.READY.value)

        return JsonResponse(data=[{'id': database.id, 'name': database.name, 'display_name': database.display_name} for database in databases], safe=False)
    else:
        return HttpResponseNotAllowed(permitted_methods=["GET"])