"""Rescale data columns."""

import pandas as pd


def rescale(data: pd.DataFrame, columns: list) -> pd.DataFrame:
    """Rescale data columns."""
    for column in columns:
        data[column] = data[column] / data[column].max()

    return data


def rescale_cmd(args):
    """Rescale command main function."""

    data = pd.read_csv(args.input)

    data = rescale(data, args.columns)

    data.to_csv(args.output, index=False)
