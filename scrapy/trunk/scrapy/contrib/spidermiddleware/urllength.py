from scrapy.core import log
from scrapy.http import Request
from scrapy.core.exceptions import NotConfigured
from scrapy.conf import settings

class UrlLengthMiddleware(object):
    """This middleware discard requests with URLs longer than URLLENGTH_LIMIT"""

    def __init__(self):
        self.maxlength = settings.getint('URLLENGTH_LIMIT')
        if not self.maxlength:
            raise NotConfigured

    def process_result(self, response, result, spider):
        def _filter(request):
            if isinstance(request, Request) and len(request.url) > self.maxlength:
                log.msg("Ignoring link (url length > %d): %s " % (self.maxlength, request.url), level=log.DEBUG, domain=spider.domain_name)
                return False
            else:
                return True

        return (r for r in result or () if _filter(r))
