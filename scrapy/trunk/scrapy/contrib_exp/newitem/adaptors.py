from scrapy.utils.python import get_func_args


class ItemAdaptor(object):
    def __init__(self, response=None, item=None):
        if item:
            self.item_instance = item
        else:
            self.item_instance = self.item_class()

        self._response = response
        self._field_adaptors = self._get_field_adaptors()

    def _get_field_adaptors(self):
        fa = {}
        for field in self.item_instance._fields.keys():
            try:
                fa[field] = object.__getattribute__(self, field)
            except AttributeError:
                pass

        return fa

    def __setattr__(self, name, value):
        if name.startswith('_') or name == 'item_instance':
            return object.__setattr__(self, name, value)

        try:
            bounded_fa = self._field_adaptors[name]
            # unbound bounded field adaptor here because use of
            # @staticmethod decorator in class definition is not practical
            # for ItemAdaptor's
            fa = bounded_fa.__func__.__call__ 
        except KeyError:
            raise AttributeError(name)

        adaptor_args = {'response': self._response}
        ovalue = fa(value, adaptor_args=adaptor_args)
        setattr(self.item_instance, name, ovalue)

    def __getattribute__(self, name):
        if name.startswith('_') or name.startswith('item_'):
            return object.__getattribute__(self, name)

        return getattr(self.item_instance, name)


def adaptor(*funcs, **adaptor_args):
    """A pipe adaptor implementing the tree adaption logic
    
    It takes multiples unnamed arguments used as functions of the pipe, and
    keywords used as adaptor_args to be passed to functions that supports it

    If an adaptor function returns a list of values, each value is used as
    input for next adaptor function

    Always returns a list of values
    """

    pipe_adaptor_args = adaptor_args
    _funcs = []
    for func in funcs:
        takes_args = 'adaptor_args' in get_func_args(func)
        _funcs.append((func, takes_args))

    def _adaptor(value, adaptor_args=None):
        values = value if isinstance(value, (list, tuple)) else [value]
        aargs = dict(t for d in [pipe_adaptor_args, adaptor_args or {}] for t in d.iteritems())
        pipe_kwargs = { 'adaptor_args': aargs }

        for func, takes_args in _funcs:
            next = []
            kwargs = pipe_kwargs if takes_args else {}

            for val in values:
                val = func(val, **kwargs)

                if isinstance(val, (list, tuple)):
                    next.extend(val)
                elif val is not None:
                    next.append(val)

            values = next
        return list(values)

    return _adaptor


