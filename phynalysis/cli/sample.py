"""Sample subcommand."""

import pandas as pd


def sample(args):
    """Sample command main function."""
    data = pd.read_csv(args.input)

    if args.n_samples:
        data = data.sample(
            args.n_samples,
            weights="count",
            random_state=args.random_state,
            replace=args.replace_samples,
        )

    data.to_csv(args.output, index=False)
