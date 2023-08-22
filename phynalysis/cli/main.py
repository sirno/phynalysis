import argparse
import logging
import sys

from collections import defaultdict
from pathlib import Path

from . import beast_xml

from .aggregate import aggregate
from .ancestors import ancestors
from .consensus import consensus
from .convert import convert
from .filter import filter
from .haplotypes import haplotypes
from .rescale import rescale
from .sample import sample
from .take import take


class ParseTemplate(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, defaultdict(lambda: None))
        if isinstance(values, str):
            values = [values]
        for value in values:
            key, value = value.split("=")
            getattr(namespace, self.dest)[key] = value


class ParsePath(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(values, str):
            setattr(namespace, self.dest, Path(values))
        else:
            setattr(namespace, self.dest, values)


class ParseBalanceWeights(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, defaultdict(lambda: 0))
        if isinstance(values, str):
            values = [values]
        for value in values:
            key, value = value.split("=") if "=" in value else (value, 1)
            getattr(namespace, self.dest)[key] = int(value)


def main():
    """Main."""
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "input",
        nargs="?",
        default=sys.stdin,
        action=ParsePath,
        help="Input file.",
    )
    common_parser.add_argument(
        "-o",
        "--output",
        default=sys.stdout,
        action=ParsePath,
        help="Output file.",
    )

    reference_parser = argparse.ArgumentParser(add_help=False)
    reference_parser.add_argument(
        "-r",
        "--reference",
        type=Path,
        required=True,
        help="Reference file.",
    )

    log_parser = argparse.ArgumentParser(add_help=False)
    log_parser.add_argument("--log-file", type=Path, help="Log file.")

    parser = argparse.ArgumentParser(description="Phynalysis toolbox.")

    subparsers = parser.add_subparsers(
        title="subcommands",
        dest="command",
        required=True,
    )

    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert data to other formats.",
        parents=[common_parser, reference_parser, log_parser],
    )
    convert_parser.add_argument(
        "--merge-replicates",
        action="store_true",
        help="Merge replicates.",
    )
    convert_parser.add_argument(
        "-f",
        "--format",
        nargs="+",
        type=str,
        help="Type of conversion.",
    )
    convert_parser.add_argument(
        "-t",
        "--template",
        action=ParseTemplate,
        default=defaultdict(lambda: None),
        help="Template file.",
    )
    convert_parser.set_defaults(func=convert)

    sample_parser = subparsers.add_parser(
        "sample",
        help="Sample data.",
        parents=[common_parser, log_parser],
    )
    sample_parser.add_argument(
        "--n-samples",
        type=int,
        default=0,
        help="Number of samples.",
    )
    sample_parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Random state.",
    )
    sample_parser.add_argument(
        "--replace-samples",
        action="store_true",
        help="Sample with replacement.",
    )
    sample_parser.add_argument(
        "--mode",
        type=str,
        default="random",
        choices=["random", "balance", "unique"],
        help="Sampling mode. One of: random, balance, unique. Default: random.",
    )

    # balance mode arguments
    sample_parser.add_argument(
        "--balance-groups",
        nargs="*",
        help="Groups to balance.",
    )
    sample_parser.add_argument(
        "--balance-weights",
        nargs="*",
        action=ParseBalanceWeights,
        help="Weights for groups to balance",
    )
    sample_parser.add_argument(
        "--n-samples-per-group",
        action="store_true",
        help="Sample `--n-samples` per group. If this is set, `--balance-weight` is ignored.",
    )

    sample_parser.set_defaults(func=sample)

    take_parser = subparsers.add_parser(
        "take",
        help="Take data.",
        parents=[common_parser, log_parser],
    )
    take_parser.add_argument(
        "--n-samples",
        type=int,
        default=0,
        help="Number of samples.",
    )
    take_parser.set_defaults(func=take)

    rescale_parser = subparsers.add_parser(
        "rescale",
        help="Rescale data columns.",
        parents=[common_parser, log_parser],
    )
    rescale_parser.add_argument(
        "--columns",
        nargs="+",
        help="Columns to rescale.",
        default=[],
    )
    rescale_parser.set_defaults(func=rescale)

    haplotypes_parser = subparsers.add_parser(
        "haplotypes",
        help="Extract haplotypes from alignment file.",
        parents=[common_parser, reference_parser, log_parser],
    )
    haplotypes_parser.add_argument(
        "--quality-threshold",
        type=int,
        default=47,
        help="Quality threshold",
    )
    haplotypes_parser.add_argument(
        "--length-threshold",
        type=int,
        default=100,
        help="Length threshold",
    )
    haplotypes_parser.set_defaults(func=haplotypes)

    filter_parser = subparsers.add_parser(
        "filter",
        help="Filter haplotypes data.",
        parents=[common_parser, log_parser],
    )
    filter_parser.add_argument("--query", type=str, help="Expr to filter by.")
    filter_parser.add_argument(
        "--filter-insertions",
        action="store_true",
        help="Filter insertions.",
    )
    filter_parser.set_defaults(func=filter)

    consensus_parser = subparsers.add_parser(
        "consensus",
        help="Compute a consensus sequence.",
        parents=[common_parser, reference_parser, log_parser],
    )
    consensus_parser.set_defaults(func=consensus)

    ancestors_parser = subparsers.add_parser(
        "ancestors",
        help="Find closes ancestors.",
        parents=[log_parser],
    )
    ancestors_parser.add_argument("input", type=Path, help="Input file.")
    ancestors_parser.add_argument("-o", "--output", type=Path, help="Output file.")
    ancestors_parser.set_defaults(func=ancestors)

    aggregate_parser = subparsers.add_parser(
        "aggregate",
        help="Aggregate haplotypes data into single file.",
        parents=[log_parser],
    )
    aggregate_parser.add_argument("barcodes", type=Path, help="Input file.")
    aggregate_parser.add_argument("input", nargs="+", type=Path, help="Input files.")
    aggregate_parser.add_argument("-o", "--output", type=Path, help="Output file.")
    aggregate_parser.set_defaults(func=aggregate)

    beast_xml_parser = subparsers.add_parser(
        "beast-xml",
        help="Generate BEAST XML file.",
    )

    beast_xml_instructions = beast_xml_parser.add_subparsers(
        title="instructions",
        dest="command",
        required=True,
    )

    beast_xml_insert_data_parser = beast_xml_instructions.add_parser(
        "insert-data",
        help="Insert data into BEAST XML file.",
        parents=[log_parser, common_parser],
    )
    beast_xml_insert_data_parser.set_defaults(func=beast_xml.insert_data)

    beast_xml_insert_tree_parser = beast_xml_instructions.add_parser(
        "insert-tree",
        help="Insert tree into BEAST XML file.",
        parents=[log_parser],
    )
    beast_xml_insert_tree_parser.add_argument(
        "xml",
        type=Path,
        help="Beast xml file",
    )
    beast_xml_insert_tree_parser.add_argument(
        "tree",
        type=Path,
        help="Tree file",
    )
    beast_xml_insert_tree_parser.set_defaults(func=beast_xml.insert_tree)

    args = parser.parse_args()
    logging.basicConfig(
        filename=args.log_file,
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    args.func(args)
