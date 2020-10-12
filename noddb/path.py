from typing import List, Union
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

    def int_if_possible(name):
        if name[0].isdigit():
            return int(name.strip(']'))
        return name

    return [int_if_possible(name) for name in path_items]
