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
        with open("C:\\Users\\Lenovo\\Desktop\\report-assistant\\chart_img_most_viewed_movies.png", "rb") as image_file:
            self.encoded_img = base64.b64encode(image_file.read())

    def test_create_description(self):
        result = create_description(chart_id=self.chart_id, chart_png=self.encoded_img)
        print(result)
