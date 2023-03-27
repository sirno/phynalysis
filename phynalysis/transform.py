"""Common transformations for haplotypes and populations.

Glossary:
    - haplotype: A list of changes
        - as a string: "position:mutation;position:mutation;..."
        - as a list: [(position, mutation), (position, mutation), ...]
        - as a set: {(position, mutation), (position, mutation), ...}
        - as a dictionary: {position: mutation, position: mutation, ...}
    - haplotypes: A list of haplotypes
"""

import numpy as np

from typing import Dict, List, Set, Tuple, Union

Change = Tuple[int, str]

HaplotypeList = List[Change]
HaplotypeSet = Set[Change]
HaplotypeDict = Dict[int, str]

Haplotype = Union[str, HaplotypeList, HaplotypeSet, HaplotypeDict]

_ENCODING = {
    "A": 0,
    "C": 1,
    "G": 2,
    "T": 3,
}


def _parse_haplotype_to_list(haplotype: str) -> HaplotypeList:
    """Internal parser"""
    changes = [change.split(":") for change in haplotype.split(";")]
    return [(int(change[0]), change[1]) for change in changes]


def haplotype_to_list(haplotype: Haplotype) -> HaplotypeList:
    """Get the mutations in a haplotype.

    Returns
    -------
    List[Tuple[int, str]]
        a list of sorted changes in the haplotype
    """
    # reference sequence
    if not haplotype or haplotype == "consensus":
        return list()

    # do nothing when haplotype is already a list
    if isinstance(haplotype, list):
        return haplotype

    # parse haplotype if it is a string
    if isinstance(haplotype, str):
        return list(_parse_haplotype_to_list(haplotype))

    # convert dict to iterator over items
    if isinstance(haplotype, dict):
        return sorted(list(haplotype.items()), key=lambda x: x[0])

    return sorted(list(haplotype), key=lambda x: x[0])


def haplotype_to_set(haplotype: Haplotype) -> HaplotypeSet:
    """Convert haplotype to a set.

    Returns
    -------
    Set[Tuple[int, str]]
        a set of changes in the haplotype
    """
    # reference sequence
    if not haplotype or haplotype == "consensus":
        return set()

    # do nothing when haplotype is already a set
    if isinstance(haplotype, set):
        return haplotype

    # parse haplotype if it is a string
    if isinstance(haplotype, str):
        return set(_parse_haplotype_to_list(haplotype))

    # convert dict to iterator over items
    if isinstance(haplotype, dict):
        return set(haplotype.items())

    return set(haplotype)


def haplotype_to_dict(haplotype: Haplotype) -> HaplotypeDict:
    """Convert haplotype to a dict.

    Returns
    -------
    Dict[int, str]
        a dictionary of changes in the haplotype
    """
    # reference sequence
    if not haplotype or haplotype == "consensus":
        return dict()

    # do nothing when haplotype is already a dict
    if isinstance(haplotype, dict):
        return haplotype

    # parse haplotype if it is a string
    if isinstance(haplotype, str):
        return dict(_parse_haplotype_to_list(haplotype))

    return dict(haplotype)


def haplotype_to_string(haplotype: Haplotype) -> str:
    """Convert a haplotype to a string.

    Returns
    -------
    str
        String representation of the haplotype
    """
    # reference sequence
    if not haplotype:
        return "consensus"

    # do nothing when haplotype is already a string
    if isinstance(haplotype, str):
        return haplotype

    # change iterator if it is a dictionary
    if isinstance(haplotype, dict):
        haplotype = haplotype.items()

    return ";".join(
        f"{pos}:{mutation}" for pos, mutation in sorted(haplotype, key=lambda x: x[0])
    )


def haplotypes_to_sequences(reference: str, haplotypes: List[Haplotype]) -> List[str]:
    """Convert haplotypes to matrix of aligned symbols."""
    sequences = []
    for haplotype in haplotypes:
        # create list with characters for each position
        sequence = list(reference)
        # transform haplotype to list representation
        haplotype = haplotype_to_list(haplotype)
        # add all changes to sequence
        for position, mutation in haplotype:
            if "->" in mutation:
                sequence[position] = mutation[-1]
            elif mutation.startswith("i"):
                sequence[position] += mutation[1:]
            else:
                NotImplementedError(f"Unknown mutation type {mutation}.")
        if sequence:
            sequences.append(sequence)

    # determine longest possible sequence for each reference position
    longest = [max(map(len, [s[i] for s in sequences])) for i in range(len(reference))]
    # add gaps to sequences
    sequences_lip = [
        "".join([s.ljust(l, "-") for s, l in zip(s, longest)]) for s in sequences
    ]

    return sequences_lip


def haplotypes_to_matrix(reference: str, haplotypes: List[Haplotype]) -> np.ndarray:
    """Convert haplotypes to matrix of aligned encoded symbols.

    Note: Can only handle substitutions.
    """
    encoded_reference = [int(_ENCODING[c]) for c in reference]
    sequences = []
    for haplotype in haplotypes:
        # create list with characters for each position
        sequence = encoded_reference.copy()
        # transform haplotype to list representation
        haplotype = haplotype_to_list(haplotype)
        # add all changes to sequence
        for position, mutation in haplotype:
            if "->" in mutation:
                sequence[position] = _ENCODING[mutation[-1]]
            else:
                NotImplementedError(f"Unknown mutation type {mutation}.")
        if sequence:
            sequences.append(sequence)

    return sequences
