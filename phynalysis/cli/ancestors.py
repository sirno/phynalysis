"""Main module."""
import argparse

import pandas as pd

from tqdm import tqdm

from ..transform import haplotype_to_set, set_to_haplotype


def haplotype_distance(haplotype1, haplotype2):
    """Calculate distance between two haplotypes."""
    return len(haplotype1 ^ haplotype2)


def find_ancestor(descendant, ancestors):
    """Find ancestor of descendants"""
    distances = ancestors.apply(
        lambda haplotype: haplotype_distance(haplotype, descendant)
    )
    return ancestors.iloc[distances.idxmin()]


def main(args):
    """Main."""
    data = pd.read_csv(args.input)
    ancestors = data[data.time == 0]
    descendants = data[data.time > 0]

    ancestor_haplotypes = ancestors.haplotype.apply(haplotype_to_set)
    descendant_haplotypes = descendants.haplotype.apply(haplotype_to_set)

    tqdm.pandas()
    descendant_ancestors = descendant_haplotypes.progress_apply(
        lambda h: set_to_haplotype(find_ancestor(h, ancestor_haplotypes))
    )
    data["closest_ancestor"] = descendant_ancestors
    data.to_csv(args.output, index=False)


def entry():
    """Entry."""
    parser = argparse.ArgumentParser(description="")

    parser.add_argument("input", type=str, help="Input file.")
    parser.add_argument("output", type=str, help="Output file.")

    parser.add_argument("--log", default="INFO")

    main(parser.parse_args())
