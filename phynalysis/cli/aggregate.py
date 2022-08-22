"""Aggregate subcommand."""

import re

import pandas as pd


def aggregate(args):
    """Aggregate command main function."""

    # load files
    barcodes = pd.read_csv(args.barcodes)
    samples = [pd.read_csv(file) for file in args.input]

    # extract barcodes from file names
    regex = r"(\w+)\.haplotypes\.csv"
    keys = [re.search(regex, file).group(1) for file in args.input]

    # merge data
    haplotypes = pd.concat(samples, keys=keys)
    haplotypes.index.names = ["bar_code", "local_id"]
    haplotypes.reset_index(inplace=True)

    # merge barcodes
    haplotypes_annotated = haplotypes.merge(
        barcodes, on="bar_code", how="left"
    ).reset_index()

    # write output
    haplotypes_annotated.to_csv(args.output, index=False)
