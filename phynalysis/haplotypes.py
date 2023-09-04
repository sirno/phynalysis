"""Functions for analyzing haplotypes."""

import numpy as np

from typing import Callable

from .transform import haplotype_to_list, Haplotype, _ENCODING

def compute_fitness(haplotype: Haplotype, fitness_table: np.ndarray, utility: Callable[[float], float] | None = None):
    """Get the fitness of a haplotype."""
    haplotype = haplotype_to_list(haplotype)

    if utility is None:
        utility = lambda x: x

    return utility(np.prod([fitness_table[pos][_ENCODING[mut[-1]]] for pos, mut in haplotype]))


class Algebraic:
    """Get a algebraic utility function."""
    def __init__(self, upper: int):
        self.upper = upper

    def __call__(self, fitness: float):
        factor = 1 / (self.upper - 1)
        return self.upper * factor * fitness / (1 + factor * fitness)
