"""Specify beast job configuration."""


from __future__ import annotations

__all__ = ["BeastJobConfig"]

import os

from dataclasses import dataclass
from slot_machine import SlotsSerializer
from typing_extensions import Self

from .utils import _expand_path


@dataclass(slots=True)
class BeastJobConfig(SlotsSerializer):
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

    def expand_paths(self) -> list[Self]:
        """Expand a path with list syntax into a list of paths."""
        template_paths = _expand_path(self.template)
        sample_paths = _expand_path(self.sample)
        return [
            BeastJobConfig.from_dict(
                {
                    **self.to_dict(),
                    "template": template,
                    "sample": sample,
                }
            )
            for template in template_paths
            for sample in sample_paths
        ]
