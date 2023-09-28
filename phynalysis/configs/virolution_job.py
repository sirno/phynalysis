"""Virolution job configuration."""

from __future__ import annotations

__all__ = ["VirolutionJobConfig", "VirolutionResources"]

from dataclasses import dataclass
from slot_machine import SlotsSerializer
from typing_extensions import Self

from .utils import _expand_path

@dataclass(slots=True, frozen=True)
class VirolutionResources(SlotsSerializer):
    threads: int = 1
    time: str = "04-00"
    mem: str = "8G"


@dataclass(slots=True, frozen=True)
class VirolutionJobConfig(SlotsSerializer):
    path: str
    generations: int
    compartments: int
    sequence: str

    replicate: int = 0
    replicates: int = 1

    resources: VirolutionResources = VirolutionResources()

    def get_config_path(self):
        """Return the path to the config directory."""
        return self.path

    def get_run_path(self):
        """Get the path to the run directory."""
        if self.replicates > 1:
            return f"{self.path}/{self.replicate}"
        return self.path

    def expand_path(self) -> list[Self]:
        """Expand a path with list syntax into a list of paths."""
        return [
            VirolutionJobConfig.from_dict(
                {**self.to_dict(recursive=True), "path": path, "replicate": replicate}
            )
            for path in _expand_path(self.path)
            for replicate in range(self.replicates)
        ]
