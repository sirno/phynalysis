"""Functions for analyzing haplotypes."""

from itertools import product
from typing import Callable

import numpy as np

from .transform import _ENCODING, Haplotype, haplotype_to_list, _encoder


def compute_fitness(
    haplotype: Haplotype,
    fitness_table: np.ndarray,
    utility: Callable[[float], float] | None = None,
):
    """Get the fitness of a haplotype."""
    haplotype = haplotype_to_list(haplotype)

    if utility is None:
        utility = lambda x: x

    return utility(
        np.prod([fitness_table[pos][_ENCODING[mut[-1]]] for pos, mut in haplotype])
    )


class FitnessTable:
    """Get a fitness table utility function."""

    def __init__(self, table: np.ndarray):
        self.table = table

    def compute_fitness(self, haplotype: Haplotype) -> float:
        return np.prod(self.table[pos][mut[-1]] for pos, mut in map(_encoder, haplotype))


class EpistasisMap:
    """Get an epistasis table utility function."""

    def __init__(self, map: dict):
        self.map = map

    def compute_fitness(self, haplotype: Haplotype) -> float:
        iterator = product(haplotype, haplotype)
        return np.prod(self.map.get((pos1, mut1[_
        return 1


class Algebraic:
    """Get an algebraic utility function."""

    def __init__(self, upper: float):
        self.upper = upper

    def __call__(self, fitness: float):
        factor = 1 / (self.upper - 1)
        return self.upper * factor * fitness / (1 + factor * fitness)
