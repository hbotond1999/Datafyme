import asyncio

from django.http import JsonResponse

from db_configurator.models import DatabaseSource
from dbloader.services.utils.db_schema.schema_extractor import DatabaseSchemaExtractor
from dbloader.services.vector_loader.loader import VectorLoader


# Create your views here.
def loader(request):
    try:
        datasource, created = DatabaseSource.objects.get_or_create(
            name="postgres",
            defaults={
                "type": "postgresql",  # Set default values for other fields
                "username": "postgres",
                "password": "password",
                "host": "localhost",
                "port": 5432,
            }
        )
        if created:
            print(f"Created new DatabaseSource: {datasource}")
        else:
            print(f"Retrieved existing DatabaseSource: {datasource}")

        extractor = DatabaseSchemaExtractor(datasource)
        table_names = extractor.get_table_names_with_schema()
        tables_schemas = extractor.get_tables_schemas()
        VectorLoader(tables_schemas, datasource.name).load()
        return JsonResponse(data={"names": table_names}, safe=False)
    except asyncio.CancelledError:
        # Handle disconnect
        raise

