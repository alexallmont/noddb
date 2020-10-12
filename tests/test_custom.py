from noddb.std_value import InputInt, OutputInt
from noddb.node import Node


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
