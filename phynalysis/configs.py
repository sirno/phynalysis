"""Configuration classes."""

from __future__ import annotations

import os
import re

from dataclasses import dataclass
from dataclass_wizard import JSONWizard, YAMLWizard
from typing import List


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

    threads: int = 1
    time: str = "04-00"

    def expand_path(self) -> List[VirolutionConfig]:
        """Expand a path with list syntax into a list of paths."""
        return [
            VirolutionConfig.from_dict({**self.__dict__, "path": path})
            for path in _expand_path(self.path)
        ]


def _expand_path(path: str) -> List[str]:
    paths = []
    expansion_stack = [path]
    list_regex = re.compile("\[(.*?)\]")
    while expansion_stack:
        path = expansion_stack.pop(0)
        list_match = re.search(list_regex, path)

        if list_match is None:
            paths.append(path)
            continue

        for item in list_match.group(1).split(","):
            expanded_path = path.replace(list_match.group(0), item)
            expansion_stack.append(expanded_path)

    return paths
