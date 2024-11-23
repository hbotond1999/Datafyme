import asyncio
import dataclasses

from django.http import JsonResponse, HttpResponse

from db_configurator.models import DatabaseSource
from dbloader.services.utils.db_schema.schema_extractor import DatabaseSchemaExtractor
from dbloader.services.vector_loader.loader import VectorLoader
from dbloader.services.graph_loader.relation_finder import RelationFinder

from common.graph_db.graph_db import Neo4JInstance


# Create your views here.
# request handlers: request -> response

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

    extractor = DatabaseSchemaExtractor(datasource)
    table_names = extractor.get_table_names_with_schema()
    tables_schemas = extractor.get_tables_schemas()
    docs = VectorLoader(tables_schemas, datasource.name).create_docs()
    database_relations = extractor.get_relations()
    return JsonResponse(data={"names": table_names, "docs": [doc.model_dump() for doc in docs],
                              "relations": [dataclasses.asdict(t) for t in database_relations]}, safe=False)


def create_relation_graph(request):
    database_name = request.GET.get('database_name')
    datasource, _ = DatabaseSource.objects.get_or_create(name=database_name)

    extractor = DatabaseSchemaExtractor(datasource)
    database_relations = extractor.get_relations()

    defined_relations = [dataclasses.asdict(t) for t in database_relations]

    table_previews = extractor.get_table_previews()
    found_relations = RelationFinder(table_previews).find_relation()
    found_relations = [rel.model_dump() for rel in found_relations.relations]

    relations = defined_relations + found_relations
    if relations:
        table_foreign_pairs = []
        for relation in relations:
            if relation is not None:
                table_schema = relation.get("table_schema")
                table_name = relation.get("table_name")
                column_name = relation.get("column_name")
                foreign_table_schema = relation.get("foreign_table_schema")
                foreign_table_name = relation.get("foreign_table_name")
                foreign_column_name = relation.get("foreign_column_name")

                if table_name and foreign_table_name:
                    edge = {
                        "database_name": database_name + '_1',
                        "table_schema": table_schema,
                        "table_name": table_name,
                        "column_name": column_name,
                        "foreign_table_schema": foreign_table_schema,
                        "foreign_table_name": foreign_table_name,
                        "foreign_column_name": foreign_column_name
                    }

                    if edge not in table_foreign_pairs:
                        table_foreign_pairs.append(edge)

    else:
        return HttpResponse("There's no relation in database")

    neo4j_instance = Neo4JInstance()

    try:
        for table_pair in table_foreign_pairs:
            neo4j_instance.create_relation(table_pair["database_name"],
                                           table_pair["table_schema"],
                                           table_pair["table_name"],
                                           table_pair["column_name"],
                                           table_pair["foreign_table_schema"],
                                           table_pair["foreign_table_name"],
                                           table_pair["foreign_column_name"])

        return JsonResponse(status=201, data={'status': 'Success', 'message': "Graph created"})

    except:
        return JsonResponse(status=404, data={'status': 'Failed', 'message': "Graph creation failed"})

    finally:
        neo4j_instance.close()


def clear_relation_graph(request):
    database_name = request.GET.get('database_name')
    neo4j_instance = Neo4JInstance()

    try:
        neo4j_instance.clear_graph_database(database_name)
        return JsonResponse(status=201, data={'status': 'Success', 'message': f"Graph delete: {database_name}"})
    except:
        return JsonResponse(status=404, data={'status': 'Failed', 'message': f"Failed {database_name} graph delete"})

    finally:
        neo4j_instance.close()


def get_neighbours(request):
    table_name = request.GET.get('table_name')
    database_name = request.GET.get('database_name')

    if not table_name or not database_name:
        return JsonResponse(status=400, data={'status': 'Failed', 'message': 'Table or database parameter is missing'})

    neo4j_instance = Neo4JInstance()

    try:
        neighbours = neo4j_instance.find_table_neighbours(database_name, table_name)
        return JsonResponse(data={"neighbours": neighbours}, safe=False)

    except:
        return JsonResponse(status=404, data={'status': 'Failed', 'message': "Finding neighbours failed"})

    finally:
        neo4j_instance.close()
