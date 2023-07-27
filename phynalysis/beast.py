"""Beast analysis module."""

import logging
import re
import math
from collections import Counter
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
from Bio import Phylo

__all__ = [
    "read_beast_log",
    "plot_rate_matrix",
    "plot_topology",
    "compute_ess",
    "count_clade_types",
]


def read_beast_log(log_file: Union[str, Path], burn_in: Union[int, float] = 0):
    """Read BEAST2 log file and return pandas dataframe."""
    data = pd.read_csv(log_file, sep="\t", comment="#")

    # Remove burn-in
    if isinstance(burn_in, float):
        burn_in = int(burn_in * len(data))
    data = data.iloc[burn_in:]

    return data


def _extract_mean_rates(log_data: pd.DataFrame) -> pd.DataFrame:
    """Extract mean rates from log data."""
    mean_rates = log_data.filter(regex="migration_model\.rateMatrix_").mean()
    indices = mean_rates.index.str.extract(
        r"migration_model\.rateMatrix_(?P<source>\d+)_(?P<target>\d+)"
    )

    return pd.concat([indices, mean_rates.reset_index(name="mean")], axis=1)


def plot_rate_matrix(log_data: pd.DataFrame):
    """Plot heatmap of the rate matrix."""
    try:
        from matplotlib.pyplot import show
        from seaborn import heatmap
    except ImportError:
        ImportError(
            "Seaborn and matplotlib are required to use this function."
            "Install them with `pip install phynalysis[beast]`."
        )

    mean_rates = _extract_mean_rates(log_data)
    mean_rate_matrix = mean_rates.pivot("source", "target", "mean")

    heatmap(mean_rate_matrix, annot=True, fmt=".2f", cmap="YlGn")
    show()


def plot_topology(log_data: pd.DataFrame, ax=None):
    """Plot type topology."""
    try:
        from networkx import (
            MultiDiGraph,
            draw,
            get_edge_attributes,
            get_node_attributes,
        )
    except ImportError:
        raise ImportError(
            "NetworkX is required to use this function."
            "Install it with `pip install phynalysis[beast]`."
        )

    mean_rates = _extract_mean_rates(log_data)

    graph = MultiDiGraph()
    n_nodes = len(mean_rates.source.unique())
    for idx, label in enumerate(mean_rates.source.unique()):
        graph.add_node(
            label,
            label=label,
            pos=(
                -math.sin(idx / n_nodes * 2 * math.pi),
                math.cos(idx / n_nodes * 2 * math.pi),
            ),
        )

    for _, e in mean_rates.iterrows():
        graph.add_edge(e.source, e.target, width=e["mean"])

    width = get_edge_attributes(graph, "width").values()
    positions = get_node_attributes(graph, "pos")

    draw(
        graph,
        positions,
        with_labels=True,
        connectionstyle="arc3, rad = 0.1",
        width=list(width),
        min_source_margin=10,
        min_target_margin=10,
        ax=ax,
    )


def compute_ess(log_data: np.ndarray):
    """Compute effective sample size."""
    try:
        from mcmc_diagnostics import estimate_ess
    except ImportError:
        raise ImportError(
            "mcmc_diagnostics is required to use this function."
            "Install it with `pip install mcmc_diagnostics`."
        )

    def estimate_ess_wrapper(x):
        try:
            return estimate_ess(np.array(x), axis=0)
        except np.linalg.LinAlgError:
            return np.nan

    return log_data.astype("float").apply(estimate_ess_wrapper, raw=False, axis=0)


def count_clade_types(trees_file: Union[str, Path]):
    """Read BEAST2 trees file and return clade type counts."""
    if not trees_file.endswith(".nwk"):
        logging.warning("Trees file should be in Newick format.")

    pattern = re.compile('&type="(?P<type>\d+)"')
    trees = Phylo.parse(trees_file, "newick")
    type_counts = pd.DataFrame()

    for tree in trees:
        clades = tree.find_clades()
        counter = Counter(
            [int(pattern.search(clade.comment).group("type")) for clade in clades]
        )
        type_counts = type_counts.append(counter, ignore_index=True)
        print(counter)

    return type_counts
