"""
codon_counter.py

Reads lines from stdin, cleans them, counts non-overlapping codons,
and prints the top 3 codons with proportions per line.
"""

import sys
from dna_ops import clean_dna_line, count_codons, top_codons_with_proportions


def main() -> None:
    for raw_line in sys.stdin:
        cleaned = clean_dna_line(raw_line)
        counts = count_codons(cleaned)
        print(top_codons_with_proportions(counts, k=3))


if __name__ == "__main__":
    main()
