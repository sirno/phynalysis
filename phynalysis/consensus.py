"""Compute consensus sequence.

Compute the consensus sequence of a given aligned .bam file, and write it to a
target file.

Additionally, print summary statistics of the alignment to stdout.

Original Author: Eva Bons

Usage: python consensus.py [alignment.bam] [reference.fasta] [consensus.fasta]
"""
import argparse

import pysam
import pandas as pd
import numpy as np


def main(args):
    """Main."""
    alignment = pysam.AlignmentFile(args.alignment, "rb", check_sq=False)
    with open(args.reference, "r") as file_descriptor:
        reference = "".join(file_descriptor.readlines()[1:])

    seq_id = 0
    changes = []

    print("Computing consensus sequence...")

    # collect all the changes
    for seq_id, read in enumerate(alignment):
        read_pos = 0
        ref_pos = read.reference_start
        for change in read.cigar:
            if change[0] == 7:  # match
                read_pos += change[1]
                ref_pos += change[1]
            elif change[0] == 8:  # mismatch
                qs = read.get_forward_qualities()[read_pos : read_pos + change[1]]
                ref_here = reference[ref_pos : ref_pos + change[1]]
                read_here = read.seq[read_pos : read_pos + change[1]]
                position = ref_pos
                read_pos += change[1]
                ref_pos += change[1]
                for mismatch in range(change[1]):
                    changes.append(
                        [
                            seq_id,
                            position + mismatch,
                            ref_here[mismatch] + "->" + read_here[mismatch],
                            qs[mismatch],
                        ]
                    )
            elif change[0] == 2:  # deletion
                position = ref_pos
                ref_pos += change[1]
                changes.append([seq_id, position, "del" + str(change[1]), 0])
            elif change[0] == 1:  # insertion
                position = ref_pos
                qs = read.get_forward_qualities()[read_pos : read_pos + change[1]]
                insertion = read.seq[read_pos : read_pos + change[1]]
                read_pos += change[1]
                changes.append([seq_id, position, "i" + insertion, np.mean(qs)])
            elif change[0] == 4:  # soft clipping
                read_pos += change[1]
            else:
                raise IndexError(f"Cigar operation '{change[0]}' not implemented.")

    changes = pd.DataFrame(
        changes, columns=["seq_id", "position", "mutation", "quality"]
    )
    n_seq = seq_id

    print(f"Found {len(changes)} mutations in {n_seq} sequences.")

    # Apply quality control
    mistakes_allowed_per_genome = 0.1
    p = mistakes_allowed_per_genome / len(reference)
    quality_threshold = -10 * np.log10(p)

    changes_qc = changes[changes["quality"] > quality_threshold]
    print(f"Found {len(changes_qc)} mutations with quality > {quality_threshold}.")

    # Get the majority changes
    per_mut = changes_qc.groupby(["position", "mutation"], as_index=False).count()
    majority_changes = per_mut[per_mut.seq_id / n_seq > 0.5]
    print(f"Found {len(majority_changes)} majority changes.")

    # Create the consensus sequence
    consensus = [i for i in reference]
    for _index, mutation in majority_changes.iterrows():
        if "->" in mutation.mutation:
            print(f"{mutation.position}: {mutation.mutation}")
            consensus[mutation.position] = mutation.mutation[-1]
        else:
            raise NotImplementedError(
                "anything else than point-mutations currently not implemented"
            )

    consensus = "".join(consensus)
    with open(args.consensus, "w", encoding="utf8") as file_descriptor:
        file_descriptor.write(f"> consensus of {args.consensus}\n{consensus}")
    print(f"Consensus sequence written to {args.consensus}.")


def entry():
    """Entry."""
    parser = argparse.ArgumentParser(description="Compute consensus sequence.")
    parser.add_argument("--log", default="INFO")
    parser.add_argument("alignment", type=str, help="Alignment file.")
    parser.add_argument("reference", type=str, help="Reference file.")
    parser.add_argument("consensus", type=str, help="Consensus file (output).")

    main(parser.parse_args())
