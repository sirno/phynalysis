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
            self.query.replace(" ", "_")
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
            self.encoded_seed,
        )
        return config_path

@dataclass
class VirolutionConfig(JSONWizard, YAMLWizard):
    path: str
    generations: int

    def expand_path(self) -> List[VirolutionConfig]:
        configs = []
        expansion_stack = [self.path]
        list_regex = re.compile("\[(.*?)\]")
        while expansion_stack:
            path = expansion_stack.pop()
            list_match = re.search(list_regex, path)

            if list_match is None:
                configs.append(VirolutionConfig(path, self.generations))
                continue

            for item in list_match.group(1).split(","):
                expanded_path = path.replace(list_match.group(0), item)
                expansion_stack.append(expanded_path)

        return configs
