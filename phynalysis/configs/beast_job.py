"""Specify beast job configuration."""


from __future__ import annotations

__all__ = ["BeastJobConfig"]

import os

from dataclasses import dataclass
from slot_machine import SlotsSerializer
from typing_extensions import Self

from .utils import _expand_path

_ENCODING = [
    (", ", ","),
    (" ", "_"),
    ("<=", "le"),
    (">=", "ge"),
    ("<", "lt"),
    (">", "gt"),
    ("[", ""),
    ("]", ""),
    ("==", "eq"),
]


@dataclass(slots=True, frozen=True)
class BeastJobConfig(SlotsSerializer):
    template: str
    sample: str
    n_samples: int

    tree: str = "random"

    query: str = ""
    phyn_seed: int = 42
    beast_seed: int = 42

    beast_seeds: int = 0

    @property
    def encoded_query(self):
        if self.query == "":
            return "all"
        query = self.query
        for old, new in _ENCODING:
            query = query.replace(old, new)
        return query

    @property
    def encoded_seed(self):
        return f"ps_{self.phyn_seed}/bs_{self.beast_seed}"
        return f"phyn_seed_{self.phyn_seed}_beast_seed_{self.beast_seed}"

    @classmethod
    def from_path(cls, path: str) -> BeastJobConfig:
        """Create a config from a path."""
        splits = path.split("/")
        beast_start = splits.index("beast")
        virolution_start = splits.index("virolution")

        template = "/".join(splits[beast_start:virolution_start])
        sample = "/".join(splits[virolution_start:-6])

        query = splits[-6]
        n_samples = int(splits[-5])
        tree = splits[-4].split("_")[0]

        phyn_seed = splits[-3].split("_")[-1]
        beast_seed = splits[-2].split("_")[-1]

        return cls(
            template=template,
            sample=sample,
            query=query,
            n_samples=int(n_samples),
            tree=tree,
            phyn_seed=int(phyn_seed),
            beast_seed=int(beast_seed),
        )

    def get_config_path(self):
        """Return the path to the config file."""
        config_path = os.path.join(
            self.template,
            self.sample,
            self.encoded_query,
            str(self.n_samples),
            f"{self.tree}_tree",
            f"ps_{self.phyn_seed}",
        )
        return config_path


    def get_run_path(self):
        """Return the path to the run."""
        return os.path.join(self.get_config_path(), f"bs_{self.beast_seed}")

    def expand_paths(self) -> list[Self]:
        """Expand a path with list syntax into a list of paths."""
        template_paths = _expand_path(self.template)
        sample_paths = _expand_path(self.sample)
        beast_seeds = (
            range(self.beast_seed, self.beast_seed + self.beast_seeds)
            if self.beast_seeds
            else [self.beast_seed]
        )
        return [
            BeastJobConfig.from_dict(
                {
                    **self.to_dict(),
                    "template": template,
                    "sample": sample,
                    "beast_seed": beast_seed,
                }
            )
            for template in template_paths
            for sample in sample_paths
            for beast_seed in beast_seeds
        ]
