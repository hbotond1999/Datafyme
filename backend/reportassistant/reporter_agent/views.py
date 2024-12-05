from django.http import JsonResponse

from db_configurator.models import DatabaseSource
from reporter_agent.reporter.subgraph.sql_statement_creator.ai.graph import create_sql_agent_graph


# Create your views here.
def sql_agent(request):
    message = request.GET.get('message')
    database_id = request.GET.get('database_id')

    datasource = DatabaseSource.objects.get(id=database_id)

    sql_graph = create_sql_agent_graph()
    result = sql_graph.invoke({"message": message, "database_source": datasource})

    return JsonResponse(data={"sql_query": result["sql_query"], "query_description": result["query_description"]},
                        safe=False)
