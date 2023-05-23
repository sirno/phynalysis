"""Rescale data columns."""

import pandas as pd


def rescale(args):
    """Rescale command main function."""

    data = pd.read_csv(args.input)

    for column in args.columns:
        data[column] = data[column] / data[column].max()
