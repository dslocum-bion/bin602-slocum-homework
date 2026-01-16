python3 - <<'PY'
import sys
from collections import defaultdict

fname = sys.argv[1]
lens = defaultdict(list)

with open(fname, "r", newline="") as f:
    for i, line in enumerate(f, 1):
        s = line.strip()  # removes spaces + \r + \n
        if not s:
            continue
        lens[len(s)].append((i, s))

for L in sorted(lens):
    print(L, ":", len(lens[L]), "lines")

if len(lens) > 1:
    print("\nLines with non-majority lengths:")
    # find majority length
    maj = max(lens, key=lambda L: len(lens[L]))
    for L in sorted(lens):
        if L != maj:
            for i, s in lens[L][:20]:
                print(f"line {i}: len={L!r} value={s!r}")
PY
