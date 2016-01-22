from os.path import join

import pytest

from twisted.trial import unittest
from twisted.internet import defer

from scrapy.commands.shell import guess_scheme
from scrapy.utils.testsite import SiteTest
from scrapy.utils.testproc import ProcessTest

from tests import tests_datadir



class ShellTest(ProcessTest, SiteTest, unittest.TestCase):

    command = 'shell'

    @defer.inlineCallbacks
    def test_empty(self):
        _, out, _ = yield self.execute(['-c', 'item'])
        assert b'{}' in out

    @defer.inlineCallbacks
    def test_response_body(self):
        _, out, _ = yield self.execute([self.url('/text'), '-c', 'response.body'])
        assert b'Works' in out

    @defer.inlineCallbacks
    def test_response_type_text(self):
        _, out, _ = yield self.execute([self.url('/text'), '-c', 'type(response)'])
        assert b'TextResponse' in out

    @defer.inlineCallbacks
    def test_response_type_html(self):
        _, out, _ = yield self.execute([self.url('/html'), '-c', 'type(response)'])
        assert b'HtmlResponse' in out

    @defer.inlineCallbacks
    def test_response_selector_html(self):
        xpath = 'response.xpath("//p[@class=\'one\']/text()").extract()[0]'
        _, out, _ = yield self.execute([self.url('/html'), '-c', xpath])
        self.assertEqual(out.strip(), b'Works')

    @defer.inlineCallbacks
    def test_response_encoding_gb18030(self):
        _, out, _ = yield self.execute([self.url('/enc-gb18030'), '-c', 'response.encoding'])
        self.assertEqual(out.strip(), b'gb18030')

    @defer.inlineCallbacks
    def test_redirect(self):
        _, out, _ = yield self.execute([self.url('/redirect'), '-c', 'response.url'])
        assert out.strip().endswith(b'/redirected')

    @defer.inlineCallbacks
    def test_request_replace(self):
        url = self.url('/text')
        code = "fetch('{0}') or fetch(response.request.replace(method='POST'))"
        errcode, out, _ = yield self.execute(['-c', code.format(url)])
        self.assertEqual(errcode, 0, out)

    @defer.inlineCallbacks
    def test_local_file(self):
        filepath = join(tests_datadir, 'test_site/index.html')
        _, out, _ = yield self.execute([filepath, '-c', 'item'])
        assert b'{}' in out

    @defer.inlineCallbacks
    def test_local_nofile(self):
        filepath = 'file:///tests/sample_data/test_site/nothinghere.html'
        errcode, out, err = yield self.execute([filepath, '-c', 'item'],
                                       check_code=False)
        self.assertEqual(errcode, 1, out or err)
        self.assertIn(b'No such file or directory', err)

    @defer.inlineCallbacks
    def test_dns_failures(self):
        url = 'www.somedomainthatdoesntexi.st'
        errcode, out, err = yield self.execute([url, '-c', 'item'],
                                       check_code=False)
        self.assertEqual(errcode, 1, out or err)
        self.assertIn(b'DNS lookup failed', err)


@pytest.mark.parametrize("url, scheme", [
    ('/index',                              'file://'),
    ('/index.html',                         'file://'),
    ('./index.html',                        'file://'),
    ('../index.html',                       'file://'),
    ('../../index.html',                    'file://'),
    ('./data/index.html',                   'file://'),
    ('.hidden/data/index.html',             'file://'),
    ('/home/user/www/index.html',           'file://'),
    ('//home/user/www/index.html',          'file://'),
    ('file:///home/user/www/index.html',    'file://'),

    ('index.html',                          'http://'),
    ('example.com',                         'http://'),
    ('www.example.com',                     'http://'),
    ('www.example.com/index.html',          'http://'),
    ('http://example.com',                  'http://'),
    ('http://example.com/index.html',       'http://'),
    ('localhost',                           'http://'),
    ('localhost/index.html',                'http://'),

    # some corner cases (default to http://)
    ('/',                                   'http://'),
    ('.../test',                            'http://'),

    pytest.mark.xfail(
        (r'C:\absolute\path\to\a\file.html', 'file://'),
         reason = 'Windows filepath are not supported for scrapy shell'
    ),
])
def test_guess_scheme(url, scheme):
    guessed_url = guess_scheme(url)
    assert guessed_url.startswith(scheme), \
        'Wrong scheme guessed: for `%s` got `%s`, expected `%s...`' % (
            url, guessed_url, scheme)
