"""Beast analysis module."""

import numpy as np
import pandas as pd

from pathlib import Path
from typing import Union


def read_beast_log(log_file: Union[str, Path], burn_in: Union[int, float] = 0):
    """Read BEAST2 log file and return pandas dataframe."""
    data = pd.read_csv(log_file, sep="\t")

    # Remove burn-in
    if isinstance(burn_in, float):
        burn_in = int(burn_in * len(data))
    data = data.iloc[burn_in:]

    return data


def plot_rate_matrix(log_data: pd.DataFrame):
    """Plot heatmap of the rate matrix."""
    try:
        from seaborn import heatmap
        from matplotlib.pyplot import show
    except ImportError:
        ImportError(
            "Seaborn and matplotlib are required to use this function."
            "Install them with `pip install phynalysis[beast]`."
        )

    mean_rates = log_data.filter(regex="migration_model\.rateMatrix_").mean()
    indices = mean_rates.index.str.extract(
        r"migration_model\.rateMatrix_(?P<from>\d+)_(?P<to>\d+)"
    )
    mean_rate_matrix = pd.concat(
        [indices, mean_rates.reset_index(name="mean")], axis=1
    ).pivot(index="from", columns="to", values="mean")

    heatmap(mean_rate_matrix, annot=True, fmt=".2f", cmap="YlGn")
    show()


def compute_ess(log_data: np.ndarray):
    """Compute effective sample size."""
    try:
        from mcmc_diagnostics import estimate_ess
    except ImportError:
        raise ImportError(
            "mcmc_diagnostics is required to use this function."
            "Install it with `pip install mcmc_diagnostics`."
        )

    def wrapper(x, **kwargs):
        return estimate_ess(np.array(x), axis=-1)

    return log_data.astype("float").apply(wrapper, raw=False, axis=0)
