"""Some debugging functions for working with the Scrapy engine"""

from time import time # used in global tests code

from scrapy.project import crawler

def get_engine_status(engine=None):
    """Return a report of the current engine status"""
    if engine is None:
        engine = crawler.engine

    global_tests = [
        "time()-engine.start_time",
        "engine.has_capacity()",
        "engine.scheduler.is_idle()",
        "len(engine.scheduler.pending_requests)",
        "engine.downloader.is_idle()",
        "len(engine.downloader.slots)",
        "len(engine.downloader.active)",
        "engine.scraper.is_idle()",
        "len(engine.scraper.slots)",
    ]
    spider_tests = [
        "engine.spider_is_idle(spider)",
        "engine.slots[spider].closing",
        "len(engine.slots[spider].inprogress)",
        "len(engine.scheduler.pending_requests[spider])",
        "len(engine.scraper.slots[spider].queue)",
        "len(engine.scraper.slots[spider].active)",
        "engine.scraper.slots[spider].active_size",
        "engine.scraper.slots[spider].itemproc_size",
        "engine.scraper.slots[spider].needs_backout()",
    ]

    status = {'global': [], 'spiders': {}}
    for test in global_tests:
        try:
            status['global'] += [(test, eval(test))]
        except Exception, e:
            status['global'] += [(test, "%s (exception)" % type(e).__name__)]
    for spider in engine.slots.keys():
        x = []
        for test in spider_tests:
            try:
                x += [(test, eval(test))]
            except Exception, e:
                x += [(test, "%s (exception)" % type(e).__name__)]
            status['spiders'][spider] = x
    return status

def format_engine_status(engine=None):
    status = get_engine_status(engine)
    s = "Execution engine status\n\n"
    for test, result in status['global']:
        s += "%-47s : %s\n" % (test, result)
    s += "\n"
    for spider, tests in status['spiders'].items():
        s += "Spider: %s\n" % spider
        for test, result in tests:
            s += "  %-50s : %s\n" % (test, result)
    return s

def print_engine_status(engine=None):
    print format_engine_status(engine)

