import pandas as pd

from reporter_agent.models import Chart
from reporter_agent.reporter.subgraph.visualisation_agent.chart_description.agents import chart_description_agent
from reporter_agent.utils.chart_data import create_chart_meta_data


def create_description(chart_id, chart_png=None):
    chart = Chart.objects.get(id=chart_id)
    chart_data = create_chart_meta_data(chart)
    chart_df = pd.DataFrame.from_dict(chart_data)
    print(chart_df.describe(include='all'))
    result = chart_description_agent().invoke({"chart_png": chart_png, "summary": chart_df.describe(include='all')})

    return result
