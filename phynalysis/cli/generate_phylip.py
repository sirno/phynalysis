"""Transform haplotype data to alignment format."""

import argparse
import logging

import pandas as pd

from ..transform import haplotypes_to_phylip


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

    if args.filter_insertions:
        haplotype_data = haplotype_data[not haplotype_data.haplotype.str.contains("i")]

    haplotype_groups = haplotypes_data.groupby("haplotype")
    logging.info("Loaded %s haplotypes.", len(haplotype_groups))

    haplotype_counts = haplotype_groups["count"].sum()
    ids = haplotype_groups.apply(lambda group: group.name)
    haplotypes = haplotype_groups.apply(lambda group: group.name)

    df = pd.DataFrame({"id": ids, "haplotype": haplotypes, "count": haplotype_counts})

    if args.n_samples:
        # sample but ensure that consensus is always included
        df = pd.concat(
            [
                df[df.haplotype == "consensus"],
                df[df.haplotype != "consensus"].sample(
                    args.n_samples, weights="count", random_state=args.random_state
                ),
            ]
        )

    sequences_lip = haplotypes_to_phylip(reference, df["haplotype"])

    logging.info("Converted %s sequences.", len(sequences_lip))

    longest_haplotype = max(map(len, ids))
    with open(args.output, "w", encoding="utf8") as file_descriptor:
        file_descriptor.write(f"{len(df['id'])} {len(sequences_lip[0])}\n")
        for name, sequence in zip(df["id"], sequences_lip):
            name = name.replace(":", "|").replace(";", ".").ljust(longest_haplotype)
            file_descriptor.write(f"{name} {sequence}\n")


def entry():
    """Entry."""
    parser = argparse.ArgumentParser(
        description="Transform haplotype data to alignment format."
    )
    parser.add_argument("input", type=str, help="Input file.")
    parser.add_argument("reference", type=str, help="Reference file.")
    parser.add_argument("output", type=str, help="Output file.")

    parser.add_argument("--n-samples", type=int, default=0, help="Number of samples.")
    parser.add_argument("--random-state", type=int, default=42, help="Random state.")
    parser.add_argument(
        "--filter-insertions", action="store_true", help="Filter insertions."
    )

    parser.add_argument("--log-file", type=str, help="Log file.")

    main(parser.parse_args())
