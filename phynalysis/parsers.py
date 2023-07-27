"""Parsing functions to extract haplotypes from reads."""

import numpy as np
import pandas as pd
import pysam
import re

__all__ = [
    "changes_from_read",
    "changes_from_alignment",
]


def changes_from_read(
    reference: str,
    read: pysam.AlignedRead,
):
    """Retrieve list of changes from single read."""
    changes = []
    read_pos = 0
    ref_pos = read.reference_start
    for cigar in read.cigar:
        if cigar[0] == 7 or cigar[0] == 0:  # match
            # move both read and reference indices
            read_pos += cigar[1]
            ref_pos += cigar[1]
        elif cigar[0] == 8:  # mismatch
            position = ref_pos
            # get read and reference bases
            reference_slice = reference[ref_pos : ref_pos + cigar[1]]
            read_slice = read.seq[read_pos : read_pos + cigar[1]]

            # get quality scores
            qualities = read.get_forward_qualities()

            # slice quality array to match cigar offset length
            if qualities:
                qualities = qualities[read_pos : read_pos + cigar[1]]

            # record changes
            changes += [
                [
                    position + offset,
                    reference_slice[offset] + "->" + read_slice[offset],
                    qualities[offset] if qualities else 255,
                ]
                for offset in range(cigar[1])
                if reference_slice[offset] != read_slice[offset]
            ]

            # move both read and reference indices
            read_pos += cigar[1]
            ref_pos += cigar[1]
        elif cigar[0] == 2:  # deletion
            changes.append(
                [
                    ref_pos,
                    "del" + str(cigar[1]),
                    0,
                ]
            )

            # move reference index
            ref_pos += cigar[1]
        elif cigar[0] == 1:  # insertion
            qualities = read.get_forward_qualities()

            quality = None
            if qualities:
                quality = np.mean(qualities[read_pos : read_pos + cigar[1]])

            insertion = read.seq[read_pos : read_pos + cigar[1]]

            # record changes
            changes.append(
                [
                    ref_pos,
                    "i" + insertion,
                    quality if quality is not None else 255,
                ]
            )

            # move read index
            read_pos += cigar[1]
        elif cigar[0] == 4:  # soft clipping
            # move read index
            read_pos += cigar[1]
        else:
            raise IndexError(f"Unknown cigar operation: {cigar[0]}")
    return changes


def changes_from_alignment(
    reference: str,
    alignment: pysam.AlignmentFile,
):
    """Retrieve all changes in an alignment."""
    BLOCK_ID_REGEX = re.compile(r"block_id=(\w+);")

    changes = []
    for seq_id, read in enumerate(alignment):
        block_id_match = BLOCK_ID_REGEX.search(read.query_name)
        block_id = block_id_match.group(1) if block_id_match else None
        read_changes = changes_from_read(reference, read)
        if read_changes:
            changes += [(seq_id, block_id, changes_from_read(reference, read))]

    if not changes:
        return pd.DataFrame(
            [], columns=["seq_id", "block_id", "position", "mutation", "quality"]
        )

    # construct dataframe
    changes = pd.DataFrame(changes, columns=["seq_id", "block_id", "changes"])
    changes = changes.explode("changes").reset_index(drop=True)

    # inplace modifications
    changes[["position", "mutation", "quality"]] = [*changes["changes"]]
    changes.drop("changes", axis=1, inplace=True)

    return changes
