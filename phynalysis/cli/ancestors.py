"""Main module."""
import argparse

import pandas as pd

from tqdm import tqdm

from ..transform import haplotype_to_set, haplotype_to_string


def _haplotype_distance(haplotype1, haplotype2):
    """Calculate distance between two haplotypes."""
    return len(haplotype1 ^ haplotype2)


def _find_ancestor(descendant, ancestors):
    """Find ancestor of descendants"""
    distances = ancestors.apply(
        lambda haplotype: _haplotype_distance(haplotype, descendant)
    )
    return ancestors.iloc[distances.idxmin()]


def ancestors(args):
    """Main."""
    data = pd.read_csv(args.input)
    ancestors = data[data.time == 0]
    descendants = data[data.time > 0]

    ancestor_haplotypes = ancestors.haplotype.apply(haplotype_to_set)
    descendant_haplotypes = descendants.haplotype.apply(haplotype_to_set)

    tqdm.pandas()
    descendant_ancestors = descendant_haplotypes.progress_apply(
        lambda h: haplotype_to_string(_find_ancestor(h, ancestor_haplotypes))
    )
    data["closest_ancestor"] = descendant_ancestors
    data.to_csv(args.output, index=False)
