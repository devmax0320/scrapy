"""
Base class for Scrapy commands
"""

import os
import warnings
from optparse import OptionGroup
from twisted.python import failure

from scrapy.utils.conf import arglist_to_dict
from scrapy.exceptions import UsageError, ScrapyDeprecationWarning

class ScrapyCommand(object):

    requires_project = False
    crawler_process = None

    # default settings to be used for this command instead of global defaults
    default_settings = {}

    exitcode = 0

    def __init__(self):
        self.settings = None # set in scrapy.cmdline

    def set_crawler(self, crawler):
        assert not hasattr(self, '_crawler'), "crawler already set"
        self._crawler = crawler

    @property
    def crawler(self):
        warnings.warn("Command's default `crawler` is deprecated and will be removed. "
            "Use `create_crawler` method to instatiate crawlers.",
            ScrapyDeprecationWarning)

        if not hasattr(self, '_crawler'):
            crawler = self.crawler_process.create_crawler('default')

            old_start = crawler.start
            self.crawler_process.started = False
            def wrapped_start():
                if self.crawler_process.started:
                    old_start()
                else:
                    self.crawler_process.started = True
                    self.crawler_process.start()
            crawler.start = wrapped_start

            self.set_crawler(crawler)

        return self._crawler

    def syntax(self):
        """
        Command syntax (preferably one-line). Do not include command name.
        """
        return ""

    def short_desc(self):
        """
        A short description of the command
        """
        return ""

    def long_desc(self):
        """A long description of the command. Return short description when not
        available. It cannot contain newlines, since contents will be formatted
        by optparser which removes newlines and wraps text.
        """
        return self.short_desc()

    def help(self):
        """An extensive help for the command. It will be shown when using the
        "help" command. It can contain newlines, since not post-formatting will
        be applied to its contents.
        """
        return self.long_desc()

    def add_options(self, parser):
        """
        Populate option parse with options available for this command
        """
        group = OptionGroup(parser, "Global Options")
        group.add_option("--logfile", metavar="FILE", \
            help="log file. if omitted stderr will be used")
        group.add_option("-L", "--loglevel", metavar="LEVEL", \
            default=None, \
            help="log level (default: %s)" % self.settings['LOG_LEVEL'])
        group.add_option("--nolog", action="store_true", \
            help="disable logging completely")
        group.add_option("--profile", metavar="FILE", default=None, \
            help="write python cProfile stats to FILE")
        group.add_option("--lsprof", metavar="FILE", default=None, \
            help="write lsprof profiling stats to FILE")
        group.add_option("--pidfile", metavar="FILE", \
            help="write process ID to FILE")
        group.add_option("-s", "--set", action="append", default=[], metavar="NAME=VALUE", \
            help="set/override setting (may be repeated)")
        group.add_option("--pdb", action="store_true", help="enable pdb on failure")
        parser.add_option_group(group)

    def process_options(self, args, opts):
        try:
            self.settings.overrides.update(arglist_to_dict(opts.set))
        except ValueError:
            raise UsageError("Invalid -s value, use -s NAME=VALUE", print_help=False)

        if opts.logfile:
            self.settings.overrides['LOG_ENABLED'] = True
            self.settings.overrides['LOG_FILE'] = opts.logfile

        if opts.loglevel:
            self.settings.overrides['LOG_ENABLED'] = True
            self.settings.overrides['LOG_LEVEL'] = opts.loglevel

        if opts.nolog:
            self.settings.overrides['LOG_ENABLED'] = False

        if opts.pidfile:
            with open(opts.pidfile, "w") as f:
                f.write(str(os.getpid()) + os.linesep)

        if opts.pdb:
            failure.startDebugMode()

    def run(self, args, opts):
        """
        Entry point for running commands
        """
        raise NotImplementedError
