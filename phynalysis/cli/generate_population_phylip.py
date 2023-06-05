import argparse
import logging

import pandas as pd

from ..transform import haplotype_to_dict, haplotypes_to_matrix


def changes_from_haplotypes(haplotypes):
    """Retrieve all changes in haplotypes."""
    changes = []
    for haplotype in haplotypes:
        mutations = haplotype_to_dict(haplotype)
        for position, mutation in mutations:
            changes.append([position, mutation])
    return pd.DataFrame(changes, columns=["position", "mutation"]).sort_values(
        "position", ascending=False
    )


def merge_haplotypes(haplotypes):
    """Merge haplotypes into haplotype."""
    haplotypes = haplotypes.sample(10, weights="count")
    changes = changes_from_haplotypes(haplotypes.haplotype)
    haplotype = ";".join(
        [f"{change.position}:{change.mutation}" for _, change in changes.iterrows()]
    )
    return haplotype


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

    sample_groups = haplotypes_data.groupby("barcode")
    merged_haplotypes = sample_groups.apply(merge_haplotypes)
    sequences_matrix = haplotypes_to_matrix(reference, merged_haplotypes.values)

    ids = merged_haplotypes.index
    longest_haplotype = max(map(len, ids))
    with open(args.output, "w", encoding="utf8") as file_descriptor:
        file_descriptor.write(f"{len(ids)} {len(sequences_matrix[0])}\n")
        for name, sequence in zip(ids, sequences_matrix):
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
    parser.add_argument(
        "--filter-insertions", action="store_true", help="Filter insertions."
    )

    parser.add_argument("--log-file", type=str, help="Log file.")

    main(parser.parse_args())
