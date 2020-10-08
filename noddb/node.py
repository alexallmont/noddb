from .visitor import Visitor, VisitorException


class NodeException(Exception):
    """
    This exception relates to any problems found whilst creating nodes. In particular
    that the type and name, and parent-child relationship is valid for the node type.
    """
    pass


class NodeBase:
    """
    A noddb node is part of a hierarchy that can be represented in a path. This base
    class is a leaf node that may have a name and parent. Concrete implementations of
    nodes derive from this class to specify their values which may be connected to
    form a DAG.
    The only nodes which shouldn't have a name are those stored in a NodeArray,
    because the child name is derived from its index in the array.
    """
    def __init__(self, parent=None, name=None):
        self._name = name
        self._parent = parent

        if parent:
            if not isinstance(parent, NodeContainer):
                raise NodeException(f'Nodes must parent to container types: parent is {type(parent)}')
            parent._add_child(self)
        else:
            if not name:
                raise NodeException('Unparented leaf nodes must be named')

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def typename(self):
        return self.__class__.__name__

    def path(self):
        result = ''
        if self._parent:
            result += self._parent.path()

            # Delimit with a dot for non-array children
            # FIXME check conditional though type, not by name
            if self._name[0] != '[':
                result += '.'

        result += self._name
        return result

    def visit(self, visitor: Visitor):
        raise VisitorException(f'visit not implemented for node type {self.typename}')


class NodeContainer(NodeBase):
    """
    Abstract base class for node that contains child nodes that may be accessed
    using square brackets, e.g. foo['bar'].
    """
    def _add_child(self, child: NodeBase):
        raise NodeException(f'_add_child not implemented for {self.typename}')

    def __getitem__(self, _item_name: str):
        raise NodeException(f'__getitem__ not implemented for {self.typename}')


class Node(NodeContainer):
    """
    This is the most commonly-used node type, with child nodes (and values) keyed
    stored in a dictionary, keyed by name.
    """
    def __init__(self, parent=None, name=None):
        self._child_dict = {}
        super().__init__(parent, name)

    def _add_child(self, child: NodeBase):
        if not isinstance(child._name, str):
            raise NodeException(f'Node children must be named: unnamed {child.typename} in {self.path()}')

        if child.name in self._child_dict:
            raise NodeException(f"Node child names must be unique: '{child.name}' already in {self.path()}")

        self._child_dict[child.name] = child

    def __getitem__(self, child_name: str):
        if child_name not in self._child_dict:
            raise NodeException(f"Node {self.path()} does not have child '{child_name}'")
        return self._child_dict[child_name]

    def visit(self, visitor: Visitor):
        visitor.on_node_enter(self)
        for child in self._child_dict.values():
            child.visit(visitor)
        visitor.on_node_exit(self)

    def is_custom(self):
        """
        Customised nodes are concrete derivatives of Node, for example with inputs and outputs declared
        in it's constructor. Unlike container nodes, a concrete implementation usually does not need to
        store any of its children, because they will be created in its constructor.
        :return: False if this is exactly a Node container type, True if customised
        """
        return type(self) != Node

    @property
    def children(self):
        return list(self._child_dict.values())


class NodeArray(NodeContainer):
    """
    An array node container stores children by index.
    """
    def __init__(self, parent=None, name=None):
        self._child_list = []
        super().__init__(parent, name)

    def visit(self, visitor: Visitor):
        visitor.on_node_array_enter(self)
        for child in self._child_list:
            child.visit(visitor)
        visitor.on_node_array_exit(self)

    def _add_child(self, child: NodeBase):
        if child._name:
            raise NodeException(f"NodeArray children must not be named: found 'name' in {self.path()}")

        # Convert the name to a convenient alias for fast path lookup
        child._name = f'[{len(self._child_list)}]'
        self._child_list.append(child)

    def __getitem__(self, child_index: int):
        if child_index < 0 or child_index >= len(self._child_list):
            raise NodeException(
                f'NodeArray bounds error: {child_index} is not in 0-{len(self._child_list)} for {self.path()}'
            )
        return self._child_list[child_index]

    @property
    def children(self):
        return self._child_list
