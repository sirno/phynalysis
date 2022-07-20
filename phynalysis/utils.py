"""Collection of functions for phynalysis."""
import numpy as np
import pandas as pd


def haplotype_to_mutations(haplotype: str):
    """Get the mutations in a haplotype."""
    if haplotype == "consensus":
        return []
    mutation_strings = haplotype.split(";")
    mutations = []
    for mutation in mutation_strings:
        split = mutation.split(":")
        mutations.append((int(split[0]), split[1]))
    return mutations
