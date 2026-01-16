# !/usr/bin/env bash
# File: download-mouse-data.sh
# Date: 2025-12-15
# Author: Davie Slocum
# Purpose: Download the files chr1.Build37.data --- chr20.Build37.data from
#     http://mtweb.cs.ucl.ac.uk/HSMICE/GENOTYPES/

set -euo pipefail

if [[ $# -lt 1 || "${1:-}" == "-h" ]]; then
    echo "USAGE: ./download-mouse-data.sh <dest directory> [--skip]"
    echo "Including --skip will cause files already downloaded to be skipped."
    exit 1
fi

destDIR="$1"
skipExisting=0

# Check is user want's to skip existing files.
if [[ $# -gt 1 && "${2:-}" == "--skip" ]]; then
    skipExisting=1
fi

#Ensure the destination directory exists and is a directory
if [[ ! -d "$destDIR" ]]; then
    echo "ERROR: $destDIR is not a directory!"
    exit 1
fi

# Download all the files.
for i in {1..20}; do
    filename="chr${i}.Build37.data"

    if [[ $skipExisting -eq 1 && -f "$destDIR/$filename" ]]; then
        echo "Skipping $filename (already downloaded)..."
    else
    echo "Downloading $filename..."
    curl -L -o "$destDIR/$filename" "http://mtweb.cs.ucl.ac.uk/HSMICE/GENOTYPES/$filename"
    sleep 0.5
    fi
done
