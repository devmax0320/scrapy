import re
from scrapy.xpath.selector import XPathSelector, XPathSelectorList
from scrapy.utils.url import canonicalize_url
from scrapy.utils.misc import extract_regex
from scrapy.utils.python import flatten

def to_unicode(value):
    """
    Receives a list of strings, converts
    it to unicode, and returns a new list.

    Input: iterable with strings
    Output: list of unicodes
    """
    if hasattr(value, '__iter__'):
        return [ unicode(v) for v in value ]
    else:
        raise TypeError('to_unicode must receive an iterable.')

def clean_spaces(value):
    _clean_spaces_re = re.compile("\s+", re.U)
    return [ _clean_spaces_re.sub(' ', v) for v in value ]

def strip_list(value):
    return [ v.strip() for v in value ]

def drop_empty(value):
    return [ v for v in value if v ]

def canonicalize_urls(value):
    if hasattr(value, '__iter__'):
        return [canonicalize_url(url) for url in value]
    elif isinstance(value, basestring):
        return canonicalize_url(value)
    return ''

class Delist(object):
    """
    Input: iterable with strings
    Output: unicode
    """
    def __init__(self, delimiter=' '):
        self.delimiter = delimiter
    
    def __call__(self, value):
        return self.delimiter.join(value)

class Regex(object):
    """
    This adaptor must receive either a list of strings or an XPathSelector
    and return a new list with the matches of the given strings with the given regular
    expression (which is passed by a keyword argument, and is mandatory for this adaptor).

    Input: XPathSelector, XPathSelectorList, iterable
    Output: list of unicodes
    """
    def __init__(self, regex=r''):
        self.regex = regex

    def __call__(self, value):
        if self.regex:
            if isinstance(value, (XPathSelector, XPathSelectorList)):
                return value.re(self.regex)
            elif hasattr(value, '__iter__'):
                return flatten([extract_regex(self.regex, string, 'utf-8') for string in value])
        return value

