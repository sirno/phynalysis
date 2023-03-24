"""Configuration classes."""

from __future__ import annotations

import csv
import os
import re

from collections import OrderedDict
from dataclasses import dataclass
from dataclass_wizard import JSONWizard, YAMLWizard
from random import randint
from typing import Dict, List, Union, get_type_hints

import yaml

from phynalysis.export.formatter import IncrementalFormatter


class Serializer:
    """Serialize to YAML."""

    def __init_subclass__(cls) -> None:
        # Add constructor to the yaml decoder
        def construct_yaml(
            loader: yaml.SafeLoader, node: yaml.nodes.MappingNode
        ) -> cls:
            value_map = loader.construct_mapping(node)
            return cls(**value_map)

        yaml.SafeLoader.add_constructor(f"!{cls.__name__}", construct_yaml)

        # Add representer to the yaml encoder
        def represent_yaml(
            dumper: yaml.SafeDumper, data: cls
        ) -> yaml.nodes.MappingNode:
            representer_tag = (
                f"!{cls.__name__}"
                if getattr(data, "_show_tag", False)
                else "tag:yaml.org,2002:map"
            )
            return dumper.represent_mapping(
                representer_tag,
                data.to_dict(),
            )

        yaml.SafeDumper.add_representer(cls, represent_yaml)

    def to_dict(self) -> Dict:
        """Convert to ordered dict."""
        return OrderedDict([(k, getattr(self, k)) for k in self.__slots__])

    def to_yaml(self) -> str:
        """Convert to yaml string."""
        return yaml.dump(self, Dumper=yaml.SafeDumper, sort_keys=False)

    def to_yaml_file(self, path):
        """Write to yaml file."""
        with open(path, "w") as f:
            f.write(self.to_yaml())

    def __str__(self) -> str:
        return self.to_yaml()

    @classmethod
    def from_dict(cls, data: Dict) -> Serializer:
        return cls(**data)

    @classmethod
    def from_yaml(cls, yaml_string: str) -> Serializer:
        if not yaml_string.startswith(f"!{cls.__name__}"):
            yaml_string = f"!{cls.__name__}\n{yaml_string}"

        dump = yaml.safe_load(yaml_string)

        if isinstance(dump, dict):
            return cls.from_dict(dump)

        if isinstance(dump, cls):
            return dump

        raise TypeError(f"Cannot load {cls.__name__} from {dump}")

    @classmethod
    def from_yaml_file(cls, path) -> Serializer:
        with open(path, "r") as f:
            return cls.from_yaml(f.read())

    @classmethod
    def show_tag(cls, subclass) -> Serializer:
        subclass._show_tag = True


@dataclass
class BeastConfig(JSONWizard, YAMLWizard):
    template: str
    sample: str
    n_samples: int

    query: str = ""
    phyn_seed: int = 42
    beast_seed: int = 42

    @property
    def encoded_query(self):
        if self.query == "":
            return "all"
        return (
            self.query.replace(", ", ",")
            .replace(" ", "_")
            .replace("<", "lt")
            .replace(">", "gt")
            .replace("[", "")
            .replace("]", "")
            .replace("==", "eq")
        )

    @property
    def encoded_seed(self):
        return f"phyn_seed_{self.phyn_seed}_beast_seed_{self.beast_seed}"

    def config_path(self):
        """Return the path to the config file."""
        config_path = os.path.join(
            self.template,
            self.sample,
            self.encoded_query,
            str(self.n_samples),
            self.encoded_seed,
        )
        return config_path

    def expand_paths(self) -> List[BeastConfig]:
        """Expand a path with list syntax into a list of paths."""
        template_paths = _expand_path(self.template)
        sample_paths = _expand_path(self.sample)
        return [
            BeastConfig.from_dict(
                {
                    **self.__dict__,
                    "template": template,
                    "sample": sample,
                }
            )
            for template in template_paths
            for sample in sample_paths
        ]


