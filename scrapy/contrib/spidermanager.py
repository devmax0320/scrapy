"""
SpiderManager is the class which locates and manages all website-specific
spiders
"""

import sys
import urlparse

from twisted.plugin import getCache
from twisted.python.rebuild import rebuild

from scrapy.spider.models import ISpider
from scrapy import log
from scrapy.conf import settings
from scrapy.utils.url import url_is_from_spider

class TwistedPluginSpiderManager(object):
    """Spider manager based in Twisted Plugin System"""

    def __init__(self):
        self.loaded = False
        self._spiders = {}

    def create(self, spider_id):
        """
        Returns Spider instance by given identifier.
        If not exists raises KeyError.
        """
        #@@@ currently spider_id = domain
        # if lookup fails let dict's KeyError exception propagate
        return self._spiders[spider_id]

    def find_by_request(self, request):
        """
        Returns list of spiders ids that match given Request.
        """
        # just find by request.url
        return [domain for domain, spider in self._spiders.iteritems()
                if url_is_from_spider(request.url, spider)]

    def list(self):
        """Returns list of spiders available."""
        return self._spiders.keys()

    def load(self, spider_modules=None):
        """Load spiders from module directory."""
        if spider_modules is None:
            spider_modules = settings.getlist('SPIDER_MODULES')
        self.spider_modules = spider_modules
        self._spiders = {}

        modules = [__import__(m, {}, {}, ['']) for m in self.spider_modules]
        for module in modules:
            for spider in self._getspiders(ISpider, module):
                ISpider.validateInvariants(spider)
                self._spiders[spider.domain_name] = spider
        self.loaded = True

    def _getspiders(self, interface, package):
        """This is an override of twisted.plugin.getPlugin, because we're
        interested in catching exceptions thrown when loading spiders such as
        KeyboardInterrupt
        """
        try:
            allDropins = getCache(package)
            for dropin in allDropins.itervalues():
                for plugin in dropin.plugins:
                    adapted = interface(plugin, None)
                    if adapted is not None:
                        yield adapted
        except KeyboardInterrupt:
            sys.stderr.write("Interrupted while loading Scrapy spiders\n")
            sys.exit(2)

    def close_spider(self, spider):
        """Reload spider module to release any resources held on to by the
        spider
        """
        domain = spider.domain_name
        if domain not in self._spiders:
            return
        spider = self._spiders[domain]
        module_name = spider.__module__
        module = sys.modules[module_name]
        if hasattr(module, 'SPIDER'):
            log.msg("Reloading module %s" % module_name, spider=spider, \
                level=log.DEBUG)
            new_module = rebuild(module, doLog=0)
            self._spiders[domain] = new_module.SPIDER
