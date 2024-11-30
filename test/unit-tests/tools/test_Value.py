import unittest
from idataframe.tools import Value, value_fn


class TestInit(unittest.TestCase):

    def setUp(self):
        self.a = Value(42)
        self.b = Value(42, 'asdf')
        self.c = Value(42, ['asdf1', 'asdf2', 'asdf3'])

    def test_items(self):
        self.assertIs(self.a.items[0], self.a.value)
        self.assertIs(self.a.items[1], self.a.messages)
        self.assertIs(self.b.items[0], self.b.value)
        self.assertIs(self.b.items[1], self.b.messages)
        self.assertIs(self.c.items[0], self.c.value)
        self.assertIs(self.c.items[1], self.c.messages)

        def override_items():
            self.a.items = (42, ['adsf'])
        self.assertRaises(PermissionError, override_items)

    def test_value(self):
        self.assertEqual(self.a.value, 42)
        self.assertEqual(self.b.value, 42)
        self.assertEqual(self.c.value, 42)

        def override_value():
            self.a.value = 42
        self.assertRaises(PermissionError, override_value)

    def test_messages(self):
        self.assertEqual(self.a.messages, [])
        self.assertEqual(self.a.message, '')
        self.assertEqual(self.b.messages, ['asdf'])
        self.assertEqual(self.b.message, 'asdf')
        self.assertEqual(self.c.messages, ['asdf1', 'asdf2', 'asdf3'])
        self.assertEqual(self.c.message, 'asdf1 | asdf2 | asdf3')

        def override_msg():
            self.a.message = 'asdf'
        self.assertRaises(PermissionError, override_msg)

        def override_msgs():
            self.a.messages = ['asdf']
        self.assertRaises(PermissionError, override_msgs)

    def test_binding(self):
        # no 'value_fn' decorator
        def double_error(value: int) -> int:
            return 2*value
        self.assertRaises(Exception, self.a.bind(double_error))

        @value_fn
        def double_correct(value: int) -> int:
            return 2*value
        self.assertEqual(self.a.bind(double_correct).value, 2*42)

    def test_prefix(self):
        self.assertEqual(self.a.prefix_messages('prefix_').messages, [])
        self.assertEqual(Value(None, '').prefix_messages('prefix_').messages,
                                                                         [''])
        self.assertEqual(self.b.prefix_messages('prefix_').messages,
                         Value(self.b.value, 'prefix_asdf').messages)
        self.assertEqual(self.c.prefix_messages('prefix_').messages,
                         Value(self.b.value, ['prefix_asdf1', 'prefix_asdf2',
                                              'prefix_asdf3']).messages)

    def test_suffix(self):
        self.assertEqual(self.a.suffix_messages('_suffix').messages, [])
        self.assertEqual(Value(None, '').suffix_messages('_suffix').messages,
                                                                         [''])
        self.assertEqual(self.b.suffix_messages('_suffix').messages,
                         Value(self.b.value, 'asdf_suffix').messages)
        self.assertEqual(self.c.suffix_messages('_suffix').messages,
                         Value(self.b.value, ['asdf1_suffix', 'asdf2_suffix',
                                              'asdf3_suffix']).messages)

    def test_str(self):
        self.assertEqual(str(self.a), '42')
        self.assertEqual(str(self.b), '42')
        self.assertEqual(str(self.c), '42')

    def test_int(self):
        self.assertEqual(int(self.a), 42)
        self.assertEqual(int(self.b), 42)
        self.assertEqual(int(self.c), 42)

    def test_float(self):
        self.assertEqual(float(self.a), 42.0)
        self.assertEqual(float(self.b), 42.0)
        self.assertEqual(float(self.c), 42.0)

    def test_add(self):
        self.assertEqual((self.a + Value(2)).value, 42+2)
        self.assertEqual((self.b + Value(2.3)).value, 42+2.3)
        self.assertEqual((self.c + Value(3)).value, 42+3)
        self.assertEqual((self.b + self.c).messages,
                    Value(None, self.b.messages + self.c.messages).messages)
        self.assertEqual((self.c + self.c).messages, self.c.messages)
        self.assertEqual((self.a + 2).value, 42+2)
        self.assertEqual((self.b + 2.3).value, 42+2.3)
        self.assertEqual((self.c + 3).value, 42+3)
        self.assertEqual((self.c + 3).messages, self.c.messages)

    def test_sub(self):
        self.assertEqual((self.a - Value(2)).value, 42-2)
        self.assertEqual((self.b - Value(2.3)).value, 42-2.3)
        self.assertEqual((self.c - Value(3)).value, 42-3)
        self.assertEqual((self.b - self.c).messages,
                    Value(None, self.b.messages + self.c.messages).messages)
        self.assertEqual((self.c - self.c).messages, self.c.messages)
        self.assertEqual((self.a - 2).value, 42-2)
        self.assertEqual((self.b - 2.3).value, 42-2.3)
        self.assertEqual((self.c - 3).value, 42-3)
        self.assertEqual((self.c - 3).messages, self.c.messages)

    def test_mul(self):
        self.assertEqual((self.a * Value(2)).value, 42*2)
        self.assertEqual((self.b * Value(2.3)).value, 42*2.3)
        self.assertEqual((self.c * Value(3)).value, 42*3)
        self.assertEqual((self.b * self.c).messages,
                    Value(None, self.b.messages + self.c.messages).messages)
        self.assertEqual((self.c * self.c).messages, self.c.messages)
        self.assertEqual((self.a * 2).value, 42*2)
        self.assertEqual((self.b * 2.3).value, 42*2.3)
        self.assertEqual((self.c * 3).value, 42*3)
        self.assertEqual((self.c * 3).messages, self.c.messages)

    def test_truediv(self):
        self.assertEqual((self.a / Value(2)).value, 42/2)
        self.assertEqual((self.b / Value(2.3)).value, 42/2.3)
        self.assertEqual((self.c / Value(3)).value, 42/3)
        self.assertEqual((self.b / self.c).messages,
                    Value(None, self.b.messages + self.c.messages).messages)
        self.assertEqual((self.c / self.c).messages, self.c.messages)
        self.assertEqual((self.a / 2).value, 42/2)
        self.assertEqual((self.b / 2.3).value, 42/2.3)
        self.assertEqual((self.c / 3).value, 42/3)
        self.assertEqual((self.c / 3).messages, self.c.messages)

    def test_floordiv(self):
        self.assertEqual((self.a // Value(2)).value, 42//2)
        self.assertEqual((self.b // Value(2.3)).value, 42//2.3)
        self.assertEqual((self.c // Value(3)).value, 42//3)
        self.assertEqual((self.b // self.c).messages,
                    Value(None, self.b.messages + self.c.messages).messages)
        self.assertEqual((self.c // self.c).messages, self.c.messages)
        self.assertEqual((self.a // 2).value, 42//2)
        self.assertEqual((self.b // 2.3).value, 42//2.3)
        self.assertEqual((self.c // 3).value, 42//3)
        self.assertEqual((self.c // 3).messages, self.c.messages)

    def test_pow(self):
        self.assertEqual((self.a ** Value(2)).value, 42**2)
        self.assertEqual((self.b ** Value(2.3)).value, 42**2.3)
        self.assertEqual((self.c ** Value(3)).value, 42**3)
        self.assertEqual((self.b ** self.c).messages,
                    Value(None, self.b.messages + self.c.messages).messages)
        self.assertEqual((self.c ** self.c).messages, self.c.messages)
        self.assertEqual((self.a ** 2).value, 42**2)
        self.assertEqual((self.b ** 2.3).value, 42**2.3)
        self.assertEqual((self.c ** 3).value, 42**3)
        self.assertEqual((self.c ** 3).messages, self.c.messages)

    def test_mod(self):
        self.assertEqual((self.a % Value(2)).value, 42%2)
        self.assertEqual((self.b % Value(2.3)).value, 42%2.3)
        self.assertEqual((self.c % Value(3)).value, 42%3)
        self.assertEqual((self.b % self.c).messages,
                    Value(None, self.b.messages + self.c.messages).messages)
        self.assertEqual((self.c % self.c).messages, self.c.messages)
        self.assertEqual((self.a % 2).value, 42%2)
        self.assertEqual((self.b % 2.3).value, 42%2.3)
        self.assertEqual((self.c % 3).value, 42%3)
        self.assertEqual((self.c % 3).messages, self.c.messages)

    def test_divmod(self):
        self.assertEqual(divmod(self.a, Value(2)).value, divmod(42, 2))
        self.assertEqual(divmod(self.b, Value(2.3)).value, divmod(42, 2.3))
        self.assertEqual(divmod(self.c, Value(3)).value, divmod(42, 3))
        self.assertEqual(divmod(self.b, self.c).messages,
                    Value(None, self.b.messages + self.c.messages).messages)
        self.assertEqual(divmod(self.c, self.c).messages, self.c.messages)
        self.assertEqual(divmod(self.a, 2).value, divmod(42, 2))
        self.assertEqual(divmod(self.b, 2.3).value, divmod(42, 2.3))
        self.assertEqual(divmod(self.c, 3).value, divmod(42, 3))
        self.assertEqual(divmod(self.c, 3).messages, self.c.messages)

    def test_neg(self):
        self.assertEqual((-self.a).value, -42)
        self.assertEqual((-self.b).value, -42)
        self.assertEqual((-self.c).value, -42)

    def test_pos(self):
        self.assertEqual((+self.a).value, +42)
        self.assertEqual((+self.b).value, +42)
        self.assertEqual((+self.c).value, +42)

    def test_abs(self):
        self.assertEqual(abs(self.a).value, abs(42))
        self.assertEqual(abs(self.b).value, abs(42))
        self.assertEqual(abs(self.c).value, abs(42))


if __name__ == '__main__':
    unittest.main()
