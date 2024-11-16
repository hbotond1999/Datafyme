from django.test import TestCase
from dotenv import load_dotenv

from reporter_agent.visualisation_agent.ai import RepType
from reporter_agent.visualisation_agent.ai.graph import create_graph
from reporter_agent.visualisation_agent.chart import ChartTypes


# Create your tests here.
class VizuAgentTests(TestCase):
    def setUp(self):
        load_dotenv()
        self.graph = create_graph()

    def test_agent(self):
        test_data = {"company": ["IBM", "Microsoft", "Google"], "income": [1000, 2000, 3000]}
        question = "Hogyan oszlott meg a cégek között az árbevétel?"
        result = self.graph.invoke({"input_data": test_data, "question": question})
        final_data = result["final_data"]

        self.assertEqual(final_data.type, RepType.CHART)
        self.assertIn(final_data.chart_type, [ChartTypes.BAR, ChartTypes.PIE])

    def test_agent_pie(self):
        test_data = {"company": ["IBM", "Microsoft", "Google"], "income": [1000, 2000, 3000]}
        question = "Hogyan oszlott meg a cégek között az árbevétel? Kör digaram legyen!"
        result = self.graph.invoke({"input_data": test_data, "question": question})
        final_data = result["final_data"]
        self.assertEqual(final_data.type, RepType.CHART)
        self.assertEqual(final_data.chart_type, ChartTypes.PIE)

    def test_agent_bubble(self):
        question = "Hogyan viszonyulnak egymáshoz a különböző termékkategóriák az eladott mennyiség, az átlagos vásárlói elégedettség, és az egy termékből származó bevétel alapján?"
        test_data = {
                "company": ["IBM", "Microsoft", "Google", "Amazon", "Apple"],
                "income": [1000, 2000, 3000, 4000, 5000],
                "satisfaction": [7.5, 8.2, 9.1, 7.8, 8.5],
                "sales": [150, 300, 450, 200, 400]
        }

        result = self.graph.invoke({"input_data": test_data, "question": question})
        final_data = result["final_data"]
        self.assertEqual(final_data.type, RepType.CHART)
        self.assertEqual(final_data.chart_type, ChartTypes.BUBBLE)

    def test_agent_text_only(self):
        question = "Mennyi volt az árbevétel 2024-ben"
        test_data = {"income": [20232321]}
        result = self.graph.invoke({"input_data": test_data, "question": question})
        final_data = result["final_data"]
        self.assertEqual(final_data.type, RepType.TEXT)

    def test_agent_table(self):
        question = "Listázd ki a top 3 szállítót az árbevétel szerint!"
        test_data = {"company": ["IBM", "MICROSOFT", "SAP"], "income": [300, 200, 100]}
        result = self.graph.invoke({"input_data": test_data, "question": question})
        final_data = result["final_data"]
        self.assertEqual(final_data.type, RepType.TABLE)