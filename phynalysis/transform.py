"""Common transformations for haplotypes and populations.

Glossary:
    - haplotype: A list of changes
        - as a string: "position:mutation;position:mutation;..."
        - as a list: [(position, mutation), (position, mutation), ...]
        - as a set: {(position, mutation), (position, mutation), ...}
        - as a dictionary: {position: mutation, position: mutation, ...}
    - change: A tuple of position and mutation
    - mutation: A string representing a change
        format: "<reference>-><mutation>"
    - haplotypes: A list of haplotypes
"""

__all__ = [
    "haplotype_to_list",
    "haplotype_to_set",
    "haplotype_to_dict",
    "haplotype_to_string",
    "haplotypes_to_sequences",
    "haplotypes_to_matrix",
    "haplotypes_to_frequencies",
]

from typing import Tuple, Union

import numpy as np

Substitution = tuple
Insertion = str

Mutation = Union[Substitution, Insertion]
Change = Tuple[int, str]

HaplotypeList = list[Change]
HaplotypeSet = set[Change]
HaplotypeDict = dict[int, str]

Haplotype = Union[str, HaplotypeList, HaplotypeSet, HaplotypeDict]

_ENCODING = {
    "A": 0,
    "T": 1,
    "C": 2,
    "G": 3,
    "0": 0,
    "1": 1,
    "2": 2,
    "3": 3,
}

_ENCODE_NT = {
    0: "A",
    1: "T",
    2: "C",
    3: "G",
    "A": "A",
    "T": "T",
    "C": "C",
    "G": "G",
    "0": "A",
    "1": "T",
    "2": "C",
    "3": "G",
    "_": "_",
}


def _encoder(change: Change) -> Change:
    """Internal encoder."""
    return (change[0], _ENCODING[change[1]])


def _parse_mutation(mutation: str) -> Mutation:
    """Internal parser for Mutation."""

    # if mutation is a substitution we store it as a tuple
    if "->" in mutation:
        ref, mut = mutation.split("->")
        return _ENCODING[ref], _ENCODING[mut]

    # if mutation is an insertion we store it as a string
    return mutation


def _parse_change(change: str) -> Change:
    """Internal parser for Change."""
    position, mutation = change.split(":")
    return int(position), _parse_mutation(mutation)


def _parse_haplotype_to_iter(haplotype: str) -> HaplotypeList:
    """Internal parser"""
    return map(_parse_change, haplotype.split(";"))


def _mutation_to_string(mutation: Mutation) -> str:
    """Get the string representation of a mutation."""
    if isinstance(mutation, Substitution):
        return "{}->{}".format(_ENCODE_NT[mutation[0]], _ENCODE_NT[mutation[1]])
    if isinstance(mutation, Insertion):
        return "i" + "".join(_ENCODE_NT[m] for m in mutation[1:])
    raise NotImplementedError(f"Unknown mutation type {mutation}.")


def _change_to_string(change: Change) -> str:
    """Get the string representation of a change."""
    position, mutation = change
    return "{}:{}".format(position, _mutation_to_string(mutation))


def _get_position(change: Change) -> int:
    """Get the position of a change."""
    return change[0]


def haplotype_to_list(haplotype: Haplotype) -> HaplotypeList:
    """Get the mutations in a haplotype.

    Returns
    -------
    List[Tuple[int, str]]
        a list of sorted changes in the haplotype
    """
    # reference sequence
    if not haplotype or haplotype in ["consensus", "wt", "wildtype"]:
        return list()

    # do nothing when haplotype is already a list
    if isinstance(haplotype, list):
        return haplotype

    # parse haplotype if it is a string
    if isinstance(haplotype, str):
        return list(_parse_haplotype_to_iter(haplotype))

    # convert dict to iterator over items
    if isinstance(haplotype, dict):
        return sorted(list(haplotype.items()), key=_get_position)

    return sorted(list(haplotype), key=_get_position)


def haplotype_to_set(haplotype: Haplotype) -> HaplotypeSet:
    """Convert haplotype to a set.

    Returns
    -------
    Set[Tuple[int, str]]
        a set of changes in the haplotype
    """
    # reference sequence
    if not haplotype or haplotype in ["consensus", "wt", "wildtype"]:
        return set()

    # do nothing when haplotype is already a set
    if isinstance(haplotype, set):
        return haplotype

    # parse haplotype if it is a string
    if isinstance(haplotype, str):
        return set(_parse_haplotype_to_iter(haplotype))

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
    if not haplotype or haplotype in ["consensus", "wt", "wildtype"]:
        return dict()

    # do nothing when haplotype is already a dict
    if isinstance(haplotype, dict):
        return haplotype

    # parse haplotype if it is a string
    if isinstance(haplotype, str):
        return dict(_parse_haplotype_to_iter(haplotype))

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
        _change_to_string(change) for change in sorted(haplotype, key=_get_position)
    )


def haplotypes_to_sequences(
    reference: str,
    haplotypes: list[Haplotype],
    count: list[int] | None = None,
) -> list[str]:
    """Convert haplotypes to matrix of aligned symbols."""
    sequences = []
    i = 0
    if count is None:
        count = [1] * len(haplotypes)
    for haplotype, n in zip(haplotypes, count):
        # create list with characters for each position
        sequence = list(reference)
        # transform haplotype to list representation
        haplotype = haplotype_to_list(haplotype)
        # add all changes to sequence
        for position, mutation in haplotype:
            if isinstance(mutation, Substitution):
                sequence[position] = _ENCODE_NT[mutation[1]]
            elif isinstance(mutation, Insertion):
                assert mutation.startswith("i")
                for m in mutation[1:]:
                    sequence[position] += _ENCODE_NT[m]
            else:
                NotImplementedError(
                    f"Unknown mutation type ({type(mutation)}) {mutation}."
                )

        # avoid empty sequences
        if not sequence:
            continue

        # add sequence n times
        for _ in range(int(n)):
            sequences.append(sequence)
            i += 1

    # determine longest possible sequence for each reference position
    longest = [max(map(len, [s[i] for s in sequences])) for i in range(len(reference))]
    # add gaps to sequences
    sequences_lip = [
        "".join([s.ljust(l, "-") for s, l in zip(s, longest)]) for s in sequences
    ]

    return sequences_lip


def haplotypes_to_matrix(reference: str, haplotypes: list[Haplotype]) -> np.ndarray:
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


def haplotypes_to_frequencies(
    reference: str, haplotypes: list[Haplotype]
) -> np.ndarray:
    """Convert haplotypes to array of frequencies."""
    counts = np.zeros((len(reference), 4))

    # count all changes
    for haplotype in haplotypes:
        # transform haplotype to list representation
        haplotype = haplotype_to_list(haplotype)
        # add all changes to sequence
        for position, mutation in haplotype:
            if "->" in mutation:
                counts[position, _ENCODING[mutation[-1]]] += 1
            else:
                NotImplementedError(f"Unknown mutation type {mutation}.")

    # count occurrences of reference base
    total = len(haplotypes)
    for position in range(len(reference)):
        ref_base = _ENCODING[reference[position]]
        counts[position, ref_base] = (
            total - counts[position].sum() + counts[position, ref_base]
        )

    # normalize counts
    return counts / len(haplotypes)
