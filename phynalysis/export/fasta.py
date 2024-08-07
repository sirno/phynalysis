"""Export fasta format."""

from ..cli.utils import write
from ..transform import haplotypes_to_sequences

DEFAULT_TEMPLATE = """
{data}
"""


def _format_data(ids, matrix):
    return "\n".join(f">{name}\n{sequence}" for name, sequence in zip(ids, matrix))


def get_fasta(data, reference, template=None):
    """Convert haplotypes to fasta format.

    Parameters
    ----------
    data : pandas.DataFrame
        Dataframe with columns "haplotype" and "id".
    reference : str
        Reference sequence.
    template : str
        Template for fasta file with {data} as placeholder. If None, the default
        template is used.

    Returns
    -------
    str
        Fasta formatted string
    """
    if not "haplotype" in data.columns:
        raise ValueError("Dataframe must contain column 'haplotype'.")

    if not "id" in data.columns:
        raise ValueError("Dataframe must contain column 'id'.")

    if template is None:
        template = DEFAULT_TEMPLATE

    sequences_matrix = haplotypes_to_sequences(
        reference, data["haplotype"], data["count"]
    )

    return template.format(data=_format_data(data["id"], sequences_matrix)).strip("\n")


def write_fasta(path, data, reference, template=None):
    """Write fasta file.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to the output file.
    data : pandas.DataFrame
        Dataframe with columns "haplotype" and "id".
    reference : str
        Reference sequence.
    template : str
        Template path for fasta file with {data} as placeholder. If None, the default
        template is used.
    """
    if template is not None:
        with open(template) as f:
            template = f.read()

    write(path, get_fasta(data, reference, template=template))
