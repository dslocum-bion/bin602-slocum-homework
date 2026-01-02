"""
dna_ops.py

Reusable DNA/genotype utility functions shared by multiple scripts.
This module intentionally has no main().
"""

from typing import Dict, List, Tuple


def clean_dna_line(dna: str) -> str:
    """
    Clean a DNA/genotype string.

    - Replace all occurrences of 'NA' with '_' (underscore)
    - Remove all whitespace (spaces, tabs, etc.)
    - Normalize case to uppercase

    Args:
        dna: Raw DNA/genotype string (may include whitespace and 'NA').

    Returns:
        Cleaned DNA string.
    """
    s = dna.rstrip("\n")
    s = s.upper()
    s = s.replace("NA", "_")
    s = "".join(s.split())
    return s


def count_codons(seq: str) -> Dict[str, int]:
    """
    Count distinct, non-overlapping 3-nt codons in a sequence.

    Uses positions 0-2, 3-5, 6-8, ... and ignores any trailing bases
    fewer than 3.

    Args:
        seq: Cleaned DNA sequence string.

    Returns:
        Dict mapping codon -> frequency.
    """
    counts: Dict[str, int] = {}
    n = len(seq)
    end = n - (n % 3)
    for i in range(0, end, 3):
        codon = seq[i:i + 3]
        counts[codon] = counts.get(codon, 0) + 1
    return counts


def top_codons_with_proportions(counts: Dict[str, int], k: int = 3) -> str:
    """
    Format the top-k most frequent codons and their proportions.

    Sorting:
      - frequency descending
      - codon ascending (tie-break)

    Output format:
      "AAA:0.18 CCC:0.08 GGG:0.06" (2 decimal places)

    Args:
        counts: Dict mapping codon -> frequency.
        k: Number of top codons to output.

    Returns:
        A formatted string (possibly empty if no codons).
    """
    total = sum(counts.values())
    if total == 0:
        return ""

    top = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:k]
    return " ".join(f"{codon}:{freq/total:.2f}" for codon, freq in top)


def cg_content(seq: str) -> float:
    """
    Compute CG content: fraction of characters that are 'C' or 'G'.

    Args:
        seq: Cleaned DNA sequence string.

    Returns:
        CG content as float in [0, 1].
    """
    if not seq:
        return 0.0
    cg = sum(1 for b in seq if b == "C" or b == "G")
    return cg / len(seq)
