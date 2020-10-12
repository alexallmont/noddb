from typing import List, Union

from .node import Node, NodeArray, NodeBase
from .path import path_to_node
from .std_value import standard_value_types
from .value import InputValue, OutputValue
from .visitor import Visitor


class ExportException(Exception):
    """
    Export exceptions are raised when unexpected data types are detected whilst traversing
    the node hierarchy.
    """
    pass


class ImportException(Exception):
    """
    Exception for unexpected types during import. If encountering this error, ensure that
    your registry custom_nodes contains all the types you are expecting.
    """
    pass


class JsonRegistry:
    """
    The registry wraps up import and export functions. This is because an application requires
    a common set of registered node types. The registry always contains the standard input and
    output value types (int, float, string and bool), and container types Node and NodeArray
    are implicitly supported. If an application has it's own custom nodes defined, say for
    processing inputs into output values, then the types of those nodes must be passed to the
    registry, e.g. JsonRegistry([FooNode, BarNode, CustomNode]).

    The json is structured into three parts: a top-level dictionary for root nodes, each of which
    recursively specifies the type of children in the hierarchy; a dictionary keying paths to
    values and the value they should be initialised with; a dictionary keying input paths to
    an output if it sources from it.

    For example nodes with a root and some application state, representing a CustomNode and
    FooNode under the root, along with a Node containing a NodeArray with two booleans in it.
    One of the boolean values is set explicitly, the other sources its value from elsewhere:
        {
            "nodes": {
                "root": {
                    "a": "CustomNode",
                    "b": "FooNode"
                    "c": {  // Node
                        "d": [  // NodeArray
                            "InputBool"  // Value in array, note these are not named
                            "InputBool"
                        ]
                    }
                }
                "application-state": {
                    "ok": "OutputBool"
                }
            }
            "values": {
                "root.c.d[0]": True  // Set first element of array to be true
            }
            "sources": {
                "root.c.d[1]": "application-state.ok"  // Second array bool is fed from app state
            }
        }
    """
    def __init__(self, custom_types: List[NodeBase] = []):
        self.type_dict = {typ.__name__: typ for typ in custom_types + standard_value_types()}

    def export_json(self, nodes: Union[NodeBase, list]):
        # Allow roots to be a single node or list of nodes
        if isinstance(nodes, NodeBase):
            nodes = [nodes]

        export = _ExportVisitor(self)
        for node in nodes:
            node.visit(export)
        return export.to_json()

    def import_json(self, json_dict: dict) -> List[NodeBase]:
        if not all(key in json_dict for key in ['nodes', 'values', 'sources']):
            raise ImportException('Expecting nodes, values and sources entries at root')

        if not all(type(value) == dict for value in json_dict.values()):
            raise ImportException('Expecting dict type for nodes, values and sources')

        # Recursively instantiate all nodes by type
        importer = _NodesImporter(self)
        importer.import_dict(json_dict['nodes'])

        # Set values from keys in values dict
        for path, value in json_dict['values'].items():
            node = path_to_node(importer.nodes, path)
            node.set_value(value)

        # Connect values from keys in sources dict
        for dst, src in json_dict['sources'].items():
            src_value = path_to_node(importer.nodes, src)
            dst_value = path_to_node(importer.nodes, dst)
            dst_value << src_value

        return importer.nodes


