"""Phynalysis toolbox arguments."""
import sys

from collections import defaultdict
from pathlib import Path
from tap import Tap


class CommonArgs(Tap):
    input: Path = None
    """Path to input file. If None, stdin is used."""
    output: Path = None
    """Path to output file. If None, stdout is used.""" ""

    def process_args(self):
        super().process_args()
        if self.input is None:
            self.input = sys.stdin
        if self.output is None:
            self.output = sys.stdout


class ReferenceArgs(Tap):
    reference: Path
    """Path to reference file."""


class LogArgs(Tap):
    log_file: Path
    """Path to log file."""

    verbose: int = 0
    """Verbosity level."""

    def configure(self):
        self.add_argument("--verbose", "-v", action="count")


class ConvertArgs(CommonArgs, ReferenceArgs, LogArgs):
    merge_replicates: bool = False
    """Merge replicates."""
    format: list = None
    """Type of conversion."""
    template: dict = None
    """Template file."""

    def configure(self):
        self.add_argument("--merge-replicates", action="store_true")

    def process_args(self):
        super().process_args()
        if self.format is None:
            self.format = []
        if self.template is None:
            self.template = defaultdict(lambda: None)
        if isinstance(self.template, str):
            self.template = [self.template]
        if isinstance(self.template, list):
            self.template = defaultdict(
                lambda: None, dict([t.split("=") for t in self.template])
            )


class SampleParser(CommonArgs, LogArgs):
    sample_size: int = 0
    """Number of samples."""
    random_state: int = 42
    """Random state."""
    replace: bool = False
    """Sample with replacement."""
    mode: str = "random"
    """Sampling mode. One of: random, balance, unique."""

    def configure(self):
        self.add_argument("--sample-size", "-n", type=int, default=0)
        self.add_argument("--random-state", "-r", type=int, default=42)
        self.add_argument("--replace", "-R", action="store_true")
        self.add_argument(
            "--mode",
            "-m",
            choices=["random", "first", "last"],
            default="random",
        )


class PhynalysisArgs(Tap):
    """Phynalysis toolbox"""

    def configure(self):
        self.add_subparsers(
            title="subcommands",
            dest="command",
            required=True,
        )
        self.add_subparser(
            "convert",
            ConvertArgs,
            description="Convert data to other formats.",
        )
        self.add_subparser(
            "sample",
            SampleParser,
            description="Sample data.",
        )
