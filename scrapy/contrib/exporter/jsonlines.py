from scrapy.contrib.exporter import BaseItemExporter

try:
    import json
except ImportError:
    import simplejson as json

class JsonLinesItemExporter(BaseItemExporter):

    def __init__(self, file, *args, **kwargs):
        super(JsonLinesItemExporter, self).__init__()
        self.file = file
        self.encoder = json.JSONEncoder(*args, **kwargs)

    def export_item(self, item):
        itemdict = dict(self._get_serialized_fields(item))
        self.file.write(self.encoder.encode(itemdict) + '\n')
