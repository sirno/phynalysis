"""Export phylip format."""

from ..transform import haplotypes_to_matrix


def _format_data(ids, matrix):
    longest_haplotype = max(map(len, ids))
    return "\n".join(
        [
            f"{name.replace(':', '|').replace(';', '.').ljust(longest_haplotype)} {sequence}"
            for name, sequence in zip(ids, matrix)
        ]
    )


def get_phylip(data, reference):
    """Convert haplotypes to phylip format.

    Parameters
    ----------
    data : pandas.DataFrame
        Dataframe with columns "haplotype" and "id".
    reference : str
        Reference sequence.

    Returns
    -------
    str
        Phylip formatted string
    """
    if not "haplotype" in data.columns:
        raise ValueError("Dataframe must contain column 'haplotype'.")

    if not "id" in data.columns:
        raise ValueError("Dataframe must contain column 'id'.")

    sequences_matrix = haplotypes_to_matrix(reference, data["haplotype"])

    return f"{len(data['id'])} {len(sequences_matrix[0])}\n" + _format_data(
        data["id"], sequences_matrix
    )
