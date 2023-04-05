"""Sampler classes for plan record sampling."""

__all__ = ["DiscreteMigrationSampler", "ContinuousMigrationSampler"]

import random

from dataclasses import dataclass
from serious_serializers import SlotsSerializer

from phynalysis.export.formatter import IncrementalFormatter

from .virolution_settings import PlanRecord

@dataclass(slots=True)
class DiscreteMigrationSampler(SlotsSerializer):
    """Sample plan records for discrete migration events."""

    frequency_range: str

    def _sample_range(self):
        return random.randint(*map(int, self.frequency_range.split("..")))

    def get_plan_records(self) -> list[PlanRecord]:
        """Get the plan records with fwd and rev transmission."""
        fwd_generation_template = "({migration_offset} + {}) % {migration_period}"
        rev_generation_template = "{} % {migration_period}"

        migration_frequency = self._sample_range()

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
class ContinuousMigrationSampler(SlotsSerializer):
    """Sample plan records for continuous migration events."""

    frequency_range: str

    def _sample_range(self):
        return random.uniform(*map(float, self.frequency_range.split("..")))

    def get_plan_records(self) -> list[PlanRecord]:
        """Get migration sample plan records with continuous migration."""
        migration_rate = self._sample_range()
        passage_rate = 1 - migration_rate

        return [
            PlanRecord(
                generation="{} % 1",
                event="transmission",
                value=f'"[[{passage_rate}, {migration_rate}],[{migration_rate}, {passage_rate}]]"'
            )
        ]