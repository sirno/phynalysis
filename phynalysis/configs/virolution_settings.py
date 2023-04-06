__all__ = [
    "Algebraic",
    "Linear",
    "Exponential",
    "Neutral",
    "FitnessModel",
    "SimulationParameters",
    "PlanRecord",
    "VirolutionSettings",
]

import csv
import os

from dataclasses import dataclass
from serious_serializers import SlotsSerializer
from typing import Union
from typing_extensions import Self

default_config = """
---
configs:
  - mutation_rate: 1e-6
    recombination_rate: 0
    host_population_size: 100000000
    infection_fraction: 0.7
    basic_reproductive_number: 100.0
    max_population: 100000000
    dilution: 0.02
    substitution_matrix:
      - [0., 1., 1., 1.]
      - [1., 0., 1., 1.]
      - [1., 1., 0., 1.]
      - [1., 1., 1., 0.]
    fitness_model:
        distribution: !Exponential
            weights:
                beneficial: 0.29
                deleterious: 0.51
                lethal: 0.2
                neutral: 0.0
            lambda_beneficial: 0.03
            lambda_deleterious: 0.21
        utility: !Algebraic
            upper: 1.5
plan:
  - generation: ({migration_offset} + {}) % {migration_period}
    event: transmission
    value: migration_fwd
  - generation: {} % {migration_period}
    event: transmission
    value: migration_rev
  - generation: {} % 200
    event: sample
    value: 10000
"""


@SlotsSerializer.show_tag
@dataclass(slots=True)
class Algebraic(SlotsSerializer):
    upper: float


@SlotsSerializer.show_tag
@dataclass(slots=True)
class Linear(SlotsSerializer):
    pass


@SlotsSerializer.show_tag
@dataclass(slots=True)
class Exponential(SlotsSerializer):
    weights: dict[str, float]
    lambda_beneficial: float
    lambda_deleterious: float


@SlotsSerializer.show_tag
@dataclass(slots=True)
class Neutral(SlotsSerializer):
    pass


Utility = Union[Linear, Algebraic]
Distribution = Union[Exponential, Neutral]


@dataclass(slots=True)
class FitnessModel(SlotsSerializer):
    distribution: Distribution
    utility: Utility


@dataclass(slots=True)
class SimulationParameters(SlotsSerializer):
    """Virolution settings."""

    mutation_rate: float
    recombination_rate: float
    host_population_size: int
    infection_fraction: float
    basic_reproductive_number: float
    max_population: int
    dilution: float
    substitution_matrix: list[list[float]]
    fitness_model: FitnessModel


@dataclass(slots=True)
class PlanRecord(SlotsSerializer):
    """Plan record."""

    generation: str
    event: str
    value: str


@dataclass(slots=True)
class VirolutionSettings(SlotsSerializer):
    """Run settings."""

    simulation_parameters: list[SimulationParameters]
    simulation_plan: list[PlanRecord]

    def sample_plan(self) -> Self:
        """Sample the plan."""
        plan = []
        for entry in self.simulation_plan:
            if hasattr(entry, "get_plan_records"):
                plan.extend(entry.get_plan_records())
            else:
                plan.append(entry)

        return VirolutionSettings(self.simulation_parameters, plan)

    def generate_virolution_configuration(self, path=".") -> None:
        """Generate a virolution configuration."""
        os.makedirs(path, exist_ok=True)

        for idx, config in enumerate(self.configs):
            config_path = os.path.join(path, f"config_{idx:03d}.yaml")
            config.to_yaml_file(config_path)

        plan_path = os.path.join(path, "plan.csv")
        with open(plan_path, "w") as plan_file:
            plan_writer = csv.DictWriter(
                plan_file,
                delimiter=";",
                fieldnames=PlanRecord.__slots__,
            )
            plan_writer.writeheader()
            for record in self.simulation_plan:
                plan_writer.writerow(record.to_dict())
