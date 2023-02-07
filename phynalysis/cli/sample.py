"""Sample subcommand."""

import pandas as pd


def sample(args):
    """Sample command main function."""
    data = pd.read_csv(args.input)

    if args.n_samples:
        if args.balance_groups is not None:
            total_weights = sum(args.balance_groups.values())
            groups = data.groupby(args.balance_groups.keys())
            data = groups.apply(
                lambda group: group.sample(
                    args.n_samples * args.balance_groups[group] // total_weights,
                    weights="count",
                    replace=args.replace_samples,
                    random_state=args.random_state,
                )
            )
            data = groups.sample(
                n=args.n_samples // len(groups), replace=args.replace_samples
            )
        else:
            data = data.sample(
                args.n_samples,
                weights="count",
                random_state=args.random_state,
                replace=args.replace_samples,
            )

    data.to_csv(args.output, index=False)
