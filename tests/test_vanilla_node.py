from unittest import TestCase
from noddb.node import Node, NodeException


class TestVanillaNodeMethods(TestCase):
    def test_root_node(self):
        foo = Node('foo')
        self.assertEqual(foo.name, 'foo')
        self.assertEqual(foo.parent, None)
        self.assertEqual(foo.children, {})

    def test_sub_node(self):
        foo = Node('foo')
        bar = Node('bar', foo)
        self.assertEqual(bar.name, 'bar')
        self.assertEqual(bar.parent, foo)
        self.assertEqual(bar.children, {})
        self.assertEqual(foo.children, {'bar':bar})

    def test_dup_sub_node(self):
        foo = Node('foo')
        _ = Node('bar', foo)
        with self.assertRaises(NodeException) as cm:
            _ = Node('bar', foo)
        self.assertEqual(str(cm.exception), 'parent "foo" already has child "bar"')

    def test_sub_path(self):
        foo = Node('foo')
        bar = Node('bar', foo)
        etc = Node('etc', bar)
        self.assertEqual(etc.path(), 'foo.bar.etc')

    def test_input_output(self):
        foo = Node('foo')
        self.assertEqual(foo.is_input(), False)
        self.assertEqual(foo.is_output(), False)


if __name__ == '__main__':
    unittest.main()
