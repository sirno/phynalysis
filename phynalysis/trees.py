"""Helper functions to read, write and process trees for phynalysis."""

from pathlib import Path
from typing import Union
from collections import defaultdict

import ete4


def read_tree(path: Union[str, Path]) -> ete4.Tree:
    """Read tree from file."""
    newick_tree = Path(path).read_text()
    return ete4.Tree(newick_tree)


def prune_tree(tree: ete4.Tree, taxa: list) -> ete4.Tree:
    """Prune tree and return strictly bifurcating tree."""
    tree = tree.copy()

    tree.prune(taxa)

    # add zero length branches to internal nodes
    for node in tree.traverse():
        # internal nodes are not pruned, so we need to remove their names if they are
        # not in the taxa list
        if node.name not in taxa:
            node.name = ""
            continue

        # add zero length branches to internal nodes
        if not node.is_leaf:
            node.add_child(name=node.name, dist=1)
            node.name = ""

    for node in tree.traverse():
        if len(node.children) == 1:
            node.delete()

    tree.resolve_polytomy(recursive=True)

    return tree


def enumerate_duplicates(tree: ete4.Tree) -> ete4.Tree:
    """Enumerate duplicate names in tree."""
    tree = tree.copy()

    names = defaultdict(lambda: 0)

    for node in tree.traverse():
        if node.name is not None:
            names[node.name] += 1

    for node in tree.traverse():
        if node.name is not None:
            name = node.name
            names[name] -= 1
            node.name += f"_{names[name]}"

    return tree


def write_tree(tree: ete4.Tree, path: Union[str, Path]):
    """Write tree to file."""
    newick_tree = tree.write()
    Path(path).write_text(newick_tree)
