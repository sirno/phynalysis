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


def enumerate_duplicates(data: pd.Series, id_field: str):
    """Enumerate duplicate ids."""
    counts = data[id_field].value_counts()
    duplicates = counts[counts > 1].index
    for duplicate in duplicates:
        indices = data[data[id_field] == duplicate].index
        for i, index in enumerate(indices):
            data.loc[index, id_field] += f"_{i}"


def convert(
    output: Path,
    data: pd.DataFrame,
    reference: str,
    format: str,
    templates: dict,
    merge_replicates: bool = False,
):
    """Convert data to desired format."""
    id_field = "block_id" if "block_id" in data.columns else "haplotype"
    max_compartment = data.compartment.max()

    if merge_replicates:
        haplotype_groups = data.groupby("haplotype")

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
        counts = data["count"]
        haplotypes = data.haplotype
        times = data.time
        lineages = data.compartment + max_compartment * data.replicate
        taxa = enumerate_duplicates(data[id_field] + "_" + data.index.astype(str))
        ids = data[id_field] + "_" + lineages.astype(str) + "_" + times.astype(str)

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

    output_file = output
    for format in format:
        # select template
        template = templates[format]

        # ensure output file has correct suffix
        if isinstance(output, Path):
            output_file = output.with_suffix(_suffixes[format])

        # convert data to desired format
        _writers[format](output_file, data, reference, template=template)


def convert_cmd(args):
    """Convert command main function."""
    for format in args.format:
        if format not in _writers:
            logging.error("Unknown format: %s", args.format)
            sys.exit(1)

    haplotypes_data = pd.read_csv(args.input)
    reference = "".join(open(args.reference).readlines()[1:])

    convert(
        args.output,
        haplotypes_data,
        reference,
        args.format,
        args.template,
        args.merge_replicates,
    )
