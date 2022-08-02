"""Collection of functions for phynalysis."""
import numpy as np
import pandas as pd


def haplotype_to_mutations(haplotype: str):
    """Get the mutations in a haplotype."""
    if haplotype == "consensus":
        return []
    mutation_strings = haplotype.split(";")
    mutations = []
    for mutation in mutation_strings:
        split = mutation.split(":")
        mutations.append((int(split[0]), split[1]))
    return mutations


def changes_from_read(reference, seq_id, read, length_threshold):
    changes = []
    if length_threshold >= 0 and abs(len(read.seq) - len(reference)) > length_threshold:
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


def changes_from_alignment(reference, alignment, quality_threshold, length_threshold):
    """Retrieve all changes in an alignment."""
    changes = []
    for seq_id, read in enumerate(alignment):
        changes += changes_from_read(reference, seq_id, read, length_threshold)

    df = pd.DataFrame(changes, columns=["seq_id", "position", "mutation", "quality"])
    n_seq = seq_id

    if quality_threshold > 0:
        return df[df["quality"] > quality_threshold], n_seq

    return df, n_seq
