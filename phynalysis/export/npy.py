"""Export data to npy format."""

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
    return _sort_haplotypes(filtered)


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


def _load_mfed_ratios(template):
    weights = template.simulation_parameters[0]["fitness_model"]["distribution"].weights

    return np.array(
        [
            weights["neutral"],
            weights["beneficial"],
            weights["deleterious"],
            weights["lethal"],
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
    input = _get_frequencies(reference, data)
    output = _load_mfed_ratios(template)

    np.savez(path, input=input, output=output)
