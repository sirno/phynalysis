"""Sampler classes for plan record sampling."""

from __future__ import annotations

__all__ = ["DiscreteMigrationSampler", "ContinuousMigrationSampler"]

import random
import yaml

from abc import ABC, abstractmethod
from dataclasses import dataclass
from serious_serializers import SlotsSerializer, SlotsLoader
from typing_extensions import Self

from phynalysis.export.formatter import IncrementalFormatter

from .virolution_settings import PlanRecord


class Sampler(ABC):
    """Base class for samplers."""

    def __init_subclass__(cls) -> None:
        SlotsLoader.add_constructor(f"!{cls.__name__}", cls._construct_yaml)

    @classmethod
    @abstractmethod
    def _construct_yaml(cls, loader: yaml.Loader, node: yaml.nodes.Node) -> Self:
        """Construct the sampler from YAML."""
        pass

    @classmethod
    @abstractmethod
    def get_sample(cls, **kwargs):
        """Get the sample."""
        pass


class ScalarSampler(Sampler):
    """Define scalar sampler."""

    @classmethod
    def _construct_yaml(cls, loader: yaml.Loader, node: yaml.nodes.Node) -> Self:
        value = loader.construct_scalar(node)
        return cls.get_sample(value=value)


class FrequencySampler(ScalarSampler):
    """Define frequency sampler."""

    @classmethod
    def get_sample(cls, value: str) -> float:
        """Get the sample."""
        return random.uniform(*map(float, value.split("..")))


class PlanRecordSampler(Sampler):
    """Base class for plan record samplers."""

    @classmethod
    def _construct_yaml(cls, loader: yaml.Loader, node: yaml.nodes.Node) -> Self:
        mapping = loader.construct_mapping(node)
        return cls.get_sample(**mapping)


@dataclass(slots=True)
class DiscreteMigrationSampler(PlanRecordSampler):
    """Sample plan records for discrete migration events."""

    frequency_range: str

    def get_sample(
        self, range: str, sample_period: str, sample_size: str
    ) -> list[PlanRecord]:
        """Get the plan records with fwd and rev transmission."""
        fwd_generation_template = "({migration_offset} + {}) % {migration_period}"
        rev_generation_template = "{} % {migration_period}"
        sample_template = "{} % {sample_period}"

        sampled_frequency = random.randint(*map(int, range.split("..")))

        fwd_generation = IncrementalFormatter().format(
            fwd_generation_template,
            migration_offset=sampled_frequency,
            migration_period=2 * sampled_frequency,
        )
        rev_generation = IncrementalFormatter().format(
            rev_generation_template,
            migration_period=2 * sampled_frequency,
        )
        sample_generation = IncrementalFormatter().format(
            sample_template,
            sample_period=sample_period,
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
            PlanRecord(generation=sample_generation, event="sample", value=sample_size),
        ]


@dataclass(slots=True)
class ContinuousMigrationSampler(SlotsSerializer):
    """Sample plan records for continuous migration events."""

    def _sample_range(self):
        return random.uniform(*map(float, self.frequency_range.split("..")))

    def get_sample(
        self, range: str, sample_period: str, sample_size: str
    ) -> list[PlanRecord]:
        """Get migration sample plan records with continuous migration."""
        migration_rate = random.uniform(*map(float, range.split("..")))
        passage_rate = 1 - migration_rate

        sample_template = "{} % {sample_period}"

        sample_generation = IncrementalFormatter().format(
            sample_template,
            sample_period=sample_period,
        )

        return [
            PlanRecord(
                generation="{} % 1",
                event="transmission",
                value=f"[[{passage_rate}, {migration_rate}],[{migration_rate}, {passage_rate}]]",
            ),
            PlanRecord(generation=sample_generation, event="sample", value=sample_size),
        ]
