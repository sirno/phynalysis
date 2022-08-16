"""Export xml format."""

from phynalysis.transform import haplotypes_to_matrix


def _sequence_data(data, sequences):
    return "\n".join(
        [
            f'<sequence id="{row.id}" taxon="{name}" value="{sequence}" />'
            for (name, row), sequence in zip(data.iterrows(), sequences)
        ]
    )


def _time_data(data):
    return ",\n".join([f"{name}={row.time:.2f}" for name, row in data.iterrows()])


def _count_data(data):
    return ",\n".join([f"{name}={row['count']}" for name, row in data.iterrows()])


def get_xml(data, reference, template=None):
    """Convert haplotypes to xml format.

    Parameters
    ----------
    data : pandas.DataFrame
        Dataframe with columns "haplotype", "id" and "time"
    reference : str
        Reference sequence.
    template : str
        Template for xml file with {sequence_data}, {time_data} and {count_data} as
        placeholders.

    Returns
    -------
    str
        XML formatted string
    """
    if template is None:
        raise ValueError("Template must be provided for xml export.")

    if not "haplotype" in data.columns:
        raise ValueError("Dataframe must contain column 'haplotype'.")

    if not "id" in data.columns:
        raise ValueError("Dataframe must contain column 'id'.")

    if not "time" in data.columns:
        raise ValueError("Dataframe must contain column 'time'.")

    sequences_matrix = haplotypes_to_matrix(reference, data["haplotype"])

    return template.format(
        sequence_data=_sequence_data(data, sequences_matrix),
        time_data=_time_data(data),
        count_data=_count_data(data),
    )
