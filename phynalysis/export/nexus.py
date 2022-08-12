"""Export nexus format."""

from ..transform import haplotypes_to_matrix


DEFAULT_TEMPLATE = """
#NEXUS

BEGIN DATA;
    DIMENSIONS NTAX={n_tax} NCHAR={n_char};
    FORMAT MISSING=? GAP=- DATATYPE=DNA;
    MATRIX
{data}
    ;
END;
"""


def _format_data(ids, matrix):
    longest_haplotype = max(map(len, ids))
    return "\n".join(
        [
            f"        {name.replace(':', '|').replace(';', '.').ljust(longest_haplotype)} {sequence}"
            for name, sequence in zip(ids, matrix)
        ]
    )


def get_nexus(data, reference, template=None):
    """Convert haplotypes to nexus format.

    Parameters
    ----------
    data : pandas.DataFrame
        Dataframe with columns "haplotype" and "id".
    reference : str
        Reference sequence.

    Returns
    -------
    str
        Nexus formatted string
    """
    if not "haplotype" in data.columns:
        raise ValueError("Dataframe must contain column 'haplotype'.")

    if not "id" in data.columns:
        raise ValueError("Dataframe must contain column 'id'.")

    if template is None:
        template = DEFAULT_TEMPLATE

    sequences_matrix = haplotypes_to_matrix(reference, data["haplotype"])

    return template.format(
        n_tax=len(sequences_matrix),
        n_char=len(sequences_matrix[0]),
        data=_format_data(data["id"], sequences_matrix),
    )
