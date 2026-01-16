#!/usr/bin/env python3
import sys
from collections import defaultdict, deque
from typing import Dict, List, Optional, Set, Tuple

DNA_ALPHABET = set("ACGT")


# ----------------------------
# Input
# ----------------------------
def read_lmers(path: str) -> List[str]:
    """Read one l-mer per non-empty line; strip whitespace."""
    with open(path, "r", newline="") as f:
        lmers = [line.strip() for line in f if line.strip()]

    if not lmers:
        raise ValueError("Input file contains no l-mers (no non-empty lines).")

    l = len(lmers[0])
    if l == 0:
        raise ValueError("First l-mer is empty after stripping.")

    # Validate same length
    bad_len = [(i + 1, s) for i, s in enumerate(lmers) if len(s) != l]
    if bad_len:
        msg = [
            "Not all l-mers have the same length.",
            f"Detected l = {l} from line 1.",
            "First few mismatches:",
        ]
        for ln, s in bad_len[:25]:
            msg.append(f"  line {ln}: len={len(s)} value={s!r}")
        raise ValueError("\n".join(msg))

    # Validate DNA characters only
    bad_chars = [(i + 1, s) for i, s in enumerate(lmers)
                 if any(c not in DNA_ALPHABET for c in s)]
    if bad_chars:
        msg = [
            "Input contains non-DNA characters. Allowed: A,C,G,T.",
            "First few bad lines:",
        ]
        for ln, s in bad_chars[:25]:
            msg.append(f"  line {ln}: {s!r}")
        raise ValueError("\n".join(msg))

    return lmers


# ----------------------------
# Graph construction
# ----------------------------
def build_debruijn(lmers: List[str]) -> Tuple[Dict[str, List[str]], Dict[str, int], Dict[str, int], int]:
    """
    Build de Bruijn graph from l-mers.
      vertices: (l-1)-mers
      edge for each l-mer: prefix -> suffix
    Returns (adj, indeg, outdeg, k) where k = l-1.
    """
    l = len(lmers[0])
    k = l - 1

    adj: Dict[str, List[str]] = defaultdict(list)
    indeg: Dict[str, int] = defaultdict(int)
    outdeg: Dict[str, int] = defaultdict(int)

    for mer in lmers:
        u = mer[:k]
        v = mer[1:]
        adj[u].append(v)
        outdeg[u] += 1
        indeg[v] += 1

        # Ensure keys exist
        _ = adj[v]
        _ = indeg[u]
        _ = outdeg[v]

    return adj, indeg, outdeg, k


def recompute_degrees(adj: Dict[str, List[str]]) -> Tuple[Dict[str, int], Dict[str, int]]:
    indeg: Dict[str, int] = defaultdict(int)
    outdeg: Dict[str, int] = defaultdict(int)

    for u, outs in adj.items():
        outdeg[u] += len(outs)
        _ = indeg[u]
        for v in outs:
            indeg[v] += 1
            _ = outdeg[v]
    return indeg, outdeg


# ----------------------------
# Connectivity & components
# ----------------------------
def weakly_connected_incident_vertices(adj: Dict[str, List[str]]) -> Tuple[Dict[str, Set[str]], Set[str]]:
    """
    Build undirected neighbor sets and the set of vertices that touch at least one edge.
    """
    und: Dict[str, Set[str]] = defaultdict(set)
    incident: Set[str] = set()

    for u, outs in adj.items():
        for v in outs:
            und[u].add(v)
            und[v].add(u)
            incident.add(u)
            incident.add(v)

    return und, incident


def is_weakly_connected(adj: Dict[str, List[str]], start: str) -> bool:
    und, incident = weakly_connected_incident_vertices(adj)
    if not incident:
        return True

    seen = {start}
    q = deque([start])
    while q:
        x = q.popleft()
        for y in und.get(x, ()):
            if y not in seen:
                seen.add(y)
                q.append(y)

    return incident.issubset(seen)


