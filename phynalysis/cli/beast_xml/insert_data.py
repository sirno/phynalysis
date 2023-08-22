"""Insert data into beast xml file."""

import logging
import sys

import pandas as pd

from lxml import etree

from ...transform import haplotypes_to_sequences
from ..utils import write


def insert_data(args):
    """Insert data into beast xml file."""

    data = pd.read_csv(args.input)
    reference = "".join(open(args.reference).readlines())

    xml = etree.parse(args.template)
    root = xml.getroot()

    if data.block_id.duplicated().any():
        logging.error("Duplicate block ids found.")
        sys.exit(1)

    data.set_index("block_id", inplace=True)

    data["lineage"] = data.compartment + data.compartment.max() * data.replicate
    data["lineage"] -= data.lineage.min()

    sequences = haplotypes_to_sequences(reference, data["haplotype"])

    alignment = root.find(".//data[@id='alignment']")
    alignment.text = "\n".join(
        [
            f'<sequence id="{name}" taxon="{name}" value="{sequence}" />'
            for (name, row), sequence in zip(data.iterrows(), sequences)
        ]
    )

    time_trait = root.find(".//trait[@id='time']")
    time_trait.text = ",\n".join(
        f"{name}={row.time:.2f}" for name, row in data.iterrows()
    )

    type_trait = root.find(".//trait[@id='type_set']")
    type_trait.text = ",\n".join(
        f"{name}={row.lineage}" for name, row in data.iterrows()
    )

    # overwrite xml
    write(args.output, etree.tostring(root, pretty_print=True).decode("utf-8"))
