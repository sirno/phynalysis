"""Transform haplotype data to alignment format."""

import argparse

import pandas as pd
import numpy as np

from tqdm import tqdm


def main(args):
    """Main."""
    haplotypes = pd.read_csv(args.input)
    with open(args.reference, "r", encoding="utf8") as file_descriptor:
        reference = "".join(file_descriptor.read().splitlines()[1:])

    sequences = []
    for haplotype, haplotype_data in haplotypes.groupby("haplotype"):
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
        sequences.append(sequence)

    sequences_lip = np.empty(len(sequences), dtype=np.string_)
    for i in tqdm(range(len(reference))):
        at_position = [s[i] for s in sequences]
        longest = max(map(lambda x: len(x), at_position))
        strings_at_position = np.array([s.ljust(longest, "-") for s in at_position])
        sequences_lip = np.char.add(sequences_lip, strings_at_position)

    print(sequences_lip)


def entry():
    """Entry."""
    parser = argparse.ArgumentParser(
        description="Transform haplotype data to alignment format."
    )
    parser.add_argument("--input", type=str, help="Input file.")
    parser.add_argument("--reference", type=str, help="Reference file.")
    parser.add_argument("--log", default="INFO")

    _args = parser.parse_args()

    main(_args)
