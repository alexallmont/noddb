from typing import List, Union
from .node import Node, NodeBase
import re


def split_path(path: str) -> List[Union[str, int]]:
    """
    Split a node/value path into component strings and integers. The split is not strict
    and assumes a relatively well-defined path with dots and square brackets delimiting
    each component.
    :param path: Path to a node, e.g. "foo.bar[4].etc[2][0].stuff"
    :return: List of names and indices in path, e.g. ["foo", "bar", 4, "etc", 2, 0, "stuff"]
    """
    path_items = re.split('[.[]', path)

    # When the first path element is an array path, e.g. "[0]", an erroneous empty string
    # is the first item. This explicitly removes it.
    if path_items and not path_items[0]:
        path_items.pop(0)

    def int_if_possible(name):
        if name[0].isdigit():
            return int(name.strip(']'))
        return name

    return [int_if_possible(name) for name in path_items]


def path_to_node(root: Union[Node, dict], path: str) -> NodeBase:
    """
    Get a node given root node or dict and a relative path. Note that the dict option
    for the root is for convenience when dealing with imported files, where top-level
    nodes are stored in a dict.
    :param root: Node or dict at root of search
    :param path: Path from root location to find node from
    :return: Found node or value
    """
    names = split_path(path)

    node = root
    while names:
        name_or_index = names.pop(0)
        node = node[name_or_index]

    return node
