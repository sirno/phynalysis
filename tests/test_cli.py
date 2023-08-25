"""Test cli functions."""

import argparse
import io

import pandas as pd

from phynalysis.cli import aggregate, filter


def test_aggregate():
    output_buffer = io.StringIO()
    args = argparse.Namespace(
        barcodes="tests/data/barcodes.csv",
        input=[
            "tests/data/sample_200_1.haplotypes.csv",
            "tests/data/sample_200_2.haplotypes.csv",
        ],
        output=output_buffer,
    )
    aggregate.aggregate(args)
    output_buffer.seek(0)
    output = pd.read_csv(output_buffer)
    expected_output = pd.read_csv("tests/data/samples.haplotypes.csv")
    pd.testing.assert_frame_equal(output, expected_output)


def test_filter():
    output_buffer = io.StringIO()
    data = pd.read_csv("tests/data/samples.haplotypes.csv")
    args = argparse.Namespace(
        filter_insertions=False,
        input="tests/data/samples.haplotypes.csv",
        output=output_buffer,
        query="compartment == 1",
    )
    filter.filter_cmd(args)
    output_buffer.seek(0)
    output = pd.read_csv(output_buffer)
    expected_output = data.query("compartment == 1")
    pd.testing.assert_frame_equal(output, expected_output)
