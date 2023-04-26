"""Sampler classes for plan record sampling."""

from __future__ import annotations

__all__ = ["DiscreteMigrationSampler", "ContinuousMigrationSampler"]

import random

from dataclasses import dataclass
from slot_machine import MappingSampler, ScalarSampler, SequenceSampler

from phynalysis.export.formatter import IncrementalFormatter

from .virolution_settings import PlanRecord


@dataclass(slots=True)
class DiscreteMigrationIntervalSampler(MappingSampler):
    """Sample plan records for discrete migration events."""

    frequency_range: str

    def get_sample(
        self,
        range: str,
        sample_period: str,
        sample_size: str,
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
class ContinuousMigrationSampler(SequenceSampler):
    """Sample plan records for continuous migration events."""

    @classmethod
    def get_sample(cls, range: str) -> PlanRecord:
        """Get migration sample plan records with continuous migration."""
        migration_rate = random.uniform(*map(float, range.split("..")))
        passage_rate = 1 - migration_rate

        return PlanRecord(
            generation="{} % 1",
            event="transmission",
            value=f"[[{passage_rate}, {migration_rate}], [{migration_rate}, {passage_rate}]]",
        )


@dataclass(slots=True)
class DiscreteMigrationSampler(SequenceSampler):
    """Sample plan records for continuous migration events."""

    @classmethod
    def get_sample(cls, values: list) -> PlanRecord:
        """Get migration sample plan records with continuous migration."""
        migration_rate = random.choice(list(map(float, values)))
        passage_rate = 1 - migration_rate

        return PlanRecord(
            generation="{} % 1",
            event="transmission",
            value=f"[[{passage_rate}, {migration_rate}],[{migration_rate}, {passage_rate}]]",
        )
