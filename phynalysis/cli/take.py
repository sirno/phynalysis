"""Take subcommand."""

import pandas as pd

__all__ = ["take_cmd", "take"]


def take(data: pd.DataFrame, n_samples: int) -> pd.DataFrame:
    if n_samples == 0:
        return data

    return data.sample(n=n_samples)


def take_cmd(args):
    """Take command main function."""
    data = pd.read_csv(args.input)

    data = take(data, args.n_samples)

    data.to_csv(args.output, index=False)
