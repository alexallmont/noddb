from .node import Node
from .value import Value


class Visitor:
    """
    Hierarchy visitor that steps into all child nodes and values from a root
    start point. Derived classes determine behaviour per node or value found.
    """
    def visit(self, node: Node, depth: int = 0):
        """
        Recursive hierarchical visit from a root node. Nodes and values are
        visited before their children.
        :param node: root node of hierarchy traversal
        :param depth: root depth, incremented per descendant
        :return: None
        """
        if isinstance(node, Value):
            self.on_visit_value(node, depth)
        else:
            self.on_visit_node(node, depth)

        for _, child in node.children.items():
            self.visit(child, depth + 1)

    def on_visit_node(self, node: Node, depth: int):
        """
        Callback when a node has been found in traversal
        :param node: node in hierarchy
        :param depth: depth of node relative to root visit depth
        :return:
        """
        pass

    def on_visit_value(self, value: Value, depth: int):
        """
        Callback when a value has been found in traversal
        :param value: value in hierarchy
        :param depth: depth of value relative to root visit depth
        :return:
        """
        pass


class LambdaVisitor(Visitor):
    """
    Internal class for specifying visitor callbacks as two lambdas rather
    than a new class. See visit() definition for callback specification.
    """
    def __init__(self, node_lambda=None, value_lambda=None):
        self.node_lambda = node_lambda
        self.value_lambda = value_lambda

    def on_visit_node(self, node: Node, _depth: int):
        if self.node_lambda:
            self.node_lambda(node)

    def on_visit_value(self, value: Value, _depth: int):
        if self.value_lambda:
            self.value_lambda(value)


def visit(node: Node, node_lambda=None, value_lambda=None):
    """
    Hierarchical traverse from root note calling lambda functions called
    per node or value, if functions specified. Lambda callback accepts
    node as argument.

    :param node: root node to start traversal from
    :param node_lambda: optional callback per node visited
    :param value_lambda: optional callback per value visited
    :return: None
    """
    visitor = LambdaVisitor(node_lambda, value_lambda)
    visitor.visit(node)
