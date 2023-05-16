"""Export data to npy format."""

import yaml

import numpy as np
import pandas as pd

from ..transform import haplotypes_to_frequencies


def _filter_haplotypes(haplotypes: pd.DataFrame, time: int, compartment: int):
    return haplotypes.query(f"time == {time} and compartment == {compartment}")


def _sort_haplotypes(haplotypes: pd.DataFrame):
    return (
        haplotypes.join(
            haplotypes.groupby("haplotype").size().rename("count"), on="haplotype"
        )
        .sort_values("count", ascending=False)
        .haplotype.values
    )


def _get_sorted_haplotypes(haplotypes, time, compartment):
    filtered = _filter_haplotypes(haplotypes, time, compartment)
    return _sort_haplotypes(filtered["haplotypes"].reset_index(drop=True))


def _get_frequencies(reference: str, haplotypes: pd.DataFrame):
    return np.array(
        [
            [
                haplotypes_to_frequencies(
                    reference, _get_sorted_haplotypes(haplotypes, time, compartment)
                )
                for time in haplotypes.time.unique()
            ]
            for compartment in haplotypes.compartment.unique()
        ]
    )


def write_npy(path, data, reference, template=None):
    """Write labeled data file.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to the output file.
    data : pandas.DataFrame
        Dataframe with columns "haplotype" and "id".
    reference : str
        Reference sequence.
    template : str
        Template for labeled data should be a yaml file with the label as key. (This
        is technically not a template)
    """
    if template is None:
        raise ValueError(
            "Template argument missing. For npy export, the template should contain a list of labels."
        )

    if not "haplotype" in data.columns:
        raise ValueError("Dataframe must contain column 'haplotype'.")

    if not "time" in data.columns:
        raise ValueError("Dataframe must contain column 'time'.")

    if not "compartment" in data.columns:
        raise ValueError("Dataframe must contain column 'compartment'.")

    input = _get_frequencies(reference, data)
    output = np.load(template)

    np.savez(path, input=input, output=output)
