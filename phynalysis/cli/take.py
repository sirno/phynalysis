"""Take subcommand."""

import pandas as pd


def take(args):
    """Take command main function."""

    data = pd.read_csv(args.input)

    if args.n_samples == 0:
        data.to_csv(args.output, index=False)
        return

    data = data.nlargest(args.n_samples, "count").sort_index()

    data.to_csv(args.output, index=False)