def largest_component_subgraph(adj: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Return adjacency dict restricted to the largest weakly connected component,
    measured by number of edges inside the component. Preserves multiplicity.
    """
    und, incident = weakly_connected_incident_vertices(adj)
    if not incident:
        return defaultdict(list)

    # Find components (vertex sets)
    seen: Set[str] = set()
    comps: List[Set[str]] = []

    for v in incident:
        if v in seen:
            continue
        q = deque([v])
        seen.add(v)
        verts = {v}
        while q:
            x = q.popleft()
            for y in und.get(x, ()):
                if y not in seen:
                    seen.add(y)
                    verts.add(y)
                    q.append(y)
        comps.append(verts)

    def edge_count(verts: Set[str]) -> int:
        c = 0
        for u in verts:
            for v in adj.get(u, []):
                if v in verts:
                    c += 1
        return c

    comps.sort(key=edge_count, reverse=True)
    keep = comps[0]

    # Filter adjacency to kept vertices
    new_adj: Dict[str, List[str]] = defaultdict(list)
    for u in keep:
        for v in adj.get(u, []):
            if v in keep:
                new_adj[u].append(v)
        _ = new_adj[u]
    return new_adj


# ----------------------------
# Eulerian path/cycle
# ----------------------------
def find_start_vertex(adj: Dict[str, List[str]], indeg: Dict[str, int], outdeg: Dict[str, int]) -> str:
    """
    Determine start vertex for Eulerian path/cycle.
    """
    start = None
    end = None
    vertices = set(indeg.keys()) | set(outdeg.keys()) | set(adj.keys())

    for v in vertices:
        outd = outdeg.get(v, 0)
        ind = indeg.get(v, 0)
        if outd - ind == 1:
            if start is not None:
                raise ValueError("Graph is not Eulerian: multiple possible starts.")
            start = v
        elif ind - outd == 1:
            if end is not None:
                raise ValueError("Graph is not Eulerian: multiple possible ends.")
            end = v
        elif ind != outd:
            raise ValueError("Graph is not Eulerian: indegree/outdegree mismatch.")

    if start is None:
        # Eulerian cycle: pick any vertex with outgoing edges
        for v, outs in adj.items():
            if outs:
                start = v
                break

    if start is None:
        raise ValueError("Graph has no edges (nothing to assemble).")

    return start


def eulerian_walk_hierholzer(adj: Dict[str, List[str]], start: str) -> List[str]:
    """
    Hierholzer's algorithm. Mutates adjacency by popping edges.
    Returns list of vertices in traversal order.
    """
    for u in adj:
        adj[u].reverse()

    stack = [start]
    path: List[str] = []

    while stack:
        v = stack[-1]
        if adj[v]:
            nxt = adj[v].pop()
            stack.append(nxt)
        else:
            path.append(stack.pop())

    path.reverse()
    return path


def spell_from_vertex_path(vpath: List[str]) -> str:
    """Given path of (l-1)-mers, reconstruct superstring."""
    if not vpath:
        return ""
    s = vpath[0]
    for v in vpath[1:]:
        s += v[-1]
    return s


# ----------------------------
# SBH assembly (Option A)
# ----------------------------
def sbh_assemble_largest_component(lmers: List[str]) -> str:
    """
    Assemble using Eulerian approach.
    If disconnected: keep only largest component by edge count.
    If not perfectly Eulerian (can't cover all edges): still output best contig found,
    with a warning.
    """
    adj, indeg, outdeg, _k = build_debruijn(lmers)

    # Pick an initial start candidate (may fail if degree mismatch, that's okay)
    start = None
    try:
        start = find_start_vertex(adj, indeg, outdeg)
    except ValueError:
        # We'll handle imperfect cases later; choose any node with outgoing edges
        for v, outs in adj.items():
            if outs:
                start = v
                break

    if start is None:
        raise ValueError("No edges to traverse (empty graph).")

    # If disconnected, keep largest component
    if not is_weakly_connected(adj, start):
        adj = largest_component_subgraph(adj)
        indeg, outdeg = recompute_degrees(adj)

        # Re-pick start for the component
        try:
            start = find_start_vertex(adj, indeg, outdeg)
        except ValueError:
            for v, outs in adj.items():
                if outs:
                    start = v
                    break

        print("WARNING: spectrum disconnected; assembling largest component only.", file=sys.stderr)

    # Perform walk (best-effort)
    vpath = eulerian_walk_hierholzer(adj, start)

    edges_in_component = sum(len(outs) for outs in adj.values())
    used_edges = max(0, len(vpath) - 1)

    if used_edges != edges_in_component:
        print(
            f"WARNING: could not traverse all edges in largest component "
            f"(used {used_edges} of {edges_in_component}). Outputting best contig found.",
            file=sys.stderr,
        )

    return spell_from_vertex_path(vpath)


def write_or_print(result: str, output_path: Optional[str]) -> None:
    if output_path:
        with open(output_path, "w") as f:
            f.write(result + "\n")
    else:
        print(result)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 sequencing_by_hybridization.py input_lmers.txt [output.txt]")
        print("Input: one DNA l-mer (A/C/G/T) per line, all same length.")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) >= 3 else None

    try:
        lmers = read_lmers(input_path)
        result = sbh_assemble_largest_component(lmers)
        write_or_print(result, output_path)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
