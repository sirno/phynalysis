"""Convert subcommand."""

import logging
import sys

import pandas as pd

from .utils import write
from phynalysis.export import (
    get_nexus,
    get_phylip,
    get_xml,
)

_conversions = {
    "nexus": get_nexus,
    "phylip": get_phylip,
    "xml": get_xml,
}


def convert(args):
    """Convert command main function."""
    if args.format not in _conversions:
        logging.error("Unknown format: %s", args.format)
        sys.exit(1)

    haplotypes_data = pd.read_csv(args.input)

    with open(args.reference, "r", encoding="utf8") as file_descriptor:
        reference = "".join(file_descriptor.read().splitlines()[1:])

    if args.filter_insertions:
        haplotypes_data = haplotypes_data[
            not haplotypes_data.haplotype.str.contains("i")
        ]

    if args.merge_replicates:
        haplotype_groups = haplotypes_data.groupby("haplotype")
        logging.info("Loaded %s haplotypes.", len(haplotype_groups))

        haplotype_counts = haplotype_groups["count"].sum()
        ids = haplotype_groups.apply(lambda group: group.name)
        haplotypes = haplotype_groups.apply(lambda group: group.name)
        times = haplotype_groups.apply(lambda group: 100 * group.time.min())

        data = pd.DataFrame(
            {
                "id": ids,
                "haplotype": haplotypes,
                "count": haplotype_counts,
                "time": times,
            }
        )
    else:
        data = haplotypes_data[["time", "haplotype", "count"]].copy()
        data["lineage"] = (
            haplotypes_data.replicate
            + haplotypes_data.replicate.max() * haplotypes_data.compartment
        )
        data["id"] = data["haplotype"] + "_" + data["lineage"].astype(str)

    if args.n_samples:
        data = data.sample(
            args.n_samples,
            weights="count",
            random_state=args.random_state,
            replace=False,
        )

    # load template file if needed
    template = None
    if args.template:
        with open(args.template, "r", encoding="utf8") as file_descriptor:
            template = file_descriptor.read()

    # convert data to desired format
    formatted_data = _conversions[args.format](data, reference, template=template)

    write(args.output, formatted_data)
