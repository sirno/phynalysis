"""Collection of functions for phynalysis."""
import pysam
import numpy as np
import pandas as pd


def print_alignment(read, reference):
    """Print the alignment of a read to a reference."""
    read_pos = 0
    ref_pos = read.reference_start
    aligned = ["", "", ""]
    for c in read.cigar:
        if c[0] == 7:  # match
            aligned[0] += reference[ref_pos : ref_pos + c[1]]
            aligned[2] += read.seq[read_pos : read_pos + c[1]]
            aligned[1] += "|" * c[1]
            read_pos += c[1]
            ref_pos += c[1]
        elif c[0] == 8:  # mismatch
            qs = read.get_forward_qualities()[read_pos : read_pos + c[1]]
            ref_here = reference[ref_pos : ref_pos + c[1]]
            read_here = read.seq[read_pos : read_pos + c[1]]
            position = ref_pos
            read_pos += c[1]
            ref_pos += c[1]
            aligned[0] += ref_here
            aligned[2] += read_here
            aligned[1] += "x" * c[1]
        elif c[0] == 2:  # deletion
            aligned[0] += reference[ref_pos : ref_pos + c[1]]
            aligned[2] += "-" * c[1]
            aligned[1] += " " * c[1]
            ref_pos += c[1]
        elif c[0] == 1:  # insertion
            qs = read.get_forward_qualities()[read_pos]
            aligned[2] += read.seq[read_pos : read_pos + c[1]]
            aligned[0] += "-" * c[1]
            aligned[1] += " " * c[1]
            read_pos += c[1]
        elif c[0] == 4:  # soft clipping
            read_pos += c[1]
        else:
            print(c[0])

    step = 60
    for i in range(0, len(aligned[0]), step):
        for a in aligned:
            print("".join(a[i : i + step]))
        print()


def get_changes(reference, alignment, quality_threshold, length_threshold):
    """Get the changes in a bam file."""
    changes = []
    for seq_id, read in enumerate(alignment):
        if abs(len(read.seq) - len(reference)) > length_threshold:
            continue
        read_pos = 0
        ref_pos = read.reference_start
        for c in read.cigar:
            if c[0] == 7:  # match
                read_pos += c[1]
                ref_pos += c[1]
            elif c[0] == 8:  # mismatch
                qs = read.get_forward_qualities()[read_pos : read_pos + c[1]]
                ref_here = reference[ref_pos : ref_pos + c[1]]
                read_here = read.seq[read_pos : read_pos + c[1]]
                position = ref_pos
                read_pos += c[1]
                ref_pos += c[1]
                for mismatch in range(c[1]):
                    if ref_here[mismatch] != read_here[mismatch]:
                        changes.append(
                            [
                                seq_id,
                                position + mismatch,
                                ref_here[mismatch] + "->" + read_here[mismatch],
                                qs[mismatch],
                            ]
                        )
            elif c[0] == 2:  # deletion
                changes.append([seq_id, ref_pos, "del" + str(c[1]), 0])
                ref_pos += c[1]
            elif c[0] == 1:  # insertion
                qs = read.get_forward_qualities()[read_pos : read_pos + c[1]]
                insertion = read.seq[read_pos : read_pos + c[1]]
                changes.append([seq_id, ref_pos, "i" + insertion, np.mean(qs)])
                read_pos += c[1]
            elif c[0] == 4:  # soft clipping
                read_pos += c[1]
            else:
                raise IndexError(f"Unknown cigar operation: {c[0]}")

    changes = pd.DataFrame(
        changes, columns=["seq_id", "position", "mutation", "quality"]
    )
    n_seq = seq_id
    changes_qc = changes[changes["quality"] > quality_threshold]
    return changes_qc, n_seq
