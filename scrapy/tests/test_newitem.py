import datetime
import decimal
import unittest

from scrapy.contrib_exp.newitem import Item, fields
from scrapy.contrib_exp.newitem.fields import BaseField


class NewItemTest(unittest.TestCase):

    def test_simple(self):
        class TestItem(Item):
            name = fields.TextField()

        i = TestItem()
        i.name = u'name'
        self.assertEqual(i.name, u'name')

    def test_init(self):
        class TestItem(Item):
            name = fields.TextField()
        
        i = TestItem()
        self.assert_(i.name is None)

        i2 = TestItem({'name': u'john doe'})
        self.assertEqual(i2.name, u'john doe')

        self.assertRaises(TypeError, TestItem, name=u'john doe')

        self.assertRaises(AttributeError, TestItem, {'name': u'john doe',
                                                     'other': u'foo'})

    def test_multi(self):
        class TestMultiItem(Item):
            name = fields.TextField()
            names = fields.MultiValuedField(fields.TextField)

        i = TestMultiItem()
        i.name = u'name'
        i.names = [u'name1', u'name2']
        self.assertEqual(i.names, [u'name1', u'name2'])

    def test_invalid_field(self):
        class TestItem(Item):
            pass

        i = TestItem()

        self.assertRaises(AttributeError, setattr, i, 'field', 'text')

        self.assertRaises(AttributeError, getattr, i, 'field')

    def test_default_value(self):
        class TestItem(Item):
            name = fields.TextField(default=u'John')
 
        i = TestItem()
        self.assertEqual(i.name, u'John')

    def test_wrong_default(self):
        def set_wrong_default():
            class TestItem(Item):
                name = fields.TextField(default=3)
        
        self.assertRaises(TypeError, set_wrong_default)

    def test_to_python_iter(self):
        class TestItem(Item):
            name = fields.TextField()
 
        i = TestItem()
        i.name = (u'John', u'Doe')
        self.assertEqual(i.name, u'John Doe')

    def test_repr(self):
        class TestItem(Item):
            name = fields.TextField()
            number = fields.IntegerField()

        i = TestItem()
        i.name = u'John Doe'
        i.number = '123'
        itemrepr = repr(i)
        self.assertEqual(itemrepr,
                         "TestItem({'name': u'John Doe', 'number': 123})")

        i2 = eval(itemrepr)
        self.assertEqual(i2.name, 'John Doe')
        self.assertEqual(i2.number, 123)

    def test_private_attr(self):
        class TestItem(Item):
            name = fields.TextField()

        i = TestItem()
        i._private = 'test'
        self.assertEqual(i._private, 'test')

    def test_custom_methods(self):
        class TestItem(Item):
            name = fields.TextField()

            def get_name(self):
                return self.name

            def change_name(self, name):
                self.name = name

        i = TestItem()
        self.assertEqual(i.get_name(), None)
        i.name = u'lala'
        self.assertEqual(i.get_name(), u'lala')
        i.change_name(u'other')
        self.assertEqual(i.get_name(), 'other')


