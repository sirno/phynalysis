"""Helper functions to read, write and process trees for phynalysis."""

from pathlib import Path
from typing import Union

import ete4


def read_tree(path: Union[str, Path]) -> ete4.Tree:
    """Read tree from file."""
    newick_tree = Path(path).read_text()
    return ete4.Tree(newick_tree)


def prune_tree(tree: ete4.Tree, taxa: list) -> ete4.Tree:
    """Prune tree and return strictly bifurcating tree."""
    tree = tree.copy()
    tree.prune(taxa)
    tree.resolve_polytomy(recursive=True)
    return tree


def write_tree(tree: ete4.Tree, path: Union[str, Path]):
    """Write tree to file."""
    newick_tree = tree.write()
    Path(path).write_text(newick_tree)
