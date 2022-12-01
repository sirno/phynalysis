"""Convert subcommand."""

import logging
import sys

from pathlib import Path

import pandas as pd

from phynalysis.export import get_fasta, get_nexus, get_phylip, get_xml

from .utils import write

_conversions = {
    "fasta": get_fasta,
    "nexus": get_nexus,
    "phylip": get_phylip,
    "xml": get_xml,
}

_suffixes = {
    "fasta": ".fasta",
    "nexus": ".nex",
    "phylip": ".phylip",
    "xml": ".xml",
}


def convert(args):
    """Convert command main function."""
    for format in args.format:
        if format not in _conversions:
            logging.error("Unknown format: %s", args.format)
            sys.exit(1)

    haplotypes_data = pd.read_csv(args.input)

    with open(args.reference, "r", encoding="utf8") as file_descriptor:
        reference = "".join(file_descriptor.read().splitlines()[1:])

    if args.merge_replicates:
        haplotype_groups = haplotypes_data.groupby("haplotype")
        logging.info("Loaded %s haplotypes.", len(haplotype_groups))

        haplotype_counts = haplotype_groups["count"].sum()
        ids = haplotype_groups.apply(lambda group: group.name)
        haplotypes = haplotype_groups.apply(lambda group: group.name)
        times = haplotype_groups.apply(lambda group: group.time.min())

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
            haplotypes_data.compartment
            + haplotypes_data.compartment.max() * haplotypes_data.replicate
        )
        data["lineage"] -= data.lineage.min()
        data["id"] = data["haplotype"] + "_" + data["lineage"].astype(str)

    # ensure each haplotype has a unique id
    data = data.reset_index(drop=True)
    data["id"] += "_" + data.index.astype(str)

    output_file = args.output
    for format in args.format:
        # convert data to desired format
        content = _conversions[format](data, reference, template=args.template[format])

        # ensure output file has correct suffix
        if isinstance(args.output, Path):
            output_file = args.output.with_suffix(_suffixes[format])

        # write content to file
        write(output_file, content)