class _NodesImporter:
    """
    This class builds a dictionary of nodes whilst recursively importing dictionaries and lists
    from json. Effectively a node factory, using the node types in the registry and maintaining
    a stack during traversal to ensure that nodes have the correct parents.
    This class only deals with the nodes themselves. Values and Sources are dealt with in the
    import_json registry method.
    """
    def __init__(self, registry: JsonRegistry):
        self.registry = registry
        self.nodes = {}

        # Maintain a stack of nodes as they are instantiated to ensure that nodes
        # are created with the correct parent.
        self._node_stack = []

    def import_dict(self, json_dict: dict):
        for name, json_obj in json_dict.items():
            self.import_obj(name, json_obj)

    def import_list(self, node_list: list):
        for json_obj in node_list:
            self.import_obj(None, json_obj)

    def import_obj(self, name: str, json_obj):
        if isinstance(json_obj, dict):
            node = self.create_node(Node, name)
            self.push_parent(node)
            self.import_dict(json_obj)
            self.pop_parent()
        elif isinstance(json_obj, list):
            node = self.create_node(NodeArray, name)
            self.push_parent(node)
            self.import_list(json_obj)
            self.pop_parent()
            pass
        elif isinstance(json_obj, str):
            typename = json_obj
            if typename not in self.registry.type_dict:
                raise ImportException(f"Unexpected node type '{typename}' during import")
            type_class = self.registry.type_dict[typename]
            self.create_node(type_class, name)
        else:
            raise ImportException(f'Expecting dict, list or string values for nodes, found {type(json_obj)}')

    def push_parent(self, node: NodeBase):
        self._node_stack.append(node)

    def pop_parent(self):
        self._node_stack.pop()

    def create_node(self, type_class: NodeBase, name=None):
        parent = self._node_stack[-1] if self._node_stack else None
        node = type_class(parent, name)

        # Store root nodes in returned import list
        if not parent:
            self.nodes[name] = node
        return node


class _ExportVisitor(Visitor):
    """
    This visitor is used by the registry for exporting nodes to json dictionaries. When visiting
    from a particular root nodes it accumulates found nodes along with any values and internal
    connections.
    """
    def __init__(self, registry: JsonRegistry):
        self.registry = registry
        self.nodes = {}
        self.values = {}
        self.sources = {}

        # Internal stack represents the path to the node currently being visited, to ensure
        # values are stored to the correct json dict, and to prevent custom nodes from making
        # their child nodes visible during export.
        self._json_stack = [self.nodes]

    def on_node_enter(self, node: Node):
        if self.can_store():
            if node.is_custom():
                if node.typename not in self.registry.type_dict:
                    raise ExportException(f"Unexpected node type '{node.typename}' during export")

                # If this is a custom leaf node, then it can be serialised by typename
                self.add_to_container(node.name, node.typename)
                # Prevent descent into any children of custom node, e.g. values, sub-nodes
                self.push_container(None)
            else:
                # Otherwise create new dictionary for children in descent
                node_dict = {}
                self.add_to_container(node.name, node_dict)
                self.push_container(node_dict)
        else:
            # Continue preventing storage of descendants
            self.push_container(None)

    def on_node_exit(self, node: Node):
        self.pop_container()

    def on_node_array_enter(self, node: NodeArray):
        if self.can_store():
            # Create an array type to descend into
            node_array = []
            self.add_to_container(node.name, node_array)
            self.push_container(node_array)
        else:
            # Continue preventing storage of descendants
            self.push_container(None)

    def on_node_array_exit(self, node: NodeArray):
        self.pop_container()

    def on_input(self, value: InputValue):
        if self.can_store():
            if value.typename not in self.registry.type_dict:
                raise ExportException(f"Unexpected input value type '{value.typename}' during export")
            self.add_to_container(value.name, value.typename)

        if value.is_sourced():
            self.sources[value.path()] = value.source().path()
        else:
            self.values[value.path()] = value.value()

    def on_output(self, value: OutputValue):
        if self.can_store():
            if value.typename not in self.registry.type_dict:
                raise ExportException(f"Unexpected output value type '{value.typename}' during export")
            self.add_to_container(value.name, value.typename)

        self.values[value.path()] = value.value()

    def push_container(self, json_obj):
        self._json_stack.append(json_obj)

    def pop_container(self):
        self._json_stack.pop()

    def can_store(self):
        return self._json_stack[-1] is not None

    def add_to_container(self, key, value):
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
