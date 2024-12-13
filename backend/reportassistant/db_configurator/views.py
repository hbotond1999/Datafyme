from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from common.db.manager.database_manager import DatabaseManager
from common.graph_db.graph_db import Neo4JInstance
from common.vectordb.db import COLLECTION_NAME
from common.vectordb.db.utils import delete_docs_from_collection
from dbloader.services import DBLoader
from .models import DatabaseSource
from .forms import DatabaseSourceForm

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
            type=form.cleaned_data["type"],
            host=form.cleaned_data["host"],
            port=form.cleaned_data["port"],
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )
        success = DatabaseManager(database_source).check_connection()
        if success:
            saved_data = form.save()
            errors = DBLoader(saved_data).load()
            if len(errors) > 0:
                saved_data.delete()
                for error in errors:
                    form.add_error('type', error)
                return JsonResponse({"success": False, "errors": form.errors.as_json()})

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
    database.delete()
    return redirect('db_configurator:manage_connections')

@permission_required("db_configurator.change_databasesource")
def pause_connection(request, pk):
    database = get_object_or_404(DatabaseSource, pk=pk)
    # Toggle the is_paused value
    database.is_paused = not database.is_paused
    database.save()
    return redirect('db_configurator:manage_connections')
