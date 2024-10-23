import dataclasses

from django.http import JsonResponse

from db_configurator.models import DatabaseSource
from dbloader.services.utils.db_schema.schema_extractor import DatabaseSchemaExtractor
from dbloader.services.vector_loader.loader import VectorLoader


# Create your views here.
def loader(request):
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
    docs = VectorLoader(tables_schemas, datasource.name).create_docs()
    database_relations = extractor.get_relations()
    return JsonResponse(data={"names": table_names, "docs": [doc.model_dump() for doc in docs],
                              "relations": [dataclasses.asdict(t) for t in database_relations]}, safe=False)
