from django.shortcuts import render, redirect, get_object_or_404
from .models import DatabaseSource
from .forms import DatabaseSourceForm

def establish_connections(request):
    if request.method == 'POST':
        form = DatabaseSourceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('db_configurator:establish_connections')
    else:
        form = DatabaseSourceForm()

    databases = DatabaseSource.objects.all()
    return render(request, 'db_configurator/establish_connections.html', {
        'form': form,
        'databases': databases,
    })

def manage_connections(request):
    databases = DatabaseSource.objects.all()
    return render(request, 'db_configurator/manage_connections.html', {
        'databases': databases,
    })

def delete_database(request, pk):
    database = get_object_or_404(DatabaseSource, pk=pk)
    database.delete()
    return redirect('db_configurator:manage_connections')

def pause_connection(request, pk):
    database = get_object_or_404(DatabaseSource, pk=pk)
    # Toggle the is_paused value
    database.is_paused = not database.is_paused
    database.save()
    return redirect('db_configurator:manage_connections')
