from django.http import JsonResponse

from reporter_agent.sql_statement_creator.ai.graph import create_sql_agent_graph


# Create your views here.
def sql_agent(request):
    message = request.GET.get('message')

    sql_graph = create_sql_agent_graph()
    result = sql_graph.invoke({"message": message})

    return JsonResponse(data={"result": result}, safe=False)
