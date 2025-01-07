"""Convert subcommand."""

import logging
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from phynalysis.export import (
    write_fasta,
    write_nexus,
    write_npy,
    write_phylip,
    write_xml,
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
    id_format: str = None,
    merge_replicates: bool = False,
):
    """Convert data to desired format."""
    if id_format is None:
        id_format = "{block_id}_{compartment}"

    id_field = "block_id" if "block_id" in data.columns else "haplotype"
    id_fields = re.findall(r"\{(\w+)\}", id_format)

    data.haplotype = data.haplotype.fillna("")

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
        data["id"] = data.apply(lambda x: id_format.format(**x[id_fields]), axis=1)
        groups = data.groupby("id")

        def _enumerate_duplicates(group):
            reps = [
                group.loc[np.repeat(idx, group["count"][idx])] for idx in group.index
            ]
            rep = pd.concat(reps)
            rep["id"] = rep["id"] + "_" + np.arange(len(rep)).astype(str)
            rep["count"] = np.ones(len(rep), dtype=int)
            return rep

        data = groups.apply(_enumerate_duplicates).reset_index(drop=True)
        counts = data["count"]
        haplotypes = data.haplotype
        times = data.time
        lineages = data.compartment + max_compartment * data.replicate
        taxa = data["id"]
        ids = data["id"]

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
    # data = data.reset_index(drop=True)
    # data["id"] += "_" + data.index.astype(str)

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
        args.id_format,
        args.merge_replicates,
    )
