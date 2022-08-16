"""Consensus subcommand.

Compute the consensus sequence of a given aligned .bam file, and write it to a
target file.

Additionally, print summary statistics of the alignment to log file.

Original Author: Eva Bons
"""
import logging

import pysam
import numpy as np

from ..parsers import changes_from_alignment


def consensus(args):
    """Consensus command main function."""
    alignment = pysam.AlignmentFile(args.alignment, "rb", check_sq=False)
    with open(args.reference, "r", encoding="utf8") as file_descriptor:
        reference = "".join(file_descriptor.read().splitlines()[1:])

    changes, n_seq = changes_from_alignment(reference, alignment, 0, -1)

    logging.info(f"Found {len(changes)} mutations in {n_seq} sequences.")

    # Apply quality control
    mistakes_allowed_per_genome = 0.1
    p = mistakes_allowed_per_genome / len(reference)
    quality_threshold = -10 * np.log10(p)

    changes_qc = changes[changes["quality"] > quality_threshold]
    logging.info(
        f"Found {len(changes_qc)} mutations with quality > {quality_threshold}."
    )

    # Get the majority changes
    per_mut = changes_qc.groupby(["position", "mutation"], as_index=False).count()
    majority_changes = per_mut[per_mut.seq_id / n_seq > 0.5]
    logging.info(f"Found {len(majority_changes)} majority changes.")

    # Create the consensus sequence
    consensus = [i for i in reference]
    for _index, mutation in majority_changes.iterrows():
        if "->" in mutation.mutation:
            logging.info(f"{mutation.position}: {mutation.mutation}")
            consensus[mutation.position] = mutation.mutation[-1]
        else:
            raise NotImplementedError(
                "anything else than point-mutations currently not implemented"
            )

    consensus = "".join(consensus)
    with open(args.consensus, "w", encoding="utf8") as file_descriptor:
        file_descriptor.write(f"> consensus of {args.consensus}\n{consensus}")
    logging.info(f"Consensus sequence written to {args.consensus}.")
