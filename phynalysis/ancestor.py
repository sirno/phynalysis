"""Main module."""
import argparse

import pandas as pd


def haplotype_to_set(haplotype):
    """Convert haplotype to list."""
    changes = [changes.split(":") for changes in haplotype.split(";")]
    return set([(int(change[0]), change[1]) for change in changes])


def haplotype_distance(haplotype1, haplotype2):
    """Calculate distance between two haplotypes."""
    return len(haplotype1 ^ haplotype2)


def find_ancestor(ancestors, descendant):
    """Find ancestor of descendants"""
    distances = ancestors.apply(
        lambda row: haplotype_distance(row.haplotype, descendant), axis=1
    )
    print(distances)


def main(args):
    """Main."""
    ancestors = pd.read_csv(args.ancestors)
    descendants = pd.read_csv(args.descendants)

    ancestor_haplotypes = ancestors.haplotype.apply(haplotype_to_set)
    descendant_haplotypes = descendants.haplotype.apply(haplotype_to_set)

    find_ancestor(ancestor_haplotypes, descendant_haplotype[0])


def entry():
    """Entry."""
    parser = argparse.ArgumentParser(description="")

    parser.add_argument("--ancestors", type=str, help="Ancestors file.")
    parser.add_argument("--descendants", type=str, help="Descendants file.")

    parser.add_argument("--log", default="INFO")

    main(parser.parse_args())
