import argparse
import logging
import sys

from .aggregate import aggregate
from .ancestors import ancestors
from .consensus import consensus
from .convert import convert
from .haplotypes import haplotypes


def main():
    """Main."""
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "input",
        nargs="?",
        default=sys.stdin,
        help="Input file.",
    )
    common_parser.add_argument(
        "-r",
        "--reference",
        type=str,
        help="Reference file.",
    )
    common_parser.add_argument(
        "-o",
        "--output",
        default=sys.stdout,
        help="Output file.",
    )

    log_parser = argparse.ArgumentParser(add_help=False)
    log_parser.add_argument("--log-file", type=str, help="Log file.")

    parser = argparse.ArgumentParser(description="Phynalysis toolbox.")

    subparsers = parser.add_subparsers(
        title="subcommands",
        dest="command",
        required=True,
    )

    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert data to other formats.",
        parents=[common_parser, log_parser],
    )
    convert_parser.add_argument(
        "--n-samples",
        type=int,
        default=0,
        help="Number of samples.",
    )
    convert_parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Random state.",
    )
    convert_parser.add_argument(
        "--filter-insertions",
        action="store_true",
        help="Filter insertions.",
    )
    convert_parser.add_argument(
        "--exclude-ancestors",
        action="store_true",
        help="Exclude ancestors.",
    )
    convert_parser.add_argument(
        "--merge-replicates",
        action="store_true",
        help="Merge replicates.",
    )
    convert_parser.add_argument(
        "-f",
        "--format",
        default="phylip",
        type=str,
        help="Type of conversion.",
    )
    convert_parser.add_argument(
        "-t",
        "--template",
        type=str,
        help="Template file.",
    )
    convert_parser.set_defaults(func=convert)

    haplotypes_parser = subparsers.add_parser(
        "haplotypes",
        help="Extract haplotypes from alignment file.",
        parents=[common_parser, log_parser],
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

    consensus_parser = subparsers.add_parser(
        "consensus",
        help="Compute a consensus sequence.",
        parents=[common_parser, log_parser],
    )
    consensus_parser.set_defaults(func=consensus)

    ancestors_parser = subparsers.add_parser(
        "ancestors",
        help="Find closes ancestors.",
        parents=[log_parser],
    )
    ancestors_parser.add_argument("input", type=str, help="Input file.")
    ancestors_parser.add_argument("-o", "--output", type=str, help="Output file.")
    ancestors_parser.set_defaults(func=ancestors)

    aggregate_parser = subparsers.add_parser(
        "aggregate",
        help="Aggregate haplotypes data into single file.",
        parents=[log_parser],
    )
    aggregate_parser.add_argument("barcodes", type=str, help="Input file.")
    aggregate_parser.add_argument("input", nargs="+", type=str, help="Input files.")
    aggregate_parser.add_argument("-o", "--output", type=str, help="Output file.")
    aggregate_parser.set_defaults(func=aggregate)

    args = parser.parse_args()
    logging.basicConfig(
        filename=args.log_file,
        level=logging.INFO,
        format="%(levelname)s:%(asctime)s %(message)s",
    )
    args.func(args)


def write(file, data):
    """Write file to output."""
    if isinstance(file, str):
        with open(file, "w", encoding="utf8") as file_descriptor:
            file_descriptor.write(data)
    else:
        file.write(data)
