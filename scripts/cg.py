"""
cg.py

Reads lines from stdin, cleans them, and prints CG content per line.
"""

import sys
from dna_ops import clean_dna_line, cg_content


def main() -> None:
    for raw_line in sys.stdin:
        cleaned = clean_dna_line(raw_line)
        print(f"{cg_content(cleaned):.4f}")


if __name__ == "__main__":
    main()
