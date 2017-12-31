import hashlib
import tempfile
import unittest
import shutil

from scrapy.dupefilters import RFPDupeFilter
from scrapy.http import Request
from scrapy.core.scheduler import Scheduler
from scrapy.utils.python import to_bytes
from scrapy.utils.job import job_dir
from scrapy.utils.test import get_crawler


class FromCrawlerRFPDupeFilter(RFPDupeFilter):

    @classmethod
    def from_crawler(cls, crawler):
        debug = crawler.settings.getbool('DUPEFILTER_DEBUG')
        df = cls(job_dir(crawler.settings), debug)
        df.method = crawler.settings.get('METHOD')
        return df


class FromSettingsRFPDupeFilter(RFPDupeFilter):

    @classmethod
    def from_settings(cls, settings):
        debug = settings.getbool('DUPEFILTER_DEBUG')
        df = cls(job_dir(settings), debug)
        df.method = settings.get('METHOD')
        return df


class RFPDupeFilterTest(unittest.TestCase):

    def test_from_crawler_scheduler(self):
        settings = {'DUPEFILTER_DEBUG': True, 'METHOD': 'from_crawler',
                    'DUPEFILTER_CLASS': __name__  + '.FromCrawlerRFPDupeFilter'}
        crawler = get_crawler(settings_dict=settings)
        scheduler = Scheduler.from_crawler(crawler)
        self.assertTrue(scheduler.df.debug)
        self.assertEqual(scheduler.df.method, 'from_crawler')

    def test_from_settings_scheduler(self):
        settings = {'DUPEFILTER_DEBUG': True, 'METHOD': 'from_settings',
                    'DUPEFILTER_CLASS': __name__  + '.FromSettingsRFPDupeFilter'}
        crawler = get_crawler(settings_dict=settings)
        scheduler = Scheduler.from_crawler(crawler)
        self.assertTrue(scheduler.df.debug)
        self.assertEqual(scheduler.df.method, 'from_settings')

    def test_filter(self):
        dupefilter = RFPDupeFilter()
        dupefilter.open()

        r1 = Request('http://scrapytest.org/1')
        r2 = Request('http://scrapytest.org/2')
        r3 = Request('http://scrapytest.org/2')

        assert not dupefilter.request_seen(r1)
        assert dupefilter.request_seen(r1)

        assert not dupefilter.request_seen(r2)
        assert dupefilter.request_seen(r3)

        dupefilter.close('finished')

    def test_dupefilter_path(self):
        r1 = Request('http://scrapytest.org/1')
        r2 = Request('http://scrapytest.org/2')

        path = tempfile.mkdtemp()
        try:
            df = RFPDupeFilter(path)
            df.open()
            assert not df.request_seen(r1)
            assert df.request_seen(r1)
            df.close('finished')

            df2 = RFPDupeFilter(path)
            df2.open()
            assert df2.request_seen(r1)
            assert not df2.request_seen(r2)
            assert df2.request_seen(r2)
            df2.close('finished')
        finally:
            shutil.rmtree(path)

    def test_request_fingerprint(self):
        """Test if customization of request_fingerprint method will change
        output of request_seen.

        """
        r1 = Request('http://scrapytest.org/index.html')
        r2 = Request('http://scrapytest.org/INDEX.html')

        dupefilter = RFPDupeFilter()
        dupefilter.open()

        assert not dupefilter.request_seen(r1)
        assert not dupefilter.request_seen(r2)

        dupefilter.close('finished')

        class CaseInsensitiveRFPDupeFilter(RFPDupeFilter):

            def request_fingerprint(self, request):
                fp = hashlib.sha1()
                fp.update(to_bytes(request.url.lower()))
                return fp.hexdigest()

        case_insensitive_dupefilter = CaseInsensitiveRFPDupeFilter()
        case_insensitive_dupefilter.open()

        assert not case_insensitive_dupefilter.request_seen(r1)
        assert case_insensitive_dupefilter.request_seen(r2)

        case_insensitive_dupefilter.close('finished')
