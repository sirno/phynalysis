"""Transform haplotype data to alignment format."""

import argparse

import pandas as pd
import numpy as np

from tqdm import tqdm


def main(args):
    """Main."""
    haplotypes_data = pd.read_csv(args.input)
    with open(args.reference, "r", encoding="utf8") as file_descriptor:
        reference = "".join(file_descriptor.read().splitlines()[1:])

    haplotypes = haplotypes_data.groupby("haplotype")

    # sequences = np.empty(len(haplotypes), dtype=object)
    ids = []
    sequences = []
    for haplotype, _haplotype_data in tqdm(haplotypes, desc="haplotype_parsing"):
        ids.append(haplotype)
        sequence = [r for r in reference]
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
        # sequences[idx] = sequence
        sequences.append(sequence)

    longest = [
        max(map(len, [s[i] for s in sequences]))
        for i in tqdm(range(len(reference)), desc="gap_detection")
    ]
    sequences_lip = [
        "".join([s.ljust(l, "-") for s, l in zip(s, longest)])
        for s in tqdm(sequences, desc="gap_inclusion")
    ]

    longest_haplotype = max(map(len, ids))
    print(len(ids), len(sequences_lip[0]))
    for name, sequence in zip(ids, sequences_lip):
        print(f"{name.ljust(longest_haplotype)} {sequence}")


def entry():
    """Entry."""
    parser = argparse.ArgumentParser(
        description="Transform haplotype data to alignment format."
    )
    parser.add_argument("--input", type=str, help="Input file.")
    parser.add_argument("--output", type=str, help="Output file.")
    parser.add_argument("--reference", type=str, help="Reference file.")
    parser.add_argument("--log", default="INFO")

    _args = parser.parse_args()

    main(_args)
