import six
import unittest
try:
    from unittest import mock
except ImportError:
    import mock

from scrapy.settings import Settings, SettingsAttribute
from . import default_settings


class SettingsAttributeTest(unittest.TestCase):

    def setUp(self):
        self.attribute = SettingsAttribute('value', 10)

    def test_set_greater_priority(self):
        self.attribute.set('value2', 20)
        self.assertEqual(self.attribute.value, 'value2')
        self.assertEqual(self.attribute.priority, 20)

    def test_set_equal_priority(self):
        self.attribute.set('value2', 10)
        self.assertEqual(self.attribute.value, 'value2')
        self.assertEqual(self.attribute.priority, 10)

    def test_set_less_priority(self):
        self.attribute.set('value2', 0)
        self.assertEqual(self.attribute.value, 'value')
        self.assertEqual(self.attribute.priority, 10)


class SettingsTest(unittest.TestCase):

    def setUp(self):
        self.settings = Settings()

    @mock.patch.dict('scrapy.settings.SETTINGS_PRIORITIES', {'default': 10})
    @mock.patch('scrapy.settings.default_settings', default_settings)
    def test_initial_defaults(self):
        settings = Settings()
        self.assertEqual(len(settings.attributes), 1)
        self.assertIn('TEST_DEFAULT', settings.attributes)

        attr = settings.attributes['TEST_DEFAULT']
        self.assertIsInstance(attr, SettingsAttribute)
        self.assertEqual(attr.value, 'defvalue')
        self.assertEqual(attr.priority, 10)

    @mock.patch.dict('scrapy.settings.SETTINGS_PRIORITIES', {})
    @mock.patch('scrapy.settings.default_settings', {})
    def test_initial_values(self):
        settings = Settings({'TEST_OPTION': 'value'}, 10)
        self.assertEqual(len(settings.attributes), 1)
        self.assertIn('TEST_OPTION', settings.attributes)

        attr = settings.attributes['TEST_OPTION']
        self.assertIsInstance(attr, SettingsAttribute)
        self.assertEqual(attr.value, 'value')
        self.assertEqual(attr.priority, 10)

    def test_set_new_attribute(self):
        self.settings.attributes = {}
        self.settings.set('TEST_OPTION', 'value', 0)
        self.assertIn('TEST_OPTION', self.settings.attributes)

        attr = self.settings.attributes['TEST_OPTION']
        self.assertIsInstance(attr, SettingsAttribute)
        self.assertEqual(attr.value, 'value')
        self.assertEqual(attr.priority, 0)

    def test_set_instance_identity_on_update(self):
        attr = SettingsAttribute('value', 0)
        self.settings.attributes = {'TEST_OPTION': attr}
        self.settings.set('TEST_OPTION', 'othervalue', 10)

        self.assertIn('TEST_OPTION', self.settings.attributes)
        self.assertIs(attr, self.settings.attributes['TEST_OPTION'])

    def test_set_calls_settings_attributes_methods_on_update(self):
        with mock.patch.object(SettingsAttribute, '__setattr__') as mock_setattr, \
                mock.patch.object(SettingsAttribute, 'set') as mock_set:

            attr = SettingsAttribute('value', 10)
            self.settings.attributes = {'TEST_OPTION': attr}
            mock_set.reset_mock()
            mock_setattr.reset_mock()

            for priority in (0, 10, 20):
                self.settings.set('TEST_OPTION', 'othervalue', priority)
                mock_set.assert_called_once_with('othervalue', priority)
                self.assertFalse(mock_setattr.called)
                mock_set.reset_mock()
                mock_setattr.reset_mock()

    def test_setdict_alias(self):
        with mock.patch.object(self.settings, 'set') as mock_set:
            self.settings.setdict({'TEST_1': 'value1', 'TEST_2': 'value2'}, 10)
            self.assertEqual(mock_set.call_count, 2)
            calls = [mock.call('TEST_1', 'value1', 10),
                     mock.call('TEST_2', 'value2', 10)]
            mock_set.assert_has_calls(calls, any_order=True)

    def test_get(self):
        test_configuration = {
            'TEST_ENABLED1': '1',
            'TEST_ENABLED2': True,
            'TEST_ENABLED3': 1,
            'TEST_DISABLED1': '0',
            'TEST_DISABLED2': False,
            'TEST_DISABLED3': 0,
            'TEST_INT1': 123,
            'TEST_INT2': '123',
            'TEST_FLOAT1': 123.45,
            'TEST_FLOAT2': '123.45',
            'TEST_LIST1': ['one', 'two'],
            'TEST_LIST2': 'one,two',
            'TEST_STR': 'value',
            'TEST_DICT1': {'key1': 'val1', 'ke2': 3},
            'TEST_DICT2': '{"key1": "val1", "ke2": 3}',
        }
        settings = self.settings
        settings.attributes = {key: SettingsAttribute(value, 0) for key, value
                               in six.iteritems(test_configuration)}

        self.assertTrue(settings.getbool('TEST_ENABLED1'))
        self.assertTrue(settings.getbool('TEST_ENABLED2'))
        self.assertTrue(settings.getbool('TEST_ENABLED3'))
        self.assertFalse(settings.getbool('TEST_ENABLEDx'))
        self.assertTrue(settings.getbool('TEST_ENABLEDx', True))
        self.assertFalse(settings.getbool('TEST_DISABLED1'))
        self.assertFalse(settings.getbool('TEST_DISABLED2'))
        self.assertFalse(settings.getbool('TEST_DISABLED3'))
        self.assertEqual(settings.getint('TEST_INT1'), 123)
        self.assertEqual(settings.getint('TEST_INT2'), 123)
        self.assertEqual(settings.getint('TEST_INTx'), 0)
        self.assertEqual(settings.getint('TEST_INTx', 45), 45)
        self.assertEqual(settings.getfloat('TEST_FLOAT1'), 123.45)
        self.assertEqual(settings.getfloat('TEST_FLOAT2'), 123.45)
        self.assertEqual(settings.getfloat('TEST_FLOATx'), 0.0)
        self.assertEqual(settings.getfloat('TEST_FLOATx', 55.0), 55.0)
        self.assertEqual(settings.getlist('TEST_LIST1'), ['one', 'two'])
        self.assertEqual(settings.getlist('TEST_LIST2'), ['one', 'two'])
        self.assertEqual(settings.getlist('TEST_LISTx'), [])
        self.assertEqual(settings.getlist('TEST_LISTx', ['default']), ['default'])
        self.assertEqual(settings['TEST_STR'], 'value')
        self.assertEqual(settings.get('TEST_STR'), 'value')
        self.assertEqual(settings['TEST_STRx'], None)
        self.assertEqual(settings.get('TEST_STRx'), None)
        self.assertEqual(settings.get('TEST_STRx', 'default'), 'default')
        self.assertEqual(settings.getdict('TEST_DICT1'), {'key1': 'val1', 'ke2': 3})
        self.assertEqual(settings.getdict('TEST_DICT2'), {'key1': 'val1', 'ke2': 3})
        self.assertEqual(settings.getdict('TEST_DICT3'), {})
        self.assertEqual(settings.getdict('TEST_DICT3', {'key1': 5}), {'key1': 5})
        self.assertRaises(ValueError, settings.getdict, 'TEST_LIST1')


if __name__ == "__main__":
    unittest.main()

