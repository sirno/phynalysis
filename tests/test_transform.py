"""Test transform module."""

from phynalysis.transform import (
    haplotype_to_dict,
    haplotype_to_list,
    haplotype_to_set,
    haplotype_to_string,
    haplotypes_to_sequences,
)

haplotype_string = "10:G->A;15:iATTA;3004:G->A"
haplotype_list = [(10, (3, 0)), (15, "iATTA"), (3004, (3, 0))]
haplotype_set = set([(10, (3, 0)), (15, "iATTA"), (3004, (3, 0))])
haplotype_dict = {10: (3, 0), 15: "iATTA", 3004: (3, 0)}


def test_haplotype_to_list():
    """Test `haplotype_to_list`."""
    assert haplotype_to_list(haplotype_string) == haplotype_list
    assert haplotype_to_list(haplotype_list) == haplotype_list
    assert haplotype_to_list(haplotype_set) == haplotype_list
    assert haplotype_to_list(haplotype_dict) == haplotype_list


def test_haplotype_to_set():
    """Test `haplotype_to_set`."""
    assert haplotype_to_set(haplotype_string) == haplotype_set
    assert haplotype_to_set(haplotype_list) == haplotype_set
    assert haplotype_to_set(haplotype_set) == haplotype_set
    assert haplotype_to_set(haplotype_dict) == haplotype_set


def test_haplotype_to_dict():
    """Test `haplotype_to_dict`."""
    assert haplotype_to_dict(haplotype_string) == haplotype_dict
    assert haplotype_to_dict(haplotype_list) == haplotype_dict
    assert haplotype_to_dict(haplotype_set) == haplotype_dict
    assert haplotype_to_dict(haplotype_dict) == haplotype_dict


def test_haplotype_to_string():
    """Test `haplotype_to_string`."""
    assert haplotype_to_string(haplotype_string) == haplotype_string
    assert haplotype_to_string(haplotype_list) == haplotype_string
    assert haplotype_to_string(haplotype_set) == haplotype_string
    assert haplotype_to_string(haplotype_dict) == haplotype_string


reference = "AAAA"
haplotypes = [
    "",
    "0:A->G",
    "consensus",
    "1:iTTT",
    set([(3, (0, 3))]),
    [(2, (0, 3))],
]


def test_haplotypes_to_sequences():
    """Test `haplotypes_to_phylip`."""
    assert haplotypes_to_sequences(reference, haplotypes) == [
        "AA---AA",
        "GA---AA",
        "AA---AA",
        "AATTTAA",
        "AA---AG",
        "AA---GA",
    ]
