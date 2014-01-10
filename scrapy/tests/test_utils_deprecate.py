# -*- coding: utf-8 -*-
from __future__ import absolute_import
import inspect
import unittest
import warnings
from scrapy.utils.deprecate import create_deprecated_class

class MyWarning(UserWarning):
    pass

class SomeBaseClass(object):
    pass

class NewName(SomeBaseClass):
    pass


class WarnWhenSubclassedTest(unittest.TestCase):

    def _mywarnings(self, w, category=MyWarning):
        return [x for x in w if x.category is MyWarning]

    def test_no_warning_on_definition(self):
        with warnings.catch_warnings(record=True) as w:
            Deprecated = create_deprecated_class('Deprecated', NewName)

        w = self._mywarnings(w)
        self.assertEqual(w, [])

    def test_subclassing_warning_message(self):
        Deprecated = create_deprecated_class('Deprecated', NewName,
                                             warn_category=MyWarning)

        with warnings.catch_warnings(record=True) as w:
            class UserClass(Deprecated):
                pass

        w = self._mywarnings(w)
        self.assertEqual(len(w), 1)
        self.assertEqual(
            str(w[0].message),
            "scrapy.tests.test_utils_deprecate.UserClass inherits from "
            "deprecated class scrapy.tests.test_utils_deprecate.Deprecated, "
            "please inherit from scrapy.tests.test_utils_deprecate.NewName."
            " (warning only on first subclass, there may be others)"
        )
        self.assertEqual(w[0].lineno, inspect.getsourcelines(UserClass)[1])

    def test_custom_class_paths(self):
        Deprecated = create_deprecated_class('Deprecated', NewName,
                                             new_class_path='foo.NewClass',
                                             old_class_path='bar.OldClass',
                                             warn_category=MyWarning)

        with warnings.catch_warnings(record=True) as w:
            class UserClass(Deprecated):
                pass

            _ = Deprecated()

        w = self._mywarnings(w)
        self.assertEqual(len(w), 2)
        self.assertIn('foo.NewClass', str(w[0].message))
        self.assertIn('bar.OldClass', str(w[0].message))
        self.assertIn('foo.NewClass', str(w[1].message))
        self.assertIn('bar.OldClass', str(w[1].message))

    def test_subclassing_warns_only_on_direct_childs(self):
        Deprecated = create_deprecated_class('Deprecated', NewName,
                                             warn_once=False,
                                             warn_category=MyWarning)

        with warnings.catch_warnings(record=True) as w:
            class UserClass(Deprecated):
                pass

            class NoWarnOnMe(UserClass):
                pass

        w = self._mywarnings(w)
        self.assertEqual(len(w), 1)
        self.assertIn('UserClass', str(w[0].message))

    def test_subclassing_warns_once_by_default(self):
        Deprecated = create_deprecated_class('Deprecated', NewName,
                                             warn_category=MyWarning)

        with warnings.catch_warnings(record=True) as w:
            class UserClass(Deprecated):
                pass

            class FooClass(Deprecated):
                pass

            class BarClass(Deprecated):
                pass

        w = self._mywarnings(w)
        self.assertEqual(len(w), 1)
        self.assertIn('UserClass', str(w[0].message))

    def test_warning_on_instance(self):
        Deprecated = create_deprecated_class('Deprecated', NewName,
                                             warn_category=MyWarning)

        # ignore subclassing warnings
        with warnings.catch_warnings(record=True):
            class UserClass(Deprecated):
                pass

        with warnings.catch_warnings(record=True) as w:
            # warns only once on instantations in the same lineno
            for _ in range(10):
                _, lineno = Deprecated(), inspect.getlineno(inspect.currentframe())
                _ = UserClass()  # subclass instances don't warn

        w = self._mywarnings(w)
        self.assertEqual(len(w), 1)
        self.assertEqual(
            str(w[0].message),
            "scrapy.tests.test_utils_deprecate.Deprecated is deprecated, "
            "instantiate scrapy.tests.test_utils_deprecate.NewName instead."
        )
        self.assertEqual(w[0].lineno, lineno)

    def test_warning_auto_message(self):
        with warnings.catch_warnings(record=True) as w:
            Deprecated = create_deprecated_class('Deprecated', NewName)

            class UserClass2(Deprecated):
                pass

        msg = str(w[0].message)
        self.assertIn("scrapy.tests.test_utils_deprecate.NewName", msg)
        self.assertIn("scrapy.tests.test_utils_deprecate.Deprecated", msg)

    def test_issubclass(self):
        with warnings.catch_warnings(record=True):
            DeprecatedName = create_deprecated_class('DeprecatedName', NewName)

            class UpdatedUserClass1(NewName):
                pass

            class UpdatedUserClass1a(NewName):
                pass

            class OutdatedUserClass1(DeprecatedName):
                pass

            class UnrelatedClass(object):
                pass

            class OldStyleClass:
                pass

        assert issubclass(UpdatedUserClass1, NewName)
        assert issubclass(UpdatedUserClass1a, NewName)
        assert issubclass(UpdatedUserClass1, DeprecatedName)
        assert issubclass(UpdatedUserClass1a, DeprecatedName)
        assert issubclass(OutdatedUserClass1, DeprecatedName)
        assert not issubclass(UnrelatedClass, DeprecatedName)
        assert not issubclass(OldStyleClass, DeprecatedName)
        assert not issubclass(OldStyleClass, DeprecatedName)

        self.assertRaises(TypeError, issubclass, object(), DeprecatedName)

    def test_isinstance(self):
        with warnings.catch_warnings(record=True):
            DeprecatedName = create_deprecated_class('DeprecatedName', NewName)

            class UpdatedUserClass2(NewName):
                pass

            class UpdatedUserClass2a(NewName):
                pass

            class OutdatedUserClass2(DeprecatedName):
                pass

            class UnrelatedClass(object):
                pass

            class OldStyleClass:
                pass

        assert isinstance(UpdatedUserClass2(), NewName)
        assert isinstance(UpdatedUserClass2a(), NewName)
        assert isinstance(UpdatedUserClass2(), DeprecatedName)
        assert isinstance(UpdatedUserClass2a(), DeprecatedName)
        assert isinstance(OutdatedUserClass2(), DeprecatedName)
        assert not isinstance(UnrelatedClass(), DeprecatedName)
        assert not isinstance(OldStyleClass(), DeprecatedName)

    def test_clsdict(self):
        with warnings.catch_warnings(record=True):
            Deprecated = create_deprecated_class('Deprecated', NewName, {'foo': 'bar'})

        self.assertEqual(Deprecated.foo, 'bar')

    def test_deprecate_a_class_with_custom_metaclass(self):
        Meta1 = type('Meta1', (type,), {})
        New = Meta1('New', (), {})
        Deprecated = create_deprecated_class('Deprecated', New)
