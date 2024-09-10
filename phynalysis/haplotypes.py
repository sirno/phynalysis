"""Functions for analyzing haplotypes."""

from itertools import product
from typing import Callable

import numpy as np

from .transform import Haplotype


class Fitness:
    """Get a fitness table utility function."""

    def __init__(
        self,
        fitness_providers: list,
        utility: Callable[[float], float] | None = None,
    ):
        self.iter = iter
        self.utility = utility

    def compute_fitness(self, haplotype: Haplotype) -> float:
        fitness = np.prod(
            fitness_provider.compute_fitness(haplotype)
            for fitness_provider in self.fitness_providers
        )

        if self.utility is not None:
            fitness = self.utility(fitness)

        return fitness


class FitnessTable:
    """Get a fitness table utility function."""

    def __init__(self, table: np.ndarray):
        self.table = table

    def compute_fitness(self, haplotype: Haplotype) -> float:
        return np.prod(self.table[pos][mut] for pos, (_, mut) in haplotype)


class EpistasisMap:
    """Get an epistasis table utility function."""

    def __init__(self, map: dict):
        self.map = map

    def compute_fitness(self, haplotype: Haplotype) -> float:
        iterator = product(haplotype, haplotype)
        return np.prod(
            self.map.get((pos1, mut1, pos2, mut2), 1)
            for (pos1, (_, mut1)), (pos2, (_, mut2)) in iterator
        )


class Algebraic:
    """Get an algebraic utility function."""

    def __init__(self, upper: float):
        self.upper = upper

    def __call__(self, fitness: float):
        factor = 1 / (self.upper - 1)
        return self.upper * factor * fitness / (1 + factor * fitness)
