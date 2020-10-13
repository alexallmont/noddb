from noddb.json import JsonRegistry
from noddb.node import Node
from noddb.ref_value import OutputRef, InputRef


def test_ref_value():
    class RefableNode(Node):
        def init_custom(self):
            OutputRef(self, 'ref')

    class RefUser(Node):
        def init_custom(self):
            InputRef(self, 'ref')

    root = Node(None, 'root')
    foo = RefableNode(root, 'foo')
    bar = RefUser(root, 'bar')
    foo['ref'] >> bar['ref']

    # Ensure that the reference value refers directly to the node
    assert bar['ref'].value() == foo
    assert bar['ref'].value() == foo['ref'].value()

    # Ensure that the ref is saved but the 'value' of the output ref is not; it's
    # not necessary because it's value is its own parent node.
    registry = JsonRegistry([OutputRef, InputRef, RefableNode, RefUser])
    json_dict = registry.export_json(root)
    assert json_dict['sources']['root.bar.ref'] == 'root.foo.ref'
    assert json_dict['values'] == {}

    # Ensure that the imported data retains the ref connection
    imp_nodes = registry.import_json(json_dict)
    imp_root = imp_nodes['root']
    assert type(imp_root) == Node
    assert len(imp_root.children) == 2
    assert type(imp_root['foo']) == RefableNode
    assert type(imp_root['bar']) == RefUser
    assert imp_root['bar']['ref'].is_sourced()
    assert imp_root['bar']['ref'].value() == imp_root['foo']
