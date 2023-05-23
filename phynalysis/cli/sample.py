"""Sample subcommand."""

import pandas as pd


def sample_balance(data, args):
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

    data.to_csv(args.output, index=False)


def sample_unique(data, args):
    """Sample unique haplotypes."""
    unique_haplotypes = data.groupby("haplotype")
    haplotype_sample = (
        unique_haplotypes["count"]
        .sum()
        .reset_index()
        .sample(
            args.n_samples,
            weights="count",
            random_state=args.random_state,
            replace=args.replace_samples,
        )
        .haplotype.to_frame()
    )

    data = pd.merge(data, haplotype_sample, on="haplotype")
    data = data.groupby("haplotype", group_keys=False).first().reset_index()

    data.to_csv(args.output, index=False)


def sample_random(data, args):
    data = data.sample(
        args.n_samples,
        weights="count",
        random_state=args.random_state,
        replace=args.replace_samples,
    )
    data.to_csv(args.output, index=False)


def sample(args):
    """Sample command main function."""
    data = pd.read_csv(args.input)

    if args.n_samples == 0:
        data.to_csv(args.output, index=False)
        return

    match args.mode:
        case "random":
            sample_random(data, args)
        case "unique":
            sample_unique(data, args)
        case "balance":
            sample_balance(data, args)
