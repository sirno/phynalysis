"""Filter subcommand.

Filter haplotypes data based on condition.
"""

import pandas as pd

from .utils import write


def filter(args):
    """Filter command main function."""
    haplotypes_data = pd.read_csv(args.input)
    haplotypes_data = haplotypes_data.query(args.query)
    haplotypes_data.to_csv(args.output, index=False)
