import unittest

from idataframe.tools import is_na, Value, Message


class TestInit(unittest.TestCase):

    def setUp(self):
        self.a = Value(42)
        self.b = Value(42, None, 'asdf')
        self.c = Value(42, None, ['asdf1', 'asdf2', 'asdf3'])

    def test_value(self):
        self.assertEqual(self.a.value, 42)
        self.assertEqual(self.b.value, 42)
        self.assertEqual(self.c.value, 42)

        def override_value():
            self.a.value = 42
        self.assertRaises(PermissionError, override_value)

        self.assertEqual(self.a.values, [42])
        self.assertEqual(Value([42, 84], None, 'insert stack').values, [42, 84])

        self.assertTrue(is_na(Value(None)))

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

    def test_stack_unstack(self):
        x = Value(42).stack(84).stack(168)
        y = Value(42, None, 'asdf1').stack(Value(84, None, 'asdf2')) ^ x

        self.assertEqual(x.values, Value([42, 84, 168], None, 'asdf').values)
        self.assertEqual(x.stack(396).values, [42, 84, 168, 396])
        self.assertEqual(int(x + 2), 44)
        self.assertEqual((x ^ 1 ^ 2 ^ 3).values, [42, 84, 168, 396, 1, 2, 3])
        self.assertEqual(y.values, [42, 84, 42, 84, 168])
        self.assertEqual(y.messages, ['asdf1', 'asdf2'])
        self.assertEqual(y.stack('asdf').values, [42, 84, 42, 84, 168, 'asdf'])
        self.assertEqual(Value([1, 2, 3, 4]).unstack(2)[0], 1)
        self.assertEqual(Value([1, 2, 3, 4]).unstack(2)[1], 2)
        self.assertEqual(Value([1, 2, 3, 4]).unstack(2)[2], [3, 4])


    def test_binding(self):
        def double(v:Value) -> Value[int|float]:
            return Value(2*v.value)

        self.assertEqual(self.a.bind(double).value, 2*42)
        self.assertEqual((self.a | double).value, 2*42)
        self.assertEqual((Value([42, 1, 2]) | double).values, [2*42])

        def manual_error(v:Value) -> Value[float]:
            if v.value == 0:
                return Value(None, None, 'Error: dividing by zero')
            return Value(100/v.value)

        self.assertEqual(Value(42).bind(manual_error).value, 100/42)
        self.assertEqual(Value(0).bind(manual_error).value, 0)
                                                   # old value (0) is preserved
        self.assertEqual(Value(0).bind(manual_error).message,
                                                 'Error: dividing by zero')

    def test_repr(self):
        self.assertEqual(repr(Value(42)),
                         "idataframe.tools.Value(42)")
        self.assertEqual(repr(Value(42, None, ['asdf'])),
                         "idataframe.tools.Value(42, None, 'asdf')")
        self.assertEqual(repr(Value(42, None, ['asdf1', 'asdf2'])),
                         "idataframe.tools.Value(42, None, ['asdf1', 'asdf2'])")
        self.assertEqual(repr(Value([42, 84], None, ['asdf'])),
                         "idataframe.tools.Value([42, 84], None, 'asdf')")
        self.assertEqual(repr(Value()),
                         "idataframe.tools.Value(None)")
        self.assertEqual(repr(Value(None, None, 'asdf')),
                         "idataframe.tools.Value(None, None, 'asdf')")

    def test_prefix(self):
        self.assertEqual(self.a.prefix_messages('prefix_').messages, [])
        self.assertEqual(Value(None, None,
                                '').prefix_messages('prefix_').messages, [''])
        self.assertEqual(self.b.prefix_messages('prefix_').messages,
                         Value(self.b.value, None, 'prefix_asdf').messages)
        self.assertEqual(self.c.prefix_messages('prefix_').messages,
                         Value(self.b.value, None,
                               ['prefix_asdf1', 'prefix_asdf2',
                                'prefix_asdf3']).messages)

    def test_suffix(self):
        self.assertEqual(self.a.suffix_messages('_suffix').messages, [])
        self.assertEqual(Value(None, None,
                               '').suffix_messages('_suffix').messages,
                                                                         [''])
        self.assertEqual(self.b.suffix_messages('_suffix').messages,
                         Value(self.b.value, None, 'asdf_suffix').messages)
        self.assertEqual(self.c.suffix_messages('_suffix').messages,
                         Value(self.b.value, None,
                               ['asdf1_suffix', 'asdf2_suffix',
                                              'asdf3_suffix']).messages)

    def test_copy(self):
        self.assertTrue(id(self.a) != id(self.a.copy()))

    def test_str(self):
        self.assertEqual(str(self.a), '42')
        self.assertEqual(str(self.b), '42')
        self.assertEqual(str(self.c), '42')
        self.assertTrue(is_na(str(Value(None))))   # idataframe.tools.na_str

    def test_int(self):
        self.assertEqual(int(self.a), 42)
        self.assertEqual(int(self.b), 42)
        self.assertEqual(int(self.c), 42)
        self.assertTrue(is_na(int(Value(None))))   # idataframe.tools.na_int

    def test_float(self):
        self.assertEqual(float(self.a), 42.0)
        self.assertEqual(float(self.b), 42.0)
        self.assertEqual(float(self.c), 42.0)
        self.assertTrue(is_na(float(Value(None)))) # idataframe.tools.na_float

    def test_add(self):
        self.assertEqual((self.a + Value(2)).value, 42+2)
        self.assertEqual((self.b + Value(2.3)).value, 42+2.3)
        self.assertEqual((self.c + Value(3)).value, 42+3)
        self.assertEqual((self.b + self.c).messages,
                    Value(None, None,
                          self.b.messages + self.c.messages).messages)
        self.assertEqual((self.c + self.c).messages, self.c.messages)
        self.assertEqual((self.a + 2).value, 42+2)
        self.assertEqual((self.b + 2.3).value, 42+2.3)
        self.assertEqual((self.c + 3).value, 42+3)
        self.assertEqual((self.c + 3).messages, self.c.messages)
        self.assertEqual((Value([42, 84]) + Value(1)).value, 42+1)
        self.assertEqual((Value([42, 84], None, 'asdf1')
                          + Value([1, 2], None, 'asdf2')).values, [42+1, 84])
        self.assertEqual((Value([42, 84], None, 'asdf1')
                          + Value([1, 2], None, 'asdf2')).messages,
                                                         ['asdf1', 'asdf2'])
        self.assertIsNone((self.a + Value(None)).value)
        self.assertIsNone((Value(None) + self.a).value)
        self.assertIsNone((self.a + None).value)

    def test_sub(self):
        self.assertEqual((self.a - Value(2)).value, 42-2)
        self.assertEqual((self.b - Value(2.3)).value, 42-2.3)
        self.assertEqual((self.c - Value(3)).value, 42-3)
        self.assertEqual((self.b - self.c).messages,
                    Value(None, None,
                          self.b.messages + self.c.messages).messages)
        self.assertEqual((self.c - self.c).messages, self.c.messages)
        self.assertEqual((self.a - 2).value, 42-2)
        self.assertEqual((self.b - 2.3).value, 42-2.3)
        self.assertEqual((self.c - 3).value, 42-3)
        self.assertEqual((self.c - 3).messages, self.c.messages)
        self.assertIsNone((self.a - Value(None)).value)
        self.assertIsNone((Value(None) - self.a).value)
        self.assertIsNone((self.a - None).value)

    def test_mul(self):
        self.assertEqual((self.a * Value(2)).value, 42*2)
        self.assertEqual((self.b * Value(2.3)).value, 42*2.3)
        self.assertEqual((self.c * Value(3)).value, 42*3)
        self.assertEqual((self.b * self.c).messages,
                    Value(None, None,
                          self.b.messages + self.c.messages).messages)
        self.assertEqual((self.c * self.c).messages, self.c.messages)
        self.assertEqual((self.a * 2).value, 42*2)
        self.assertEqual((self.b * 2.3).value, 42*2.3)
        self.assertEqual((self.c * 3).value, 42*3)
        self.assertEqual((self.c * 3).messages, self.c.messages)
        self.assertIsNone((self.a * Value(None)).value)
        self.assertIsNone((Value(None) * self.a).value)
        self.assertIsNone((self.a * None).value)

    def test_truediv(self):
        self.assertEqual((self.a / Value(2)).value, 42/2)
        self.assertEqual((self.b / Value(2.3)).value, 42/2.3)
        self.assertEqual((self.c / Value(3)).value, 42/3)
        self.assertEqual((self.b / self.c).messages,
                    Value(None, None,
                          self.b.messages + self.c.messages).messages)
        self.assertEqual((self.c / self.c).messages, self.c.messages)
        self.assertEqual((self.a / 2).value, 42/2)
        self.assertEqual((self.b / 2.3).value, 42/2.3)
        self.assertEqual((self.c / 3).value, 42/3)
        self.assertEqual((self.c / 3).messages, self.c.messages)
        self.assertIsNone((self.a / Value(None)).value)
        self.assertIsNone((Value(None) / self.a).value)
        self.assertIsNone((self.a / None).value)

    def test_floordiv(self):
        self.assertEqual((self.a // Value(2)).value, 42//2)
        self.assertEqual((self.b // Value(2.3)).value, 42//2.3)
        self.assertEqual((self.c // Value(3)).value, 42//3)
        self.assertEqual((self.b // self.c).messages,
                    Value(None, None,
                          self.b.messages + self.c.messages).messages)
        self.assertEqual((self.c // self.c).messages, self.c.messages)
        self.assertEqual((self.a // 2).value, 42//2)
        self.assertEqual((self.b // 2.3).value, 42//2.3)
        self.assertEqual((self.c // 3).value, 42//3)
        self.assertEqual((self.c // 3).messages, self.c.messages)
        self.assertIsNone((self.a // Value(None)).value)
        self.assertIsNone((Value(None) // self.a).value)
        self.assertIsNone((self.a // None).value)

    def test_pow(self):
        self.assertEqual((self.a ** Value(2)).value, 42**2)
        self.assertEqual((self.b ** Value(2.3)).value, 42**2.3)
        self.assertEqual((self.c ** Value(3)).value, 42**3)
        self.assertEqual((self.b ** self.c).messages,
                    Value(None, None,
                          self.b.messages + self.c.messages).messages)
        self.assertEqual((self.c ** self.c).messages, self.c.messages)
        self.assertEqual((self.a ** 2).value, 42**2)
        self.assertEqual((self.b ** 2.3).value, 42**2.3)
        self.assertEqual((self.c ** 3).value, 42**3)
        self.assertEqual((self.c ** 3).messages, self.c.messages)
        self.assertIsNone((self.a ** Value(None)).value)
        self.assertIsNone((Value(None) ** self.a).value)
        self.assertIsNone((self.a ** None).value)

    def test_mod(self):
        self.assertEqual((self.a % Value(2)).value, 42%2)
        self.assertEqual((self.b % Value(2.3)).value, 42%2.3)
        self.assertEqual((self.c % Value(3)).value, 42%3)
        self.assertEqual((self.b % self.c).messages,
                    Value(None, None,
                          self.b.messages + self.c.messages).messages)
        self.assertEqual((self.c % self.c).messages, self.c.messages)
        self.assertEqual((self.a % 2).value, 42%2)
        self.assertEqual((self.b % 2.3).value, 42%2.3)
        self.assertEqual((self.c % 3).value, 42%3)
        self.assertEqual((self.c % 3).messages, self.c.messages)
        self.assertIsNone((self.a % Value(None)).value)
        self.assertIsNone((Value(None) % self.a).value)
        self.assertIsNone((self.a % None).value)

    def test_divmod(self):
        self.assertEqual(divmod(self.a, Value(2)).value, divmod(42, 2))
        self.assertEqual(divmod(self.b, Value(2.3)).value, divmod(42, 2.3))
        self.assertEqual(divmod(self.c, Value(3)).value, divmod(42, 3))
        self.assertEqual(divmod(self.b, self.c).messages,
                    Value(None, None,
                          self.b.messages + self.c.messages).messages)
        self.assertEqual(divmod(self.c, self.c).messages, self.c.messages)
        self.assertEqual(divmod(self.a, 2).value, divmod(42, 2))
        self.assertEqual(divmod(self.b, 2.3).value, divmod(42, 2.3))
        self.assertEqual(divmod(self.c, 3).value, divmod(42, 3))
        self.assertEqual(divmod(self.c, 3).messages, self.c.messages)
        self.assertIsNone(divmod(self.a, Value(None)).value)
        self.assertIsNone(divmod(Value(None), self.a).value)
        self.assertIsNone(divmod(self.a, None).value)

    def test_neg(self):
        self.assertEqual((-self.a).value, -42)
        self.assertEqual((-self.b).value, -42)
        self.assertEqual((-self.c).value, -42)
        self.assertEqual((-Value([42, 84], None, 'asdf')).values, [-42, 84])
        self.assertEqual((-Value([42, 84], None, 'asdf')).messages, ['asdf'])
        self.assertIsNone((-Value(None)).value)

    def test_pos(self):
        self.assertEqual((+self.a).value, +42)
        self.assertEqual((+self.b).value, +42)
        self.assertEqual((+self.c).value, +42)
        self.assertIsNone((+Value(None)).value)

    def test_abs(self):
        self.assertEqual(abs(self.a).value, abs(42))
        self.assertEqual(abs(self.b).value, abs(42))
        self.assertEqual(abs(self.c).value, abs(42))
        self.assertIsNone(abs(Value(None)).value)

    def test_round(self):
        self.assertEqual(round(Value(42.36)).value, abs(42))
        self.assertEqual(round(Value(42.36), 1).value, abs(42.4))
        self.assertIsNone(round(Value(None)).value)

if __name__ == '__main__':
    unittest.main()
