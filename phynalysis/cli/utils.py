"""Cli utility functions."""

from pathlib import Path
from typing import Any


def write(file: Any, data: str):
    """Write file to output."""
    if isinstance(file, str | Path):
        with open(file, "w", encoding="utf8") as file_descriptor:
            file_descriptor.write(data)
    else:
        file.write(data)
