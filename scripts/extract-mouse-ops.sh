#!/usr/bin/env bash
# File: extract-mouse-ops.sh
# Purpose: For each *.data file in a mouse data directory, generate:
#   Problem 2: .snp    (sequence columns only, after first NA column)
#   Problem 3: .codons (top 3 codons/proportions per line via codon script)
#   Problem 4: .cg     (CG content per line via cg script)
#
# Usage:
#   ./scripts/extract-mouse-ops.sh data/mouse [--skip]
#
# If --skip is provided, existing outputs are not regenerated.

set -euo pipefail

if [[ $# -lt 1 || "${1:-}" == "-h" ]]; then
  echo "USAGE: ./scripts/extract-mouse-ops.sh <mouse data directory> [--skip]"
  exit 1
fi

mouse_dir="$1"
skipExisting=0

if [[ $# -gt 1 && "${2:-}" == "--skip" ]]; then
  skipExisting=1
fi

if [[ ! -d "$mouse_dir" ]]; then
  echo "ERROR: $mouse_dir is not a directory!"
  exit 1
fi

CODON_SCRIPT="scripts/codon_counter.py"   
CG_SCRIPT="scripts/cg.py"

if [[ ! -f "$CODON_SCRIPT" ]]; then
  echo "ERROR: Codon script not found at $CODON_SCRIPT"
  echo "Edit CODON_SCRIPT in this bash file to match your actual filename."
  exit 1
fi

if [[ ! -f "$CG_SCRIPT" ]]; then
  echo "ERROR: CG script not found at $CG_SCRIPT"
  exit 1
fi

shopt -s nullglob
data_files=("$mouse_dir"/*.data)

if [[ ${#data_files[@]} -eq 0 ]]; then
  echo "No .data files found in $mouse_dir"
  exit 0
fi

for data_file in "${data_files[@]}"; do
  base="${data_file%.data}"
  snp_file="${base}.snp"
  codons_file="${base}.codons"
  cg_file="${base}.cg"

  echo "=== Processing $(basename "$data_file") ==="

  # Problem 2: .data -> .snp
  if [[ $skipExisting -eq 1 && -f "$snp_file" ]]; then
    echo "Skipping $(basename "$snp_file") (already exists)"
  else
    echo "Generating $(basename "$snp_file")"
    # Space-delimited file; sequence begins at field 7 (after NA field 6)
    cut -d' ' -f7- "$data_file" > "$snp_file"
  fi

  # Problem 3: .snp -> .codons
  if [[ $skipExisting -eq 1 && -f "$codons_file" ]]; then
    echo "Skipping $(basename "$codons_file") (already exists)"
  else
    echo "Generating $(basename "$codons_file")"
    cat "$snp_file" | python3 "$CODON_SCRIPT" > "$codons_file"
  fi

  # Problem 4: .snp -> .cg
  if [[ $skipExisting -eq 1 && -f "$cg_file" ]]; then
    echo "Skipping $(basename "$cg_file") (already exists)"
  else
    echo "Generating $(basename "$cg_file")"
    cat "$snp_file" | python3 "$CG_SCRIPT" > "$cg_file"
  fi

  echo
done
