from .node import Node
from .value import Value


class Visitor:
    def visit(self, node: Node, depth: int = 0):
        if isinstance(node, Value):
            self.on_visit_value(node, depth)
        else:
            self.on_visit_node(node, depth)

        for _, child in node.children.items():
            self.visit(child, depth + 1)

    def on_visit_node(self, node: Node, depth: int):
        pass

    def on_visit_value(self, value: Value, depth: int):
        pass


class LambdaVisitor(Visitor):
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
    visitor = LambdaVisitor(node_lambda, value_lambda)
    visitor.visit(node)
