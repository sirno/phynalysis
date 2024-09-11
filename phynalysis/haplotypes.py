"""Functions for analyzing haplotypes.

## Example:

```python
table = FitnessTable.load("fitness_table.npy")
epistasis = EpistasisMap.load("epistasis_map.npy")

fitness_function = FitnessFunction([table, epistasis])
fitness = fitness_function.compute_fitness(haplotype)
"""

from itertools import product
from typing import Callable

import numpy as np

from .transform import Haplotype

__all__ = ["FitnessFunction", "FitnessTable", "EpistasisMap", "Algebraic"]


class FitnessFunction:
    """Get a fitness table utility function."""

    def __init__(
        self,
        fitness_providers: list,
        utility: Callable[[float], float] | None = None,
    ):
        self.fitness_providers = fitness_providers
        self.utility = utility

    def compute_fitness(self, haplotype: Haplotype) -> float:
        fitness = np.prod(
            [
                fitness_provider.compute_fitness(haplotype)
                for fitness_provider in self.fitness_providers
            ]
        )

        if self.utility is not None:
            fitness = self.utility(fitness)

        return fitness


class FitnessTable:
    """Get a fitness table utility function."""

    def __init__(self, table: np.ndarray):
        if isinstance(table, str):
            raise ValueError("Use `load` method to load a table from a file.")

        self.table = table

    @classmethod
    def load(cls, path: str):
        return cls(np.load(path))

    def compute_fitness(self, haplotype: Haplotype) -> float:
        return np.prod([self.table[pos][mut] for pos, (_, mut) in haplotype])


class EpistasisMap:
    """Get an epistasis table utility function."""

    def __init__(self, map: dict):
        if isinstance(map, str):
            raise ValueError("Use `load` method to load a table from a file.")

        self.map = map

    @classmethod
    def load(cls, path: str):
        table = np.load(path)
        return cls(
            {
                (pos1, mut1, pos2, mut2): value
                for (pos1, mut1, pos2, mut2, value) in table
            }
        )

    def compute_fitness(self, haplotype: Haplotype) -> float:
        iterator = product(haplotype, haplotype)
        return np.prod(
            [
                self.map.get((pos1, mut1, pos2, mut2), 1)
                for (pos1, (_, mut1)), (pos2, (_, mut2)) in iterator
            ]
        )


class Algebraic:
    """Get an algebraic utility function."""

    def __init__(self, upper: float):
        self.upper = upper

    def __call__(self, fitness: float):
        factor = 1 / (self.upper - 1)
        return self.upper * factor * fitness / (1 + factor * fitness)
