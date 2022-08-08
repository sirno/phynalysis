"""Collection of functions for phynalysis."""


def compute_haplotype_frequency(data):
    """Compute frequencies for haplotype data."""
    return data["count"].div(data.groupby("sample_name")["count"].sum(), axis=0)


def filter_haplotype_counts(data, min_counts):
    """Filter haplotype data by minimum counts."""
    return data.loc[data["count"].ge(min_counts)].copy()


def filter_haplotype_frequency(data, min_frequency):
    """Filter haplotype data by minimum frequency."""
    frequencies = compute_haplotype_frequency(data)
    return data.loc[frequencies.ge(min_frequency)].copy()
