"""Export nexus format."""

from ..transform import haplotypes_to_matrix


def _get_nexus_header(n_tax, n_char):
    return f"""#NEXUS

BEGIN DATA;
    DIMENSIONS NTAX={n_tax} NCHAR={n_char};
    FORMAT MISSING=? GAP=- DATATYPE=DNA;
    MATRIX
"""


def _format_data(ids, matrix):
    longest_haplotype = max(map(len, ids))
    return "\n".join(
        [
            f"        {name.replace(':', '|').replace(';', '.').ljust(longest_haplotype)} {sequence}"
            for name, sequence in zip(ids, matrix)
        ]
    )


def get_nexus(data, reference):
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

    sequences_matrix = haplotypes_to_matrix(reference, data["haplotype"])

    return (
        _get_nexus_header(len(sequences_matrix), len(sequences_matrix[0]))
        + _format_data(data["id"], sequences_matrix)
        + ";\nEND;\n"
    )
