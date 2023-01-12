"""Configuration classes."""

import os

from dataclasses import dataclass
from dataclass_wizard import JSONWizard, YAMLWizard


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
        )

    @property
    def encoded_seed(self):
        return f"phyn_seed_{self.phyn_seed}_beast_seed_{self.beast_seed}"

    def config_path(self):
        config_path = os.path.join(
            "beast",
            self.template,
            self.sample,
            self.encoded_query,
            self.encoded_seed,
        )
        return config_path
