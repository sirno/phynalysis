"""Analyse haplotypes in a sample.

This module is used to find the frequency of mutations and haplotypes in each
sample.

It creates two output files:

- a file containing the frequency of mutations in each sample
- a file containing the frequency of haplotypes in each sample

Original author: Eva Bons

Usage: phynalysis-haplotypes reference.fasta alignment.bam output_mutations.csv output_haplotypes.csv
"""

import argparse
import logging

from collections import Counter

import pysam

import pandas as pd

from ..parsers import changes_from_alignment


def main(args):
    """Main."""
    logging.basicConfig(
        filename=args.log_file,
        level=logging.INFO,
        format="%(levelname)s:%(asctime)s %(message)s",
    )
    logging.info(
        "Running phynalysis-haplotypes with quality_threshold=%s and length_threshold=%s",
        args.quality_threshold,
        args.length_threshold,
    )
    logging.info("Reading reference...")
    with open(args.reference, "r", encoding="utf8") as file_descriptor:
        reference = "".join(file_descriptor.read().splitlines()[1:])

    logging.info("Reading alignment...")
    alignment = pysam.AlignmentFile(args.alignment, "rb", check_sq=False)
    changes, n_seq = changes_from_alignment(
        reference,
        alignment,
        quality_threshold=args.quality_threshold,
        length_threshold=args.length_threshold,
    )

    logging.info("Computing mutations...")
    counts = changes.groupby(["position", "mutation"], as_index=False).count()
    counts["frequencies"] = counts.seq_id / n_seq
    mutations = counts.drop(["seq_id", "quality"], axis=1)
    mutations.sort_values("frequencies", inplace=True, ascending=False)
    logging.info("Found %s mutations.", len(mutations))

    logging.info("Computing haplotypes...")
    haplotype_counter = Counter()
    for group in changes.groupby("seq_id"):
        haplotype = sorted(
            list(group[1].position.astype(str) + ":" + group[1].mutation)
        )
        haplotype = ";".join(haplotype)
        haplotype_counter[haplotype] += 1
    haplotype_counter["consensus"] = n_seq - changes.seq_id.unique().size
    logging.info("Found %s haplotypes.", len(haplotype_counter))

    haplotypes = pd.DataFrame(haplotype_counter.items(), columns=["haplotype", "count"])
    # haplotypes["frequencies"] = haplotypes["count"] / n_seq
    haplotypes.sort_values("count", inplace=True, ascending=False)

    logging.info("Writing file %s...", args.output_mutations)
    mutations.to_csv(args.output_mutations, index=False)

    logging.info("Writing file %s...", args.output_haplotypes)
    haplotypes.to_csv(args.output_haplotypes, index=False)


def entry():
    """Entry."""
    parser = argparse.ArgumentParser(description="Analyse haplotypes in a sample.")

    parser.add_argument("reference", help="Reference file")
    parser.add_argument("alignment", help="Alignment file")

    parser.add_argument("output_mutations", help="Output file for mutations")
    parser.add_argument("output_haplotypes", help="Output file for haplotypes")

    parser.add_argument(
        "--quality-threshold", type=int, default=47, help="Quality threshold"
    )
    parser.add_argument(
        "--length-threshold", type=int, default=100, help="Length threshold"
    )

    parser.add_argument("--log-file", help="Log file")

    main(parser.parse_args())
