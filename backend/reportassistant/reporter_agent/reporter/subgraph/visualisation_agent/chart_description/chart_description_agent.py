import pandas as pd
from langchain_core.messages import HumanMessage

from reporter_agent.models import Chart
from reporter_agent.reporter.subgraph.visualisation_agent.chart_description.agents import chart_description_agent
from reporter_agent.utils.chart_data import create_chart_meta_data


def create_description(chart_id, chart_url):
    chart = Chart.objects.get(id=chart_id)
    chart_data = create_chart_meta_data(chart)
    chart_df = pd.DataFrame.from_dict(chart_data)
    content = [
        {"type": "text", "text": "Your task is to provide a description of the following figure."},
    ]

    if chart_url:
        content.append({"type": "image_url", "image_url": {"url": chart_url}})

    message = HumanMessage(content=content)

    result = chart_description_agent().invoke({"message": message, "summary": chart_df.describe(include='all')})

    chart.description = result.description
    chart.save()

    return result

