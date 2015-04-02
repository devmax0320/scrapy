import warnings
import unittest

from twisted.internet import defer

from scrapy.crawler import Crawler, CrawlerRunner
from scrapy.settings import Settings
from scrapy.utils.spider import DefaultSpider
from scrapy.utils.misc import load_object


class CrawlerTestCase(unittest.TestCase):

    def setUp(self):
        self.crawler = Crawler(DefaultSpider, Settings())

    def test_deprecated_attribute_spiders(self):
        with warnings.catch_warnings(record=True) as w:
            spiders = self.crawler.spiders
            self.assertEqual(len(w), 1)
            self.assertIn("Crawler.spiders", str(w[0].message))
            sm_cls = load_object(self.crawler.settings['SPIDER_MANAGER_CLASS'])
            self.assertIsInstance(spiders, sm_cls)

            self.crawler.spiders
            self.assertEqual(len(w), 1, "Warn deprecated access only once")

    def test_populate_spidercls_settings(self):
        spider_settings = {'TEST1': 'spider', 'TEST2': 'spider'}
        project_settings = {'TEST1': 'project', 'TEST3': 'project'}

        class CustomSettingsSpider(DefaultSpider):
            custom_settings = spider_settings

        settings = Settings()
        settings.setdict(project_settings, priority='project')
        crawler = Crawler(CustomSettingsSpider, settings)

        self.assertEqual(crawler.settings.get('TEST1'), 'spider')
        self.assertEqual(crawler.settings.get('TEST2'), 'spider')
        self.assertEqual(crawler.settings.get('TEST3'), 'project')

        self.assertFalse(settings.frozen)
        self.assertTrue(crawler.settings.frozen)
