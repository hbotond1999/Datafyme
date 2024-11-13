from django.test import TestCase
from dotenv import load_dotenv

from reporter_agent.visualisation_agent.ai import RepType
from reporter_agent.visualisation_agent.ai.graph import create_graph
from reporter_agent.visualisation_agent.chart import ChartTypes


# Create your tests here.
class VizuAgentTests(TestCase):
    def setUp(self):
        load_dotenv()

    def test_agent(self):
        graph = create_graph()
        test_data = {"company": ["IBM", "Microsoft", "Google"], "income": [1000, 2000, 3000]}
        question = "Hogyan oszlott meg a cégek között az árbevétel?"
        result = graph.invoke({"preview_data": test_data, "question": question})

        self.assertEqual(result["representation_type"], RepType.CHART.value)
        self.assertIn(result["chart_type"], [ChartTypes.BAR.value, ChartTypes.PIE.value])

    def test_agent_pie(self):
        graph = create_graph()
        test_data = {"company": ["IBM", "Microsoft", "Google"], "income": [1000, 2000, 3000]}
        question = "Hogyan oszlott meg a cégek között az árbevétel? Kör digaram legyen!"
        result = graph.invoke({"preview_data": test_data, "question": question})

        self.assertEqual(result["representation_type"], RepType.CHART.value)
        self.assertEqual(result["chart_type"], ChartTypes.PIE.value)