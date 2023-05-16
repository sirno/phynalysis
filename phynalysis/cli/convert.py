"""Convert subcommand."""

import logging
import sys

from pathlib import Path

import pandas as pd

from phynalysis.export import (
    write_fasta,
    write_nexus,
    write_phylip,
    write_xml,
    write_npy,
)

from .utils import write

_writers = {
    "fasta": write_fasta,
    "nexus": write_nexus,
    "phylip": write_phylip,
    "xml": write_xml,
    "npy": write_npy,
}

_suffixes = {
    "fasta": ".fasta",
    "nexus": ".nex",
    "phylip": ".phylip",
    "xml": ".xml",
    "npy": ".npz",
}


def convert(args):
    """Convert command main function."""
    for format in args.format:
        if format not in _writers:
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
        data = haplotypes_data[["time", "compartment", "haplotype", "count"]].copy()
        data["lineage"] = (
            haplotypes_data.compartment
            + haplotypes_data.compartment.max() * haplotypes_data.replicate
        )
        data["lineage"] -= data.lineage.min()
        data["id"] = (
            data["haplotype"]
            + "_"
            + data["lineage"].astype(str)
            + "_"
            + data["time"].astype(str)
        )

    # ensure each haplotype has a unique id
    data = data.reset_index(drop=True)
    data["id"] += "_" + data.index.astype(str)

    output_file = args.output
    for format in args.format:
        # select template
        template = None
        if args.template[format] is not None:
            template = args.template[format]

        # ensure output file has correct suffix
        if isinstance(args.output, Path):
            output_file = args.output.with_suffix(_suffixes[format])

        # convert data to desired format
        _writers[format](output_file, data, reference, template=template)
