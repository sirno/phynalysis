"""Virolution job configuration."""

from __future__ import annotations

__all__ = ["VirolutionJobConfig"]

import os

from dataclasses import dataclass
from serious_serializers import SlotsSerializer
from typing import Union
from typing_extensions import Self

from .utils import _expand_path

@dataclass(slots=True)
class VirolutionJobConfig(SlotsSerializer):
    path: str
    generations: int
    compartments: int

    _run: int = 1

    threads: int = 1
    time: str = "04-00"
    mem: str = "8G"
    n_runs: int = 1

    def config_path(self):
        """Return the path to the config file."""
        if self.n_runs == 1:
            return self.path

        return os.path.join(self.path, f"run_{self._run}")

    def expand_path(self) -> list[Self]:
        """Expand a path with list syntax into a list of paths."""
        return [
            VirolutionJobConfig.from_dict({**self.to_dict(), "path": path, "_run": run})
            for path in _expand_path(self.path)
            for run in range(self.n_runs)
        ]
