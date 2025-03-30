import base64

import pandas as pd
from langchain_core.messages import HumanMessage

from common.ai.model import get_llm_model
from reporter_agent.models import Chart
from reporter_agent.reporter.subgraph.visualisation_agent.chart_description.response import ChartDescription
from reporter_agent.reporter.utils import png_to_base64
from reporter_agent.utils.chart_data import create_chart_meta_data


def create_description(chart_id, chart_path, lang):
    chart = Chart.objects.get(id=chart_id)
    chart_data = create_chart_meta_data(chart)
    chart_df = pd.DataFrame.from_dict(chart_data)

    content = [
        {"type": "text", "text": "Your task is to analyze and provide a description of the following figure in this language: " + lang + "." + f"""
             You can additionally use the chart's data source summary for a more precise description: { chart_df.describe(include='all')}
        """
        },
    ]

    if chart_path:
        content.append({"type": "image_url", "image_url": {"url": "data:image/png;base64," + png_to_base64(chart_path)}})

    message = HumanMessage(content=content)

    result = get_llm_model().with_structured_output(ChartDescription).invoke([message])

    chart.description = result.description
    chart.save()

    return result
