from noddb.node import Node, NodeArray
from noddb.value import InputValue, OutputValue
from noddb.visitor import Visitor


def test_visit_values():
    fish = Node(None, 'fish')
    InputValue(fish, 'fingers', int(0))
    OutputValue(fish, 'knees', False)
    OutputValue(fish, 'toes', '')

    class ValueCounter(Visitor):
        def __init__(self):
            self.input_count = 0
            self.output_count = 0

        def on_input(self, value: InputValue):
            self.input_count += 1

        def on_output(self, value: OutputValue):
            self.output_count += 1

    counter = ValueCounter()
    fish.visit(counter)
    assert counter.input_count == 1
    assert counter.output_count == 2


def test_visit_order():
    class CollatePaths(Visitor):
        def __init__(self):
            self.paths = []

        def on_node_enter(self, node: Node):
            self.paths.append(node.path())

        def on_node_array_enter(self, node: NodeArray):
            self.paths.append(node.path())

        def on_input(self, value: InputValue):
            self.paths.append(value.path())

        def on_output(self, value: OutputValue):
            self.paths.append(value.path())

    root = Node(None, 'root')
    foo = Node(root, 'foo')
    InputValue(foo, 'x', True)
    bar = Node(root, 'bar')
    OutputValue(bar, 'y', False)

    collator = CollatePaths()
    root.visit(collator)
    assert collator.paths == ['root', 'root.foo', 'root.foo.x', 'root.bar', 'root.bar.y']


def test_visit_containers():
    class ReportContainers(Visitor):
        def __init__(self):
            self.log = []

        def on_node_enter(self, node: Node):
            self.log.append(f'enter:{node.path()}')

        def on_node_exit(self, node: Node):
            self.log.append(f'exit:{node.path()}')

        def on_node_array_enter(self, node: Node):
            self.log.append(f'enter_array:{node.path()}')

        def on_node_array_exit(self, node: Node):
            self.log.append(f'exit_array:{node.path()}')

    root = Node(None, 'root')
    a = Node(root, 'foo')
    b = Node(a, 'etc')
    OutputValue(b, 'value_ignored_by_visitor', int)
    c = NodeArray(root, 'bar')
    d = Node(c)
    InputValue(d, 'value_ignored_by_visitor', int)

    reporter = ReportContainers()
    root.visit(reporter)
    assert reporter.log == [
        'enter:root',
        'enter:root.foo',
        'enter:root.foo.etc',
        'exit:root.foo.etc',
        'exit:root.foo',
        'enter_array:root.bar',
        'enter:root.bar[0]',
        'exit:root.bar[0]',
        'exit_array:root.bar',
        'exit:root'
    ]

    # Check that arrays also work as root elements
    root_array = NodeArray(None, 'root_array')
    Node(root_array)
    Node(root_array)
    Node(root_array[1], 'foo')
    NodeArray(root_array)
    Node(root_array[2])
    Node(root_array[2][0], 'bar')

    reporter2 = ReportContainers()
    root_array.visit(reporter2)
    assert reporter2.log == [
        'enter_array:root_array',
        'enter:root_array[0]',
        'exit:root_array[0]',
        'enter:root_array[1]',
        'enter:root_array[1].foo',
        'exit:root_array[1].foo',
        'exit:root_array[1]',
        'enter_array:root_array[2]',
        'enter:root_array[2][0]',
        'enter:root_array[2][0].bar',
        'exit:root_array[2][0].bar',
        'exit:root_array[2][0]',
        'exit_array:root_array[2]',
        'exit_array:root_array'
    ]
