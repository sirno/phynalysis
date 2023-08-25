"""Sample subcommand."""

import pandas as pd
import logging

__all__ = ["sample_cmd", "sample_random", "sample_unique", "sample_balance"]


def sample_balance(
    data: pd.DataFrame,
    balance_groups: list,
    balance_weights: dict,
    n_samples: int,
    n_samples_per_group: bool,
    replace_samples: bool,
    random_state: int,
):
    """Sample data with balanced groups."""
    groups = data.groupby(balance_groups, group_keys=False)

    if n_samples_per_group:
        size = lambda group: n_samples
    elif balance_weights is None:
        size = lambda group: n_samples // len(groups)
    else:
        size = (
            lambda group: n_samples
            * balance_weights[str(group.name).replace(" ", "").strip("()")]
            // sum(balance_weights.values())
        )

    data = groups.apply(
        lambda group: group.sample(
            n=size(group),
            weights="count",
            replace=replace_samples,
            random_state=random_state,
        )
    )

    return data


def sample_unique(
    data: pd.DataFrame, n_samples: int, replace_samples: bool, random_state: int
):
    """Sample unique haplotypes."""
    unique_haplotypes = data.groupby("haplotype")
    if n_samples > len(unique_haplotypes):
        logging.warning(
            "Requested %s samples, but there are only %s unique haplotypes. Sampling all unique haplotypes.",
            n_samples,
            len(unique_haplotypes),
        )
        n_samples = len(unique_haplotypes)
    haplotype_sample = (
        unique_haplotypes["count"]
        .sum()
        .reset_index()
        .sample(
            n_samples if n_samples else len(unique_haplotypes),
            weights="count",
            random_state=random_state,
            replace=replace_samples,
        )
        .haplotype.to_frame()
    )

    data = pd.merge(data, haplotype_sample, on="haplotype")
    data = data.groupby("haplotype", group_keys=False).first().reset_index()

    return data


def sample_random(data, n_samples: int, replace_samples: bool, random_state: int):
    """Sample data randomly."""
    data = data.sample(
        n_samples,
        weights="count",
        random_state=random_state,
        replace=replace_samples,
    )

    return data


def sample_cmd(args):
    """Sample command main function."""
    data = pd.read_csv(args.input)

    if args.n_samples == 0 and args.mode != "unique":
        data.to_csv(args.output, index=False)
        return

    match args.mode:
        case "random":
            data = sample_random(
                data,
                args.n_samples,
                args.replace_samples,
                args.random_state,
            )
        case "unique":
            data = sample_unique(
                data,
                args.n_samples,
                args.replace_samples,
                args.random_state,
            )
        case "balance":
            data = sample_balance(
                data,
                args.balance_groups,
                args.balance_weights,
                args.n_samples,
                args.n_samples_per_group,
                args.replace_samples,
                args.random_state,
            )

    data.to_csv(args.output, index=False)
