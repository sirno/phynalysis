# Phynalysis

Collection of tools for analysis of long-read, high-fidelity sequencing reads of
virus populations originally written by Eva Bons.

## CLI Tools

`convert` converts haplotypes data to files that can be analyzed by phylogenetic
and phylodynamic software. Possible formats include `phylip`, `nexus` and `xml`.
Convert can be used to fill the data into arbitrary template files.

`haplotypes` extracts haplotypes and associated data from alignment files. The
output will be exported to csv.

`consensus` finds the consensus sequence for an alignment. The consensus
sequence is the sequence that contains the most common nucleotide in each
position.

`ancestors` finds the closest ancestor for every descendant ancestor. The
closest ancestor is the one that has least hamming-distance and among those
ancestors with the same hamming-distance is the most common.

## Library functions

Some common operations are accessible as library functions.
