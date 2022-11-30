"""Export fasta format."""

from ..transform import haplotypes_to_matrix

DEFAULT_TEMPLATE = """
{data}
"""


def _format_data(ids, matrix):
    return "\n".join([f">{name}\n{sequence}" for name, sequence in zip(ids, matrix)])


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

    sequences_matrix = haplotypes_to_matrix(reference, data["haplotype"])

    return template.format(data=_format_data(data["id"], sequences_matrix))
