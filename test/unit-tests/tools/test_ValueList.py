import unittest
from idataframe.tools import Value, ValueList


class TestInit(unittest.TestCase):

    def setUp(self):
        self.x = Value(42)
        self.y = Value(42, 'duplicate value')
        self.z = Value(42, ['asdf1', 'duplicate value', 'asdf2', 'asdf3'])

        self.a = ValueList().add(self.x).add(self.y).add(self.z)
        self.b = ValueList([self.x, self.y, self.z])

    def test_init(self):
        self.assertEqual(self.a.values, self.b.values)
        self.assertEqual(self.a.messages, self.b.messages)

    def test_items(self):
        self.assertIs(self.a.items[0], self.x)
        self.assertIs(self.a.items[1], self.y)
        self.assertIs(self.a.items[2], self.z)

    def test_values(self):
        self.assertEqual(self.a.values, [42, 42, 42])

    def test_messages(self):
        self.assertEqual(self.a.messages, ['duplicate value', 'asdf1',
                                           'asdf2', 'asdf3'])



if __name__ == '__main__':
    unittest.main()
