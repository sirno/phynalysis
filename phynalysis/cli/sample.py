"""Sample subcommand."""

import pandas as pd
import sys


def balanced_sample(data, args):
    """Sample data with balanced groups."""
    groups = data.groupby(args.balance_groups, group_keys=False)

    if args.n_samples_per_group:
        size = lambda group: args.n_samples
    elif args.balance_weights is None:
        size = lambda group: args.n_samples // len(groups)
    else:
        size = (
            lambda group: args.n_samples
            * args.balance_weights[str(group.name).replace(" ", "").strip("()")]
            // sum(args.balance_weights.values())
        )

    data = groups.apply(
        lambda group: group.sample(
            n=size(group),
            weights="count",
            replace=args.replace_samples,
            random_state=args.random_state,
        )
    )

    return data


def sample(args):
    """Sample command main function."""
    data = pd.read_csv(args.input)

    if args.n_samples == 0:
        data.to_csv(args.output, index=False)
        return

    if args.balance_groups is not None:
        data = balanced_sample(data, args)
        data.to_csv(args.output, index=False)
        return

    data = data.sample(
        args.n_samples,
        weights="count",
        random_state=args.random_state,
        replace=args.replace_samples,
    )
    data.to_csv(args.output, index=False)
