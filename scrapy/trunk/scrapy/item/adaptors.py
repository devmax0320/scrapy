import re
from traceback import format_exc
from scrapy.core import log

class DuplicatedAdaptorName(Exception): pass

class Adaptor(object):
    """
    Adaptors instances should be instantiated and used only
    inside the AdaptorPipe.
    """
    def __init__(self, function, name, match_function):
        self.name = name
        self.basefunction = function
        self.match_function = match_function
    def function(self, value):
        return self.basefunction(value)
    def __repr__(self):
        return "'%s' Adaptor" %self.name
        
class AdaptorPipe:

    def __init__(self, attribute_names, adaptors=None, adaptorclass=None):
        """
        If "adaptors" is given, constructs pipeline from this.
        "adaptors" is an ordered tuple of 3-elements tuples, each of which
        has the same parameters you give to the insertadaptor method, except 
        'after' and 'before', because you define the adaptors order in the tuple.
        Example:
        (
          (my_function, "my_function", lambda x: x in my_list)
          ...
        )
        """
        self.__attribute_names = [ n for n in attribute_names ]
        self.__adaptorspipe = []
        self.__adaptorclass = adaptorclass or Adaptor
        self.pipes = {}
        if adaptors:
            for entry in adaptors:
                self.insertadaptor(compile_pipe=False, *entry)
            self._compile_pipe()

    @property
    def adaptors_names(self):
        _adaptors = []
        for a in self.__adaptorspipe:
            _adaptors.append(a.name)
        return _adaptors
    
    def insertadaptor(self, function, name, match_function=lambda x: True, after=None, before=None, compile_pipe=True):
        """
        Inserts a "function" as an adaptor that will apply when match_function returns True (by
        default always apply)
        If "after" is given, inserts the adaptor after the already inserted adaptor
        of the name given in this parameter, If "before" is given, inserts it before
        the adaptor of the given name. "name" is the name of the adaptor.
        """
        if name in self.adaptors_names:
            raise DuplicatedAdaptorName(name)
        else:
            adaptor = self.__adaptorclass(function, name, match_function)
            #by default append adaptor at end of pipe
            pos = len(self.adaptors_names)
            if after:
                pos = self.adaptors_names.index(after) + 1
            elif before:
                pos = self.adaptors_names.index(before)
            self.__adaptorspipe.insert(pos, adaptor)
            if compile_pipe:
                self._compile_pipe()
            return pos

    def removeadaptor(self, adaptorname):
        pos = self.adaptors_names.index(adaptorname)
        self.__adaptorspipe.pop(pos)
        self._compile_pipe()

    def _compile_pipe(self):
        for attrname in self.__attribute_names:
            adaptors_pipe = []
            for adaptor in self.__adaptorspipe:
                if adaptor.match_function(attrname):
                    adaptors_pipe.append(adaptor)
            self.pipes[attrname] = adaptors_pipe
            
    def execute(self, attrname, value, debug=False):
        """
        Execute pipeline for attribute name "attrname" and value "value".
        """
        for adaptor in self.pipes.get(attrname, []):
            try:
                if debug:
                    print "  %07s | input >" % adaptor.name, repr(value)
                value = adaptor.function(value)
                if debug:
                    print "  %07s | output>" % adaptor.name, repr(value)

            except Exception, e:
                print "Error in '%s' adaptor. Traceback text:" % adaptor.name
                print format_exc()
                return

        return value
