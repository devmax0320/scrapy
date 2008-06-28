"""
The ResponseLibxml2 extension causes the Response objects to grow a new method
("getlibxml2doc") which returns a (cached) libxml2 document of itself.
"""

from scrapy.http import Response
from scrapy.xpath.document import Libxml2Document
from scrapy.xpath.constructors import xmlDoc_from_html

class ResponseLibxml2(object):
    def __init__(self):
        setattr(Response, 'getlibxml2doc', getlibxml2doc)

def getlibxml2doc(response, constructor=xmlDoc_from_html):
    attr = '_lx2doc_%s' % constructor.__name__
    if not hasattr(response, attr):
        lx2doc = Libxml2Document(response, constructor=constructor)
        setattr(response, attr, lx2doc)
    return getattr(response, attr)

