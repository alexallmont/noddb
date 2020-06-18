from unittest import TestCase
from noddb.value import InputValue, OutputValue, ValueException
from noddb.node import Node


class TestVanillaValueMethods(TestCase):
    def test_input_value(self):
        n = Node('n')
        n_in = InputValue('in', n, 11)
        self.assertEqual(n_in.name, 'in')
        self.assertEqual(n_in.path(), 'n.in')
        self.assertEqual(n_in.is_input(), True)
        self.assertEqual(n_in.is_output(), False)
        self.assertEqual(n_in.parent, n)
        self.assertEqual(n_in.value(), 11)
        self.assertEqual(n_in.is_sourced(), False)
        self.assertEqual(n_in.source(), None)

    def test_input_value(self):
        n = Node('n')
        n_out = OutputValue('out', n, 13)
        self.assertEqual(n_out.name, 'out')
        self.assertEqual(n_out.path(), 'n.out')
        self.assertEqual(n_out.is_input(), False)
        self.assertEqual(n_out.is_output(), True)
        self.assertEqual(n_out.parent, n)
        self.assertEqual(n_out.value(), 13)
        self.assertEqual(n_out.is_sourced(), False)
        self.assertEqual(n_out.source(), None)

    def test_deep_path(self):
        foo = Node('foo')
        bar = Node('bar', foo)
        etc = Node('etc', bar)
        tez = InputValue('tez', etc, 17)
        self.assertEqual(tez.path(), 'foo.bar.etc.tez')

    def test_sourced(self):
        foo = Node('foo')
        foo_out = OutputValue('out', foo, 7)
        bar = Node('bar')
        bar_in = InputValue('out', bar, 5)

        bar_in.set_source(foo_out)
        self.assertEqual(bar_in.is_sourced(), True)
        self.assertEqual(bar_in.source(), foo_out)
        self.assertEqual(bar_in.value(), 7)

        with self.assertRaises(ValueException) as cm:
            bar_in.set_value(9)
        self.assertEqual(str(cm.exception), 'Cannot set input "bar.out" as value is already sourced from "foo.out"')

        bar_in.clear_source()
        self.assertEqual(bar_in.is_sourced(), False)
        self.assertEqual(bar_in.source(), None)
        bar_in.set_value(3)
        self.assertEqual(bar_in.value(), 3)

    def test_mismatch_set_value(self):
        n = Node('n')
        n_in = InputValue('in', n, 17)
        with self.assertRaises(ValueException) as cm:
            n_in.set_value("fish")
        self.assertEqual(str(cm.exception), 'Cannot set input "n.in" (int) to mismatched value of "fish" (str)')

    def test_source_from_non_output(self):
        a = InputValue('a', None, 'this')
        b = InputValue('b', None, 'that')
        with self.assertRaises(ValueException) as cm:
            b.set_source(a)
        self.assertEqual(str(cm.exception), 'Cannot set non-output "a" to a source')

    def test_double_source_input(self):
        a = OutputValue('a', None, 'this')
        b = OutputValue('b', None, 'that')
        c = InputValue('c', None, 'tother')
        c.set_source(a)
        with self.assertRaises(ValueException) as cm:
            c.set_source(b)
        self.assertEqual(str(cm.exception), 'Cannot set already-connected input "c" from output "b"')

    def test_source_to_non_input(self):
        a = OutputValue('a', None, 'this')
        b = OutputValue('b', None, 'that')
        with self.assertRaises(ValueException) as cm:
            b.set_source(a)
        self.assertEqual(str(cm.exception), 'Cannot set non-input "b" from a source')

    def test_source_mismatched_type(self):
        a = OutputValue('a', None, 23)
        b = InputValue('b', None, 'that')
        with self.assertRaises(ValueException) as cm:
            b.set_source(a)
        self.assertEqual(str(cm.exception), 'Cannot set input "b" (str) to mismatched output "a" (int)')

    def test_invalid_clear(self):
        foo = InputValue('foo', None, 27)
        with self.assertRaises(ValueException) as cm:
            foo.clear_source()
        self.assertEqual(str(cm.exception), 'Cannot clear source on non-connected input "foo"')


if __name__ == '__main__':
    unittest.main()
