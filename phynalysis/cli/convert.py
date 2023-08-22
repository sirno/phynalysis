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
    reference = "".join(open(args.reference).readlines())

    id_field = "block_id" if "block_id" in haplotypes_data.columns else "haplotype"
    max_compartment = haplotypes_data.compartment.max()

    if args.merge_replicates:
        haplotype_groups = haplotypes_data.groupby("haplotype")

        logging.info("Merged %s haplotypes.", len(haplotype_groups))
        counts = haplotype_groups["count"].sum()
        ids = haplotype_groups.apply(lambda group: group[id_field])
        taxa = haplotype_groups.apply(lambda group: group[id_field])
        haplotypes = haplotype_groups.apply(lambda group: group.name)
        times = haplotype_groups.apply(lambda group: group.time.min())
        lineages = haplotype_groups.apply(
            lambda group: group.compartment.mode()[0]
            + max_compartment * group.replicate.mode()[0]
        )
    else:
        counts = haplotypes_data["count"]
        haplotypes = haplotypes_data.haplotype
        times = haplotypes_data.time
        lineages = (
            haplotypes_data.compartment + max_compartment * haplotypes_data.replicate
        )
        taxa = haplotypes_data[id_field]
        ids = (
            haplotypes_data[id_field]
            + "_"
            + lineages.astype(str)
            + "_"
            + times.astype(str)
        )

    data = pd.DataFrame(
        {
            "id": ids,
            "haplotype": haplotypes,
            "count": counts,
            "time": times,
            "taxon": taxa,
            "lineage": lineages - lineages.min(),
        }
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
