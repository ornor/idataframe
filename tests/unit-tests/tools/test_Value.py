import unittest
from idataframe.tools import Value


class TestInit(unittest.TestCase):

    def setUp(self):
        self.a = Value(42)
        self.b = Value(42, 'asdf')
        self.c = Value(42, ['asdf1', 'asdf2', 'asdf3'])

    def test_value(self):
        self.assertEqual(self.a.value, 42)
        self.assertEqual(self.b.value, 42)
        self.assertEqual(self.c.value, 42)

    def test_messages(self):
        self.assertEqual(self.a.messages, [])
        self.assertEqual(self.b.messages, ['asdf'])
        self.assertEqual(self.b.message, 'asdf')
        self.assertEqual(self.c.messages, ['asdf1', 'asdf2', 'asdf3'])
        self.assertEqual(self.c.message, 'asdf1 | asdf2 | asdf3')


if __name__ == '__main__':
    unittest.main()
