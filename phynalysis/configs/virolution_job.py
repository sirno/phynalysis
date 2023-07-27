"""Virolution job configuration."""

from __future__ import annotations

__all__ = ["VirolutionJobConfig"]

from dataclasses import dataclass
from slot_machine import SlotsSerializer
from typing_extensions import Self

from .utils import _expand_path


@dataclass(slots=True)
class VirolutionJobConfig(SlotsSerializer):
    path: str
    generations: int
    compartments: int
    sequence: str

    array: str = ""

    threads: int = 1
    time: str = "04-00"
    mem: str = "8G"

    def get_path(self):
        """Return the path to the config file."""
        return self.path

    def expand_path(self) -> list[Self]:
        """Expand a path with list syntax into a list of paths."""
        return [
            VirolutionJobConfig.from_dict({**self.to_dict(), "path": path})
            for path in _expand_path(self.path)
        ]
