"""Haplotypes subcommand.

Analyse haplotypes in a sample. This module is used to find all haplotypes in each
sample.

The output is a CSV file with the following columns:
    - haplotype: Haplotype sequence
    - count: Number of sequences with this haplotype

Original author: Eva Bons
"""

import logging
from collections import Counter

import pandas as pd
import pysam

from ..parsers import changes_from_alignment


def haplotypes(args):
    """Haplotypes command main function."""
    logging.info(
        "Running phynalysis-haplotypes with quality_threshold=%s and length_threshold=%s",
        args.quality_threshold,
        args.length_threshold,
    )
    logging.info("Reading reference...")
    with open(args.reference, "r", encoding="utf8") as file_descriptor:
        reference = "".join(file_descriptor.read().splitlines()[1:])

    logging.info("Reading alignment...")
    alignment = pysam.AlignmentFile(args.input, "rb", check_sq=False)

    if args.length_threshold:
        logging.info("Filtering reads by length...")
        alignment = filter(
            lambda read: abs(read.reference_length - read.query_length)
            < args.length_threshold,
            alignment,
        )

    alignment = list(alignment)
    n_seq = len(alignment)

    logging.info("Computing mutations...")
    changes = changes_from_alignment(
        reference,
        alignment,
    )

    if args.quality_threshold > 0:
        logging.info("Filtering mutations by quality...")
        changes = changes.query("quality >= @args.quality_threshold")

    logging.info("Reformatting mutations...")
    counts = changes.groupby(["position", "mutation"], as_index=False).count()
    counts["frequencies"] = counts.seq_id / n_seq
    mutations = counts.drop(["seq_id", "quality"], axis=1)
    mutations.sort_values("frequencies", inplace=True, ascending=False)
    logging.info("Found %s mutations.", len(mutations))

    logging.info("Computing haplotypes...")
    haplotype_counter = Counter()
    haplotype_block_ids = {}

    # reconstruct all haplotypes from mutations
    for group in changes.groupby("seq_id"):
        haplotype = sorted(
            list(group[1].position.astype(str) + ":" + group[1].mutation)
        )
        haplotype = ";".join(haplotype)
        haplotype_counter[haplotype] += 1
        haplotype_block_ids[haplotype] = group[1].block_id.iloc[0]

    # add consensus haplotype because it does not contain any changes
    haplotype_counter["consensus"] = n_seq - changes.seq_id.unique().size
    haplotype_block_ids["consensus"] = None

    logging.info("Found %s haplotypes.", len(haplotype_counter))

    # create the haplotype dataframe
    haplotypes = pd.DataFrame(
        (haplotype, haplotype_block_ids[haplotype], haplotype_counter[haplotype]),
        columns=["haplotype", "block_id", "count"],
    )
    haplotypes.sort_values("count", inplace=True, ascending=False)

    # filter haplotypes with zero count
    haplotypes = haplotypes.query("count > 0")

    logging.info("Writing file %s...", args.output)
    haplotypes.to_csv(args.output, index=False)
