"""Filter subcommand.

Filter haplotypes data based on condition.
"""

import pandas as pd


__all__ = ["filter_cmd", "filter"]


def filter(frame: pd.DataFrame, query: str, filter_insertions: bool) -> pd.DataFrame:
    """Filter haplotypes data based on condition."""
    if query:
        frame = frame.query(query)

    if filter_insertions:
        insertions = frame.haplotype.str.contains("i").fillna(False)
        frame = frame[~insertions]

    return frame


def filter_cmd(args):
    """Filter command main function."""
    haplotypes_data = pd.read_csv(args.input)

    haplotypes_data = filter(haplotypes_data, args.query, args.filter_insertions)

    haplotypes_data.to_csv(args.output, index=False)
