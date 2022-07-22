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
import numpy as np


def get_changes_from_read(reference, seq_id, read, length_threshold):
    changes = []
    if abs(len(read.seq) - len(reference)) > length_threshold:
        return changes
    read_pos = 0
    ref_pos = read.reference_start
    for cigar in read.cigar:
        if cigar[0] == 7:  # match
            read_pos += cigar[1]
            ref_pos += cigar[1]
        elif cigar[0] == 8:  # mismatch
            qs = read.get_forward_qualities()[read_pos : read_pos + cigar[1]]
            ref_here = reference[ref_pos : ref_pos + cigar[1]]
            read_here = read.seq[read_pos : read_pos + cigar[1]]
            position = ref_pos
            read_pos += cigar[1]
            ref_pos += cigar[1]
            for mismatch in range(cigar[1]):
                if ref_here[mismatch] != read_here[mismatch]:
                    changes.append(
                        [
                            seq_id,
                            position + mismatch,
                            ref_here[mismatch] + "->" + read_here[mismatch],
                            qs[mismatch],
                        ]
                    )
        elif cigar[0] == 2:  # deletion
            changes.append([seq_id, ref_pos, "del" + str(cigar[1]), 0])
            ref_pos += cigar[1]
        elif cigar[0] == 1:  # insertion
            qs = read.get_forward_qualities()[read_pos : read_pos + cigar[1]]
            insertion = read.seq[read_pos : read_pos + cigar[1]]
            changes.append([seq_id, ref_pos, "i" + insertion, np.mean(qs)])
            read_pos += cigar[1]
        elif cigar[0] == 4:  # soft clipping
            read_pos += cigar[1]
        else:
            raise IndexError(f"Unknown cigar operation: {cigar[0]}")
    return changes


def get_changes_from_alignment(
    reference, alignment, quality_threshold, length_threshold
):
    """Retrieve all changes in an alignment."""
    changes = []
    for seq_id, read in enumerate(alignment):
        changes += get_changes_from_read(reference, seq_id, read, length_threshold)

    df = pd.DataFrame(changes, columns=["seq_id", "position", "mutation", "quality"])
    n_seq = seq_id
    changes_qc = df[df["quality"] > quality_threshold]
    return changes_qc, n_seq


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
    changes, n_seq = get_changes_from_alignment(
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
    parser.add_argument("output_haplotypes", help="Output file for mutations")

    parser.add_argument(
        "--quality-threshold", type=int, default=47, help="Quality threshold"
    )
    parser.add_argument(
        "--length-threshold", type=int, default=100, help="Length threshold"
    )

    parser.add_argument("--log-file", help="Log file")

    main(parser.parse_args())
