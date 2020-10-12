from noddb.json import JsonRegistry
from noddb.node import Node
from noddb.std_value import InputInt, OutputInt


class AddNode(Node):
    def init_custom(self):
        InputInt(self, 'a')
        InputInt(self, 'b')
        OutputInt(self, 'sum')

    def evaluate(self):
        self['sum'].set_value(self['a'].value() + self['b'].value())


def test_custom_setup():
    adder = AddNode(None, 'adder')
    assert adder.is_custom() is True
    assert len(adder.children) == 3
    assert type(adder['a']) == InputInt
    assert type(adder['b']) == InputInt
    assert type(adder['sum']) == OutputInt


def test_custom_evaluate():
    adder = AddNode(None, 'adder')
    adder['a'].set_value(5)
    adder['b'].set_value(7)
    adder.evaluate()
    assert adder['sum'].value() == 12


def test_custom_import():
    registry = JsonRegistry([AddNode])
    nodes = registry.import_json({
        'nodes': {
            'root': {
                'A': 'OutputInt',
                'B': 'OutputInt',
                'C': 'InputInt',
                'adder': 'AddNode'
            },
        },
        'values': {
            'root.A': 7,
            'root.B': 11,
        },
        'sources': {
            'root.adder.a': 'root.A',
            'root.adder.b': 'root.B',
            'root.C': 'root.adder.sum'
        }
    })
    root = nodes['root']
    assert root['A'].value() == 7
    assert root['B'].value() == 11
    assert root['adder']['a'].source() == root['A']
    assert root['adder']['b'].source() == root['B']
    assert root['C'].source() == root['adder']['sum']

    root['adder'].evaluate()
    assert root['C'].value() == 18
