import dataclasses

from django.http import JsonResponse, HttpResponse

from db_configurator.models import DatabaseSource
from dbloader.services.utils.db_schema.schema_extractor import DatabaseSchemaExtractor
from dbloader.services.vector_loader.loader import VectorLoader

from common.graph_db.graph_db import Neo4JInstance

from common.graph_db.graph_db import Neo4JInstance


# Create your views here.
# request handlers: request -> response

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


def create_relation_graph(request):
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
    database_relations = extractor.get_relations()

    relations = [dataclasses.asdict(t) for t in database_relations]
    if relations:
        table_foreign_pairs = []
        for relation in relations:
            if relation is not None:
                table_name = relation.get("table_name")
                foreign_table_name = relation.get("foreign_table_name")

                if table_name and foreign_table_name:
                    table_foreign_pairs.append({"table_name": table_name, "foreign_table_name": foreign_table_name})

    else:
        return HttpResponse("There's no relation in database")

    neo4j_instance = Neo4JInstance()

    try:
        for table_pair in table_foreign_pairs:
            neo4j_instance.create_relation(table_pair["table_name"], table_pair["foreign_table_name"])

        neo4j_instance.find_table_neighbours(table_foreign_pairs[0]["table_name"])
        return JsonResponse(status=201, data={'status': 'Success', 'message': "Graph created"})

    except:
        return JsonResponse(status=404, data={'status': 'Failed', 'message': "Graph creation failed"})

    finally:
        neo4j_instance.close()


def clear_relation_graph(request):
    neo4j_instance = Neo4JInstance()

    try:
        neo4j_instance.clear_graph_database()
        return JsonResponse(status=201, data={'status': 'Success', 'message': "Graph cleared"})
    except:
        return JsonResponse(status=404, data={'status': 'Failed', 'message': "Graph clear failed"})

    finally:
        neo4j_instance.close()


def get_neighbours(request):
    table = request.GET.get('table')

    if not table:
        return JsonResponse(status=400, data={'status': 'Failed', 'message': 'Table parameter is missing'})

    neo4j_instance = Neo4JInstance()

    try:
        neighbours = neo4j_instance.find_table_neighbours(table)
        return JsonResponse(data={"neighbours": neighbours}, safe=False)

    except:
        return JsonResponse(status=404, data={'status': 'Failed', 'message': "Finding neighbours failed"})

    finally:
        neo4j_instance.close()
