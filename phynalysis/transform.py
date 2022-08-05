"""Common transformations for haplotypes and populations."""

import pandas as pd

from tqdm import tqdm


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


def haplotype_to_set(haplotype):
    """Convert haplotype to list."""
    if haplotype == "consensus":
        return set()

    changes = [changes.split(":") for changes in haplotype.split(";")]
    return set([(int(change[0]), change[1]) for change in changes])


def set_to_haplotype(set_):
    """Convert a set of mutations to a haplotype."""
    if not set_:
        return "consensus"
    return ";".join(f"{pos}:{mutation}" for pos, mutation in set_)


def haplotypes_to_phylip(reference, haplotypes, ids):
    """Convert haplotypes to phylip format."""
    if len(haplotypes) != len(ids):
        raise ValueError("Number of haplotypes and ids must match.")

    sequences = []
    for haplotype in tqdm(haplotypes, desc="haplotype_parsing"):
        # discard haplotypes with insertions
        sequence = list(reference)
        for change in haplotype.split(";"):
            if change == "consensus":
                break
            split = change.split(":")
            position = int(split[0])
            mutation = split[1]
            if "->" in mutation:
                sequence[position] = mutation[-1]
            elif mutation.startswith("i"):
                sequence[position] += mutation[1:]
            else:
                NotImplementedError(f"Unknown mutation type {mutation}.")
        if sequence:
            sequences.append(sequence)

    df = pd.DataFrame({"id": ids, "sequence": sequences})

    longest = [
        max(map(len, [s[i] for s in df.sequence]))
        for i in tqdm(range(len(reference)), desc="gap_detection")
    ]
    sequences_lip = [
        "".join([s.ljust(l, "-") for s, l in zip(s, longest)])
        for s in tqdm(df.sequence, desc="gap_inclusion")
    ]

    return sequences_lip
