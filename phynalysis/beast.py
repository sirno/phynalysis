"""Beast analysis module."""

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
