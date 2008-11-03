"""
This module provides some LinkExtractors, which extend that base LinkExtractor
(scrapy.link.LinkExtractor) with some useful features.

"""

import re

from scrapy.link import LinkExtractor
from scrapy.utils.url import canonicalize_url, url_is_from_any_domain
from scrapy.utils.response import new_response_from_xpaths
from scrapy.utils.misc import dict_updatedefault

_re_type = type(re.compile("", 0))

_matches = lambda url, regexs: any((r.search(url) for r in regexs))
_is_valid_url = lambda url: url.split('://', 1)[0] in set(['http', 'https', 'file'])

class RegexLinkExtractor(LinkExtractor):
    """RegexLinkExtractor implements extends the base LinkExtractor by
    providing several mechanisms to extract the links.

    It's constructor parameters are:

    allow - list of regexes that the (absolute urls) must match to be extracted
    deny - ignore urls that match any of these regexes
    allow_domains - only extract urls from these domains
    deny_domains - ignore urls from these dmoains
    tags - look for urls in this tags
    attrs - look for urls in this attrs
    canonicalize - canonicalize all extracted urls using scrapy.utils.url.canonicalize_url

    Both 'allow' and 'deny' arguments can be a list of regexes strings or regex
    python objects (already compiled)

    Url matching is always performed against the absolute urls, never the
    relative urls found in pages.

    """
    
    def __init__(self, allow=(), deny=(), allow_domains=(), deny_domains=(), restrict_xpaths=(), 
                 tags=('a', 'area'), attrs=('href'), canonicalize=True):
        self.allow_res = [x if isinstance(x, _re_type) else re.compile(x) for x in allow]
        self.deny_res = [x if isinstance(x, _re_type) else re.compile(x) for x in deny]
        self.allow_domains = set(allow_domains)
        self.deny_domains = set(deny_domains)
        self.restrict_xpaths = restrict_xpaths
        self.canonicalize = canonicalize
        tag_func = lambda x: x in tags
        attr_func = lambda x: x in attrs
        LinkExtractor.__init__(self, tag=tag_func, attr=attr_func)

    def extract_urls(self, response, unique=True):
        if self.restrict_xpaths:
            response = new_response_from_xpaths(response, self.restrict_xpaths)

        links = LinkExtractor.extract_urls(self, response, unique)
        links = [link for link in links if _is_valid_url(link.url)]

        if self.allow_res:
            links = [link for link in links if _matches(link.url, self.allow_res)]
        if self.deny_res:
            links = [link for link in links if not _matches(link.url, self.deny_res)]
        if self.allow_domains:
            links = [link for link in links if url_is_from_any_domain(link.url, self.allow_domains)]
        if self.deny_domains:
            links = [link for link in links if not url_is_from_any_domain(link.url, self.deny_domains)]
        
        if self.canonicalize:
            for link in links:
                link.url = canonicalize_url(link.url)

        return links

    def match(self, url):
        return any(regex.search(url) for regex in self.allow_res) and not any(regex.search(url) for regex in self.deny_res)
