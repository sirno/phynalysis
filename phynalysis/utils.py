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


def balance_unique_haplotypes(data, groupby):
    """Balance unique haplotypes by group."""
    groups = data.reset_index().groupby(groupby)
    min_count = groups.haplotype.count().min()
    return (
        groups.apply(lambda group: group.nlargest(min_count, "count"))
        .reset_index(drop=True)
        .set_index(data.index.names)
    )


def split_haplotypes(data, groupby):
    """Split haplotypes by group."""
    groups = data.reset_index().groupby(groupby)
    return [group.set_index(data.index.names) for _, group in groups]


def unstack_haplotypes(data):
    """Unstack haplotypes."""
    return data.reset_index().set_index(["haplotype", "sample_name"]).unstack()
