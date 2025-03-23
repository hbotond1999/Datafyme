import base64

from django.core.management.base import BaseCommand
import unittest

from dotenv import load_dotenv

from reporter_agent.reporter.subgraph.visualisation_agent.chart_description.chart_description_agent import \
    create_description


class Command(BaseCommand):
    def handle(self, **options):
        suite = unittest.TestLoader().loadTestsFromTestCase(TestChartDescription)
        unittest.TextTestRunner().run(suite)


class TestChartDescription(unittest.TestCase):
    def setUp(self):
        load_dotenv()
        self.chart_id = 6
        self.chart_url = "C:\\Users\\Lenovo\\Desktop\\report-assistant\\chart_img_most_viewed_movies.png"

    def test_create_description(self):
        result = create_description(chart_id=self.chart_id, chart_path=self.chart_url, lang="hu")
        print(result)
