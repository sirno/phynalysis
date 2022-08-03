"""Transform haplotype data to alignment format."""

import argparse
import logging

import pandas as pd
import numpy as np

from tqdm import tqdm


def main(args):
    """Main."""
    logging.basicConfig(
        filename=args.log_file,
        level=logging.INFO,
        format="%(levelname)s:%(asctime)s %(message)s",
    )

    haplotypes_data = pd.read_csv(args.input)
    with open(args.reference, "r", encoding="utf8") as file_descriptor:
        reference = "".join(file_descriptor.read().splitlines()[1:])

    haplotypes = haplotypes_data.groupby("haplotype")
    logging.info("Loaded %s haplotypes.", len(haplotypes))

    ids = []
    sequences = []
    counts = []
    for haplotype, haplotype_data in tqdm(haplotypes, desc="haplotype_parsing"):
        # discard haplotypes with insertions
        if "i" in haplotype:
            continue
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
            ids.append(haplotype)
            sequences.append(sequence)
            counts.append(haplotype_data["count"].sum())

    logging.info("Parsed %s sequences.", len(sequences))

    df = pd.DataFrame({"id": ids, "sequence": sequences, "count": counts})

    if args.n_samples:
        df = df.sample(n=args.n_samples, weights="count")

    longest = [
        max(map(len, [s[i] for s in df.sequence]))
        for i in tqdm(range(len(reference)), desc="gap_detection")
    ]
    sequences_lip = [
        "".join([s.ljust(l, "-") for s, l in zip(s, longest)])
        for s in tqdm(df.sequence, desc="gap_inclusion")
    ]

    logging.info("Converted %s sequences.", len(sequences_lip))

    longest_haplotype = max(map(len, ids))
    if args.output:
        with open(args.output, "w", encoding="utf8") as file_descriptor:
            file_descriptor.write(len(ids), len(sequences_lip[0]))
            for name, sequence in zip(ids, sequences_lip):
                name = name.replace(":", "|").ljust(longest_haplotype)
                file_descriptor.write(f"{name} {sequence}")
    else:
        print(len(df), len(sequences_lip[0]))
        for name, sequence in zip(ids, sequences_lip):
            name = name.replace(":", "|").ljust(longest_haplotype)
            print(f"{name} {sequence}")


def entry():
    """Entry."""
    parser = argparse.ArgumentParser(
        description="Transform haplotype data to alignment format."
    )
    parser.add_argument("--input", type=str, help="Input file.")
    parser.add_argument("--output", type=str, help="Output file.")
    parser.add_argument("--reference", type=str, help="Reference file.")

    parser.add_argument("--n-samples", type=int, default=0, help="Number of samples.")

    parser.add_argument("--log-file", type=str, help="Log file.")

    main(parser.parse_args())
