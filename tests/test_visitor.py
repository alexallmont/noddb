import pytest

from noddb.node import Node
from noddb.value import InputValue, OutputValue, Value
from noddb.visitor import Visitor, visit


def test_visit_children():
    root = Node('root')
    Node('a', root)
    Node('b', root)

    # Check that all names may be accumulated by a lambda
    all_names = []
    visit(
        root,
        node_lambda=lambda node: all_names.append(node.path())
    )
    assert all_names == ['root', 'root.a', 'root.b']


class ValueTestNode(Node):
    """Concrete node with input and output for testing value visitation"""

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        InputValue('in', self, int(0))
        OutputValue('out', self, float(0))


def test_visit_values():
    root = Node('root')
    ValueTestNode('a', root)

    all_inputs = []
    visit(
        root,
        value_lambda=lambda value: all_inputs.append(value.path()) if value.is_input() else None
    )
    assert all_inputs == ['root.a.in']


class FindValuesVisitor(Visitor):
    """Search for all values depending on whether they are inputs or outputs"""

    def __init__(self, find_outputs: bool):
        super().__init__()
        self.find_outputs = find_outputs
        self.found_values = []

    def on_visit_value(self, value: Value, depth: int):
        if self.find_outputs:
            if value.is_output():
                self.found_values.append(value)
        else:
            if value.is_input():
                self.found_values.append(value)


def test_custom_visitor():
    root = Node('root')
    child = ValueTestNode('a', root)

    input_visitor = FindValuesVisitor(find_outputs=False)
    input_visitor.visit(root)
    assert input_visitor.found_values == [child.children['in']]

    output_visitor = FindValuesVisitor(find_outputs=True)
    output_visitor.visit(root)
    assert output_visitor.found_values == [child.children['out']]
