from collections import defaultdict
from typing import Callable, Any

import pandas as pd

from .transform import haplotype_to_list

__all__ = ["mutations_from_haplotypes"]


def mutations_from_haplotypes(
    data: pd.DataFrame,
    index_map: Callable[[str], Any] = None,
) -> pd.DataFrame:
    """Compute mutations from haplotypes."""
    experiments = defaultdict(lambda: defaultdict(int))
    for idx, row in data.iterrows():
        sample_name, haplotype = idx
        if index_map is not None:
            sample_name = index_map(sample_name)
        mutations = haplotype_to_list(haplotype)
        for mutation in mutations:
            experiments[sample_name][mutation] += int(row["count"])

    df = pd.DataFrame.from_dict(experiments)
    df.index.names = ["position", "mutation"]
    return df
