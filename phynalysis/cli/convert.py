"""Convert subcommand."""

import logging
import sys

from pathlib import Path

import numpy as np
import pandas as pd

from phynalysis.export import (
    write_fasta,
    write_nexus,
    write_phylip,
    write_xml,
    write_npy,
)


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


def enumerate_duplicates(data: pd.Series):
    """Enumerate duplicate ids."""
    counts = data.value_counts()
    duplicates = counts[counts > 1].index
    for duplicate in duplicates:
        indices = data[data == duplicate].index
        for i, index in enumerate(indices):
            data.loc[index] += f"_{i}"
    return data


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
        data[id_field] = data[id_field] + "_" + data.compartment.astype(str)
        groups = data.groupby([id_field])

        def _enumerate_duplicates(group):
            rep = group.loc[np.repeat(group.index.values, group["count"])]
            rep[id_field] = rep[id_field] + "_" + np.arange(len(rep)).astype(str)
            return rep

        data = groups.apply(_enumerate_duplicates)
        counts = data["count"]
        haplotypes = data.haplotype
        times = data.time
        lineages = data.compartment + max_compartment * data.replicate
        taxa = data[id_field]
        ids = data[id_field]

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
