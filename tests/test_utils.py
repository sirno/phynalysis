import pandas as pd
import numpy as np
from phynalysis.utils import (
    compute_haplotype_frequency,
    filter_haplotype_counts,
    filter_haplotype_frequency,
)


def test_compute_haplotype_frequency_single_sample_single_haplotype():
    data = pd.DataFrame({"sample_name": ["sample1"], "haplotype": ["A"], "count": [10]})
    data.set_index(["sample_name", "haplotype"], inplace=True)
    expected_output = pd.Series(
        [1.0],
        index=pd.MultiIndex.from_tuples(
            [("sample1", "A")],
            names=["sample_name", "haplotype"],
        ),
        name="count",
    )
    pd.testing.assert_series_equal(compute_haplotype_frequency(data), expected_output)


def test_compute_haplotype_frequency_single_sample_multiple_haplotypes():
    data = pd.DataFrame(
        {
            "sample_name": ["sample1", "sample1"],
            "haplotype": ["A", "B"],
            "count": [10, 20],
        }
    )
    data.set_index(["sample_name", "haplotype"], inplace=True)
    expected_output = pd.Series(
        [0.333333, 0.666667],
        index=pd.MultiIndex.from_tuples(
            [("sample1", "A"), ("sample1", "B")],
            names=["sample_name", "haplotype"],
        ),
        name="count",
    )
    pd.testing.assert_series_equal(compute_haplotype_frequency(data), expected_output)


def test_compute_haplotype_frequency_multiple_samples_single_haplotype():
    data = pd.DataFrame(
        {
            "sample_name": ["sample1", "sample2"],
            "haplotype": ["A", "A"],
            "count": [10, 20],
        }
    )
    data.set_index(["sample_name", "haplotype"], inplace=True)
    expected_output = pd.Series(
        [1.0, 1.0],
        index=pd.MultiIndex.from_tuples(
            [("sample1", "A"), ("sample2", "A")],
            names=["sample_name", "haplotype"],
        ),
        name="count",
    )
    pd.testing.assert_series_equal(compute_haplotype_frequency(data), expected_output)


def test_compute_haplotype_frequency_multiple_samples_multiple_haplotypes():
    data = pd.DataFrame(
        {
            "sample_name": ["sample1", "sample1", "sample2", "sample2"],
            "haplotype": ["A", "B", "A", "B"],
            "count": [10, 20, 30, 40],
        }
    )
    data.set_index(["sample_name", "haplotype"], inplace=True)
    expected_output = pd.Series(
        [0.333333, 0.666667, 0.428571, 0.571429],
        index=pd.MultiIndex.from_tuples(
            [("sample1", "A"), ("sample1", "B"), ("sample2", "A"), ("sample2", "B")],
            names=["sample_name", "haplotype"],
        ),
        name="count",
    )
    pd.testing.assert_series_equal(compute_haplotype_frequency(data), expected_output)


def test_filter_haplotype_counts_no_filter():
    data = pd.DataFrame(
        {
            "sample_name": ["sample1", "sample1", "sample2", "sample2"],
            "haplotype": ["A", "B", "A", "B"],
            "count": [10, 20, 30, 40],
        }
    )
    expected_output = data.copy()
    pd.testing.assert_frame_equal(filter_haplotype_counts(data, 0), expected_output)


def test_filter_haplotype_counts_filter():
    data = pd.DataFrame(
        {
            "sample_name": ["sample1", "sample1", "sample2", "sample2"],
            "haplotype": ["A", "B", "A", "B"],
            "count": [10, 20, 30, 40],
        }
    )
    expected_output = pd.DataFrame(
        {
            "sample_name": ["sample1", "sample2", "sample2"],
            "haplotype": ["B", "A", "B"],
            "count": [20, 30, 40],
        },
        index=[1, 2, 3],
    )
    pd.testing.assert_frame_equal(filter_haplotype_counts(data, 20), expected_output)


def test_filter_haplotype_frequency_no_filter():
    data = pd.DataFrame(
        {
            "sample_name": ["sample1", "sample1", "sample2", "sample2"],
            "haplotype": ["A", "B", "A", "B"],
            "count": [10, 20, 30, 40],
        }
    )
    data = data.set_index(["sample_name", "haplotype"])
    expected_output = data.copy()
    pd.testing.assert_frame_equal(filter_haplotype_frequency(data, 0), expected_output)


def test_filter_haplotype_frequency_filter():
    data = pd.DataFrame(
        {
            "sample_name": ["sample1", "sample1", "sample2", "sample2"],
            "haplotype": ["A", "B", "A", "B"],
            "count": [10, 20, 40, 30],
        }
    )
    data = data.set_index(["sample_name", "haplotype"])
    expected_output = pd.DataFrame(
        {
            "count": [20, 40],
        },
        index=pd.MultiIndex.from_tuples(
            [("sample1", "B"), ("sample2", "A")], names=["sample_name", "haplotype"]
        ),
    )
    pd.testing.assert_frame_equal(
        filter_haplotype_frequency(data, 0.5), expected_output
    )
