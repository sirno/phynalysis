"""Export phylip format."""

from ..cli.utils import write
from ..transform import haplotypes_to_sequences
from .nexus import DEFAULT_TEMPLATE
from .formatter import IncrementalFormatter

DEFAULT_TEMPLATE = """
{n_tax} {n_char}
{data}
"""


def _format_data(ids, matrix):
    longest_haplotype = max(map(len, ids))
    return "\n".join(
        [
            f"{name.replace(':', '|').replace(';', '.').ljust(longest_haplotype)} {sequence}"
            for name, sequence in zip(ids, matrix)
        ]
    )


def get_phylip(data, reference, template=None):
    """Convert haplotypes to phylip format.

    Parameters
    ----------
    data : pandas.DataFrame
        Dataframe with columns "haplotype" and "id".
    reference : str
        Reference sequence.
    template : str
        Template for phylip file with {n_tax}, {n_char} and {data} as placeholders. If
        None, the default template is used.

    Returns
    -------
    str
        Phylip formatted string
    """
    if not "haplotype" in data.columns:
        raise ValueError("Dataframe must contain column 'haplotype'.")

    if not "id" in data.columns:
        raise ValueError("Dataframe must contain column 'id'.")

    if template is None:
        template = DEFAULT_TEMPLATE

    sequences_matrix = haplotypes_to_sequences(reference, data["haplotype"])

    return IncrementalFormatter().format(
        template,
        n_tax=len(sequences_matrix),
        n_char=len(sequences_matrix[0]),
        data=_format_data([str(i) for i in data.index], sequences_matrix),
    )


def write_phylip(path, data, reference, template=None):
    """Write phylip formatted data to file.

    Parameters
    ----------
    path : str
        Output file.
    data : pandas.DataFrame
        Dataframe with columns "haplotype" and "id".
    reference : str
        Reference sequence.
    template : str
        Template path for phylip file with {n_tax}, {n_char} and {data} as placeholders.
        If None, the default template is used.
    """
    if template is not None:
        with open(template, "r") as f:
            template = f.read()

    write(path, get_phylip(data, reference, template))
