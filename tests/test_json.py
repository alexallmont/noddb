from noddb.node import Node, NodeArray
from noddb.json import JsonRegistry
from noddb.std_value import InputBool, InputInt, OutputBool, OutputInt


def test_complex():
    # Test storing a custom user-defined node
    class CustomNode(Node):
        def __init__(self, parent=None, name=None):
            super().__init__(parent, name)
            InputBool(self, 'inny', False)
            OutputInt(self, 'outy', 2)

    # Add a hierarcy under root 'foo'
    foo = Node(None, 'foo')
    x = OutputBool(foo, 'x', True)
    bar = NodeArray(foo, 'bar')
    y = OutputInt(bar, None, 3)
    etc = Node(bar)
    fzz = CustomNode(bar)
    z = InputInt(etc, 'z', 5)
    last = NodeArray(bar)
    InputBool(last, None)
    InputBool(last, None, True)

    # Test connecting inputs to outputs
    y >> z
    x >> fzz['inny']

    # Add an extra root not connected to 'foo'
    extra_root = CustomNode(None, 'extra_root')

    registry = JsonRegistry([CustomNode])
    assert registry.export_json([foo, extra_root]) == {
        'nodes': {
            'foo': {
                'bar': [
                    'OutputInt',
                    {
                        'z': 'InputInt'
                    },
                    'CustomNode',
                    [
                        'InputBool',
                        'InputBool'
                    ]
                ],
                'x': 'OutputBool'
            },
            'extra_root': 'CustomNode'
        },
        'sources': {
            'foo.bar[1].z': 'foo.bar[0]',
            'foo.bar[2].inny': 'foo.x'
        },
        'values': {
            'foo.bar[0]': 3,
            'foo.bar[2].outy': 2,
            'foo.bar[3][0]': False,
            'foo.bar[3][1]': True,
            'foo.x': True,
            'extra_root.inny': False,
            'extra_root.outy': 2
        }
    }
