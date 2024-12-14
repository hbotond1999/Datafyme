from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404

from common.db.manager.database_manager import DatabaseManager
from common.graph_db.graph_db import Neo4JInstance
from common.vectordb.db import COLLECTION_NAME
from common.vectordb.db.utils import delete_docs_from_collection
from .models import DatabaseSource, Status
from .forms import DatabaseSourceForm
from .tasks import load_db


@permission_required("db_configurator.view_databasesource")
def manage_connections(request):
    databases = DatabaseSource.objects.all()
    form = DatabaseSourceForm()
    return render(request, 'db_configurator/manage_connections.html', {
        'form': form,
        'databases': databases,
    })

@permission_required("db_configurator.add_databasesource")
def add_connection(request):
    if request.method == 'POST':
        form = DatabaseSourceForm(request.POST)

        if not form.is_valid():
            return JsonResponse({"success": False, "errors": form.errors.as_json()})

        database_source = DatabaseSource(
            name=form.cleaned_data['name'],
            type=form.cleaned_data["type"],
            host=form.cleaned_data["host"],
            port=form.cleaned_data["port"],
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )
        success = DatabaseManager(database_source).check_connection()
        if success:
            group_name = "database_source_group_" + form.cleaned_data["name"] + "_" + form.cleaned_data["type"]
            existing_groups = Group.objects.filter(name__startswith=group_name)

            if existing_groups.exists():
                count = existing_groups.count()
                unique_name = f"{group_name}_{count + 1}"
            else:
                unique_name = group_name
            new_group = Group.objects.create(name=unique_name)

            form.instance.group = new_group
            saved_data = form.save()
            load_db.enqueue(saved_data.id)

            return JsonResponse({'success': True})
        else:
            for field in ['host', 'port', 'username', 'password', "name", "type"]:
                form.add_error(field, ValidationError("Could not connect to database", code="ConnectionError"))
            return JsonResponse({'success': False, "errors": form.errors.as_json()})



@permission_required("db_configurator.delete_databasesource")
def delete_database(request, pk):
    database = get_object_or_404(DatabaseSource, pk=pk)
    delete_docs_from_collection(collection_name=COLLECTION_NAME, column_name="database_id", value=database.id)
    neo4j_instance = Neo4JInstance()
    neo4j_instance.clear_graph_database(database.id)
    database.group.delete()
    database.delete()
    return redirect('db_configurator:manage_connections')

@permission_required("db_configurator.change_databasesource")
def pause_connection(request, pk):
    database = get_object_or_404(DatabaseSource, pk=pk)
    # Toggle the is_paused value
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