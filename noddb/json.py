from typing import List, Union

from .node import Node, NodeArray, NodeBase
from .std_value import standard_value_types
from .value import InputValue, OutputValue
from .visitor import Visitor


class ExportException(Exception):
    pass


class ImportException(Exception):
    pass


class JsonRegistry:
    def __init__(self, custom_types: List[NodeBase] = []):
        self.type_dict = {typ.__name__: typ for typ in custom_types + standard_value_types()}

    def export_json(self, nodes: Union[NodeBase, list]):
        # Allow roots to be a single node or list of nodes
        if isinstance(nodes, NodeBase):
            nodes = [nodes]

        export = ExportVisitor(self)
        for node in nodes:
            node.visit(export)
        return export.to_json()

    def import_json(self, json_dict: dict) -> List[NodeBase]:
        if not all(key in json_dict for key in ['nodes', 'values', 'sources']):
            raise ImportException('Expecting nodes, values and sources entries at root')

        if not all(type(value) == dict for value in json_dict.values()):
            raise ImportException('Expecting dict type for nodes, values and sources')

        # Recursively instantiate all nodes by type
        loader = NodesLoader(self, json_dict['nodes'])

        # Set values from keys in values dict
        for path, value in json_dict['values'].items():
            if path not in loader.node_dict:
                raise ImportException(f"Invalid path '{path}' when loading values")
            loader.node_dict[path].set_value(value)

        # Connect values from keys in sources dict
        for dst, src in json_dict['sources'].items():
            if dst not in loader.node_dict:
                raise ImportException(f"Invalid input destination '{dst}' when loading sources")
            if src not in loader.node_dict:
                raise ImportException(f"Invalid output source '{src}' when loading sources")
            dst_value = loader.node_dict[dst]
            src_value = loader.node_dict[src]
            dst_value << src_value

        return loader.nodes


class NodesLoader:
    def __init__(self, registry: JsonRegistry, json_dict: dict):
        self.registry = registry
        self.nodes = {}
        self.node_dict = {}

        self._node_stack = []
        self._import_dict(json_dict)

    def _import_dict(self, json_dict: dict):
        for name, json_obj in json_dict.items():
            self._import_obj(name, json_obj)

    def _import_list(self, node_list: list):
        for json_obj in node_list:
            self._import_obj(None, json_obj)

    def _import_obj(self, name: str, json_obj):
        if isinstance(json_obj, dict):
            node = self._create_node(Node, name)
            self._push_parent(node)
            self._import_dict(json_obj)
            self._pop_parent()
        elif isinstance(json_obj, list):
            node = self._create_node(NodeArray, name)
            self._push_parent(node)
            self._import_list(json_obj)
            self._pop_parent()
            pass
        elif isinstance(json_obj, str):
            typename = json_obj
            if typename not in self.registry.type_dict:
                raise ExportException(f"Unexpected node type '{typename}' during import")
            type_class = self.registry.type_dict[typename]
            self._create_node(type_class, name)
        else:
            raise ImportException(f'Expecting dict, list or string values for nodes, found {type(json_obj)}')

    def _push_parent(self, node: NodeBase):
        self._node_stack.append(node)

    def _pop_parent(self):
        self._node_stack.pop()

    def _create_node(self, type_class: NodeBase, name=None):
        parent = self._node_stack[-1] if self._node_stack else None
        node = type_class(parent, name)
        self.node_dict[node.path()] = node

        # Store root nodes in returned import list
        if not parent:
            self.nodes[name] = node
        return node


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
                if node.typename not in self.registry.type_dict:
                    raise ExportException(f"Unexpected node type '{node.typename}' during export")

                # If this is a custom leaf node, then it can be serialised by typename
                self._add_to_container(node.name, node.typename)
                # Prevent descent into any children of custom node, e.g. values, sub-nodes
                self._push_container(None)
            else:
                # Otherwise create new dictionary for children in descent
                node_dict = {}
                self._add_to_container(node.name, node_dict)
                self._push_container(node_dict)
        else:
            # Continue preventing storage of descendants
            self._push_container(None)

    def on_node_exit(self, node: Node):
        self._pop_container()

    def on_node_array_enter(self, node: NodeArray):
        if self._can_store():
            # Create an array type to descend into
            node_array = []
            self._add_to_container(node.name, node_array)
            self._push_container(node_array)
        else:
            # Continue preventing storage of descendants
            self._push_container(None)

    def on_node_array_exit(self, node: NodeArray):
        self._pop_container()

    def on_input(self, value: InputValue):
        if self._can_store():
            if value.typename not in self.registry.type_dict:
                raise ExportException(f"Unexpected input value type '{value.typename}' during export")
            self._add_to_container(value.name, value.typename)

        if value.is_sourced():
            self.sources[value.path()] = value.source().path()
        else:
            self.values[value.path()] = value.value()

    def on_output(self, value: OutputValue):
        if self._can_store():
            if value.typename not in self.registry.type_dict:
                raise ExportException(f"Unexpected output value type '{value.typename}' during export")
            self._add_to_container(value.name, value.typename)

        self.values[value.path()] = value.value()

    def _push_container(self, json_obj):
        self._json_stack.append(json_obj)

    def _pop_container(self):
        self._json_stack.pop()

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
