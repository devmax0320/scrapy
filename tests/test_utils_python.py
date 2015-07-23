import functools
import operator
import unittest
from itertools import count

from scrapy.utils.python import (
    memoizemethod_noargs, isbinarytext, equal_attributes,
    WeakKeyCache, stringify_dict, get_func_args, to_bytes, to_unicode)

__doctests__ = ['scrapy.utils.python']


class ToUnicodeTest(unittest.TestCase):
    def test_converting_an_utf8_encoded_string_to_unicode(self):
        self.assertEqual(to_unicode(b'lel\xc3\xb1e'), u'lel\xf1e')

    def test_converting_a_latin_1_encoded_string_to_unicode(self):
        self.assertEqual(to_unicode(b'lel\xf1e', 'latin-1'), u'lel\xf1e')

    def test_converting_a_unicode_to_unicode_should_return_the_same_object(self):
        self.assertEqual(to_unicode(u'\xf1e\xf1e\xf1e'), u'\xf1e\xf1e\xf1e')

    def test_converting_a_strange_object_should_raise_TypeError(self):
        self.assertRaises(TypeError, to_unicode, 423)

    def test_check_errors_argument_works(self):
        self.assertIn(u'\ufffd', to_unicode(b'a\xedb', 'utf-8', errors='replace'))


class ToBytesTest(unittest.TestCase):
    def test_converting_a_unicode_object_to_an_utf_8_encoded_string(self):
        self.assertEqual(to_bytes(u'\xa3 49'), b'\xc2\xa3 49')

    def test_converting_a_unicode_object_to_a_latin_1_encoded_string(self):
        self.assertEqual(to_bytes(u'\xa3 49', 'latin-1'), b'\xa3 49')

    def test_converting_a_regular_string_to_string_should_return_the_same_object(self):
        self.assertEqual(to_bytes(b'lel\xf1e'), b'lel\xf1e')

    def test_converting_a_strange_object_should_raise_TypeError(self):
        self.assertRaises(TypeError, to_bytes, unittest)

    def test_check_errors_argument_works(self):
        self.assertIn(b'?', to_bytes(u'a\ufffdb', 'latin-1', errors='replace'))


class UtilsPythonTestCase(unittest.TestCase):
    def test_memoizemethod_noargs(self):
        class A(object):

            @memoizemethod_noargs
            def cached(self):
                return object()

            def noncached(self):
                return object()

        a = A()
        one = a.cached()
        two = a.cached()
        three = a.noncached()
        assert one is two
        assert one is not three

    def test_isbinarytext(self):

        # basic tests
        assert not isbinarytext("hello")

        # utf-16 strings contain null bytes
        assert not isbinarytext(u"hello".encode('utf-16'))

        # one with encoding
        assert not isbinarytext("<div>Price \xa3</div>")

        # finally some real binary bytes
        assert isbinarytext("\x02\xa3")

    def test_equal_attributes(self):
        class Obj:
            pass

        a = Obj()
        b = Obj()
        # no attributes given return False
        self.failIf(equal_attributes(a, b, []))
        # not existent attributes
        self.failIf(equal_attributes(a, b, ['x', 'y']))

        a.x = 1
        b.x = 1
        # equal attribute
        self.assertTrue(equal_attributes(a, b, ['x']))

        b.y = 2
        # obj1 has no attribute y
        self.failIf(equal_attributes(a, b, ['x', 'y']))

        a.y = 2
        # equal attributes
        self.assertTrue(equal_attributes(a, b, ['x', 'y']))

        a.y = 1
        # differente attributes
        self.failIf(equal_attributes(a, b, ['x', 'y']))

        # test callable
        a.meta = {}
        b.meta = {}
        self.assertTrue(equal_attributes(a, b, ['meta']))

        # compare ['meta']['a']
        a.meta['z'] = 1
        b.meta['z'] = 1

        get_z = operator.itemgetter('z')
        get_meta = operator.attrgetter('meta')
        compare_z = lambda obj: get_z(get_meta(obj))

        self.assertTrue(equal_attributes(a, b, [compare_z, 'x']))
        # fail z equality
        a.meta['z'] = 2
        self.failIf(equal_attributes(a, b, [compare_z, 'x']))

    def test_weakkeycache(self):
        class _Weakme(object): pass
        _values = count()
        wk = WeakKeyCache(lambda k: next(_values))
        k = _Weakme()
        v = wk[k]
        self.assertEqual(v, wk[k])
        self.assertNotEqual(v, wk[_Weakme()])
        self.assertEqual(v, wk[k])
        del k
        self.assertFalse(len(wk._weakdict))

    def test_stringify_dict(self):
        d = {'a': 123, u'b': 'c', u'd': u'e', object(): u'e'}
        d2 = stringify_dict(d, keys_only=False)
        self.assertEqual(d, d2)
        self.failIf(d is d2) # shouldn't modify in place
        self.failIf(any(isinstance(x, unicode) for x in d2.keys()))
        self.failIf(any(isinstance(x, unicode) for x in d2.values()))

    def test_stringify_dict_tuples(self):
        tuples = [('a', 123), (u'b', 'c'), (u'd', u'e'), (object(), u'e')]
        d = dict(tuples)
        d2 = stringify_dict(tuples, keys_only=False)
        self.assertEqual(d, d2)
        self.failIf(d is d2) # shouldn't modify in place
        self.failIf(any(isinstance(x, unicode) for x in d2.keys()), d2.keys())
        self.failIf(any(isinstance(x, unicode) for x in d2.values()))

    def test_stringify_dict_keys_only(self):
        d = {'a': 123, u'b': 'c', u'd': u'e', object(): u'e'}
        d2 = stringify_dict(d)
        self.assertEqual(d, d2)
        self.failIf(d is d2) # shouldn't modify in place
        self.failIf(any(isinstance(x, unicode) for x in d2.keys()))

    def test_get_func_args(self):
        def f1(a, b, c):
            pass

        def f2(a, b=None, c=None):
            pass

        class A(object):
            def __init__(self, a, b, c):
                pass

            def method(self, a, b, c):
                pass

        class Callable(object):

            def __call__(self, a, b, c):
                pass

        a = A(1, 2, 3)
        cal = Callable()
        partial_f1 = functools.partial(f1, None)
        partial_f2 = functools.partial(f1, b=None)
        partial_f3 = functools.partial(partial_f2, None)

        self.assertEqual(get_func_args(f1), ['a', 'b', 'c'])
        self.assertEqual(get_func_args(f2), ['a', 'b', 'c'])
        self.assertEqual(get_func_args(A), ['a', 'b', 'c'])
        self.assertEqual(get_func_args(a.method), ['a', 'b', 'c'])
        self.assertEqual(get_func_args(partial_f1), ['b', 'c'])
        self.assertEqual(get_func_args(partial_f2), ['a', 'c'])
        self.assertEqual(get_func_args(partial_f3), ['c'])
        self.assertEqual(get_func_args(cal), ['a', 'b', 'c'])
        self.assertEqual(get_func_args(object), [])

        # TODO: how do we fix this to return the actual argument names?
        self.assertEqual(get_func_args(unicode.split), [])
        self.assertEqual(get_func_args(" ".join), [])
        self.assertEqual(get_func_args(operator.itemgetter(2)), [])

if __name__ == "__main__":
    unittest.main()