@dataclass
class VirolutionConfig(JSONWizard, YAMLWizard):
    path: str
    generations: int
    compartments: int

    run: Union[int, None] = None

    threads: int = 1
    time: str = "04-00"
    n_runs: int = 1

    def config_path(self):
        """Return the path to the config file."""
        if self.n_runs == 1:
            return self.path

        return os.path.join(self.path, f"run_{self.n_runs}")

    def expand_path(self) -> List[VirolutionConfig]:
        """Expand a path with list syntax into a list of paths."""
        return [
            VirolutionConfig.from_dict({**self.__dict__, "path": path, "run": run})
            for path in _expand_path(self.path)
            for run in range(self.n_runs)
        ]


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


@Serializer.show_tag
@dataclass(slots=True)
class Algebraic(Serializer):
    upper: float


@Serializer.show_tag
@dataclass(slots=True)
class Linear(Serializer):
    pass


@Serializer.show_tag
@dataclass(slots=True)
class Exponential(Serializer):
    weights: dict[str, float]
    lambda_beneficial: float
    lambda_deleterious: float


@Serializer.show_tag
@dataclass(slots=True)
class Neutral(Serializer):
    pass


Utility = Union[Linear, Algebraic]
Distribution = Union[Exponential, Neutral]


@dataclass(slots=True)
class FitnessModel(Serializer):
    distribution: Distribution
    utility: Utility


@dataclass(slots=True)
class SimulationParameters(Serializer):
    """Virolution settings."""

    mutation_rate: float
    recombination_rate: float
    host_population_size: int
    infection_fraction: float
    basic_reproductive_number: float
    max_population: int
    dilution: float
    substitution_matrix: List[List[float]]
    fitness_model: FitnessModel


@dataclass(slots=True)
class PlanRecord(Serializer):
    """Plan record."""

    generation: str
    event: str
    value: str


@dataclass(slots=True)
class TransmissionSample(Serializer):
    """Plan record sample."""

    frequency_range: str

    def get_plan_records(self) -> List[PlanRecord]:
        """Get the plan records."""
        fwd_generation_template = "({migration_offset} + {}) % {migration_period}"
        rev_generation_template = "{} % {migration_period}"

        range_regex = re.compile(r"(?P<start>\d+)\.\.(?P<end>\d+)")
        match = range_regex.match(self.frequency_range)
        migration_frequency = randint(
            int(match.group("start")), int(match.group("end"))
        )

        fwd_generation = IncrementalFormatter().format(
            fwd_generation_template,
            migration_offset=migration_frequency,
            migration_period=2 * migration_frequency,
        )
        rev_generation = IncrementalFormatter().format(
            rev_generation_template,
            migration_period=2 * migration_frequency,
        )
        return [
            PlanRecord(
                generation=fwd_generation,
                event="transmission",
                value="migration_fwd",
            ),
            PlanRecord(
                generation=rev_generation,
                event="transmission",
                value="migration_rev",
            ),
        ]


@dataclass(slots=True)
class RunConfig(Serializer):
    """Run settings."""

    simulation_parameters: List[SimulationParameters]
    simulation_plan: List[PlanRecord]

    def sample_plan(self) -> RunConfig:
        """Sample the plan."""
        plan = []
        for entry in self.simulation_plan:
            if hasattr(entry, "get_plan_records"):
                plan.extend(entry.get_plan_records())
            else:
                plan.append(entry)

        return RunConfig(self.simulation_parameters, plan)

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


def _expand_path(path: str) -> List[str]:
    paths = []
    expansion_stack = [path]
    range_regex = re.compile(r"\[(?P<start>\d+)-(?P<end>\d+)\]")
    list_regex = re.compile("\[(.*?)\]")
    while expansion_stack:
        path = expansion_stack.pop(0)

        range_match = re.search(range_regex, path)

        if range_match:
            for item in range(
                int(range_match.group("start")),
                int(range_match.group("end")) + 1,
            ):
                expanded_path = re.sub(range_regex, str(item), path, count=1)
                expansion_stack.append(expanded_path)
            continue

        list_match = re.search(list_regex, path)

        if list_match:
            for item in list_match.group(1).split(","):
                expanded_path = re.sub(list_regex, item, path, count=1)
                expansion_stack.append(expanded_path)
            continue

        paths.append(path)

    return sorted(paths)