class NewItemFieldsTest(unittest.TestCase):
    
    def test_base_field(self):
        f = fields.BaseField()

        self.assert_(f.get_default() is None)
        self.assertRaises(NotImplementedError, f.to_python, 1)

    def test_boolean_field(self):
        class TestItem(Item):
            field = fields.BooleanField()

        i = TestItem()

        i.field = True
        self.assert_(i.field is True)
    
        i.field = 1
        self.assert_(i.field is True)

        i.field = False
        self.assert_(i.field is False)

        i.field = 0
        self.assert_(i.field is False)

        i.field = None
        self.assert_(i.field is False)

    def test_date_field(self):
        class TestItem(Item):
            field = fields.DateField()

        i = TestItem()

        d_today = datetime.date.today()
        i.field = d_today
        self.assertEqual(i.field, d_today)

        dt_today = datetime.datetime.today()
        i.field = dt_today
        self.assertEqual(i.field, dt_today.date())
 
        i.field = '2009-05-21'
        self.assertEqual(i.field, datetime.date(2009, 5, 21))

        self.assertRaises(ValueError, setattr, i, 'field', '21-05-2009')

        self.assertRaises(ValueError, setattr, i, 'field', '2009-05-51')

        self.assertRaises(TypeError, setattr, i, 'field', None)

    def test_datetime_field(self):
        class TestItem(Item):
            field = fields.DateTimeField()

        i = TestItem()

        dt_today = datetime.datetime.today()
        i.field = dt_today
        self.assertEqual(i.field, dt_today)

        d_today = datetime.date.today()
        i.field = d_today
        self.assertEqual(i.field, datetime.datetime(d_today.year,
                                                    d_today.month, d_today.day))

        i.field = '2009-05-21 11:08:10.100'
        self.assertEqual(i.field, datetime.datetime(2009, 5, 21, 11, 8, 10,
                                                    100))
 
        i.field = '2009-05-21 11:08:10'
        self.assertEqual(i.field, datetime.datetime(2009, 5, 21, 11, 8, 10))

        i.field = '2009-05-21 11:08'
        self.assertEqual(i.field, datetime.datetime(2009, 5, 21, 11, 8))

        i.field = '2009-05-21'
        self.assertEqual(i.field, datetime.datetime(2009, 5, 21))

        self.assertRaises(ValueError, setattr, i, 'field', '2009-05-21 11:08:10.usecs')

        self.assertRaises(ValueError, setattr, i, 'field', '21-05-2009')

        self.assertRaises(ValueError, setattr, i, 'field', '2009-05-51')

        self.assertRaises(TypeError, setattr, i, 'field', None)

    def test_decimal_field(self):
        class TestItem(Item):
            field = fields.DecimalField()

        i = TestItem()

        i.field = decimal.Decimal('3.14')
        self.assertEqual(i.field, decimal.Decimal('3.14'))

        i.field = '3.14'
        self.assertEqual(i.field, decimal.Decimal('3.14'))
        
        self.assertRaises(decimal.InvalidOperation, setattr, i, 'field', 'text')

        self.assertRaises(TypeError, setattr, i, 'field', None)

    def test_float_field(self):
        class TestItem(Item):
            field = fields.FloatField()

        i = TestItem()

        i.field = 3.14
        self.assertEqual(i.field, 3.14)

        i.field = '3.14'
        self.assertEqual(i.field, 3.14)
        
        self.assertRaises(ValueError, setattr, i, 'field', 'text')

        self.assertRaises(TypeError, setattr, i, 'field', None)

    def test_integer_field(self):
        class TestItem(Item):
            field = fields.IntegerField()

        i = TestItem()

        i.field = 3
        self.assertEqual(i.field, 3)

        i.field = '3'
        self.assertEqual(i.field, 3)

        self.assertRaises(ValueError, setattr, i, 'field', 'text')

        self.assertRaises(TypeError, setattr, i, 'field', None)

    def test_text_field(self):
        class TestItem(Item):
            field = fields.TextField()

        i = TestItem()

        i.field = u'hello'
        self.assertEqual(i.field, u'hello')
        self.assert_(isinstance(i.field, unicode))

        # must be unicode!
        self.assertRaises(TypeError, setattr, i, 'field', 'string')

        self.assertRaises(TypeError, setattr, i, 'field', None)

        def set_invalid_value():
            i.field = 3 

        self.assertRaises(TypeError, set_invalid_value)

        i = TestItem()
        i.field = [u'hello', u'world']
        self.assertEqual(i.field, u'hello world')
        self.assert_(isinstance(i.field, unicode))

        self.assertRaises(TypeError, setattr, i, 'field', [u'hello', 3, u'world']) 
        self.assertRaises(TypeError, setattr, i, 'field', [u'hello', 'world']) 

        i = TestItem()
        i.field = []
        self.assert_(isinstance(i.field, unicode))
        self.assertEqual(i.field, '')

    def test_time_field(self):
        class TestItem(Item):
            field = fields.TimeField()

        i = TestItem()

        dt_t = datetime.time(11, 8, 10, 100)
        i.field = dt_t
        self.assertEqual(i.field, dt_t)

        self.assertRaises(TypeError, setattr, i, 'field', None)

        dt_dt = datetime.datetime.today()
        i.field = dt_dt
        self.assertEqual(i.field, dt_dt.time)

        i.field = '11:08:10.100'
        self.assertEqual(i.field, datetime.time(11, 8, 10, 100))
 
        i.field = '11:08:10'
        self.assertEqual(i.field, datetime.time(11, 8, 10))

        i.field = '11:08'
        self.assertEqual(i.field, datetime.time(11, 8))

        self.assertRaises(ValueError, setattr, i, 'field', '11:08:10.usecs')

        self.assertRaises(ValueError, setattr, i, 'field', '25:08:10')

        self.assertRaises(ValueError, setattr, i, 'field', 'string')

