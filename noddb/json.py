from typing import List

from .node import Node, NodeArray, NodeBase
from .std_value import standard_value_types
from .value import InputValue, OutputValue
from .visitor import Visitor


class JsonRegistry:
    def __init__(self, node_types=[], value_types=[]):
        self.node_dict = {typ.__name__: typ for typ in node_types}
        self.value_dict = {typ.__name__: typ for typ in value_types + standard_value_types()}

    def export_json(self, nodes: List[NodeBase]):
        # Allow roots to be a single node or a list of nodes
        if isinstance(nodes, NodeBase):
            nodes = [nodes]

        export = ExportVisitor(self)
        for node in nodes:
            node.visit(export)
        return export.to_json()


class ExportException(Exception):
    pass


class ExportVisitor(Visitor):
    def __init__(self, registry: JsonRegistry):
        self.registry = registry
        self.nodes = {}
        self.values = {}
        self.sources = {}
        self._json_stack = [self.nodes]

    def on_node_enter(self, node: Node):
        if self._can_store():
            if node.is_custom():
                if node.typename not in self.registry.node_dict:
                    raise ExportException(f"Unexpected node type '{node.typename}' during export")

                # If this is a custom leaf node, then it can be serialised by typename
                self._add_to_container(node.name, node.typename)
                # Prevent descent into any children of custom node, e.g. values, sub-nodes
                self._json_stack.append(None)
            else:
                # Otherwise create new dictionary for children in descent
                node_dict = {}
                self._add_to_container(node.name, node_dict)
                self._json_stack.append(node_dict)
        else:
            # Continue preventing storage of descendants
            self._json_stack.append(None)

    def on_node_exit(self, node: Node):
        self._json_stack.pop()

    def on_node_array_enter(self, node: NodeArray):
        if self._can_store():
            # Create an array type to descend into
            node_array = []
            self._add_to_container(node.name, node_array)
            self._json_stack.append(node_array)
        else:
            # Continue preventing storage of descendants
            self._json_stack.append(None)

    def on_node_array_exit(self, node: NodeArray):
        self._json_stack.pop()

    def on_input(self, value: InputValue):
        if self._can_store():
            if value.typename not in self.registry.value_dict:
                raise ExportException(f"Unexpected input value type '{value.typename}' during export")

            self._add_to_container(value.name, value.typename)

        if value.is_sourced():
            self.sources[value.path()] = value.source().path()
        else:
            self.values[value.path()] = value.value()

    def on_output(self, value: OutputValue):
        if self._can_store():
            if value.typename not in self.registry.value_dict:
                raise ExportException(f"Unexpected output value type '{value.typename}' during export")

            self._add_to_container(value.name, value.typename)

        self.values[value.path()] = value.value()

    def _can_store(self):
        return self._json_stack[-1] is not None

    def _add_to_container(self, key, value):
        parent = self._json_stack[-1]
        if isinstance(parent, dict):
            parent[key] = value
        elif isinstance(parent, list):
            parent.append(value)

    def to_json(self):
        return {
            'nodes': self.nodes,
            'values': self.values,
            'sources': self.sources
        }
