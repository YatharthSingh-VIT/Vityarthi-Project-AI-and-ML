import heapq
import time
from collections import deque


def _neighbors(grid, r, c, rows, cols):
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 1:
            yield (nr, nc)


def _trace_path(parent, start, end):
    path, node = [], end
    while node != start:
        path.append(node)
        node = parent[node]
    path.append(start)
    path.reverse()
    return path


def bfs(grid, start, end, rows, cols):
    queue = deque([start])
    parent = {start: None}
    steps = []
    t0 = time.perf_counter()

    while queue:
        node = queue.popleft()
        steps.append(node)

        if node == end:
            path = _trace_path(parent, start, end)
            return _pack(path, steps, len(parent), len(path) - 1, t0)

        for nb in _neighbors(grid, *node, rows, cols):
            if nb not in parent:
                parent[nb] = node
                queue.append(nb)

    return _pack([], steps, len(parent), 0, t0)


def dfs(grid, start, end, rows, cols):
    stack = [start]
    parent = {}
    visited = set()
    steps = []
    t0 = time.perf_counter()

    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        steps.append(node)

        if node == end:
            path = _trace_path(parent, start, end)
            return _pack(path, steps, len(visited), len(path) - 1, t0)

        for nb in _neighbors(grid, *node, rows, cols):
            if nb not in visited:
                if nb not in parent:
                    parent[nb] = node
                stack.append(nb)

    return _pack([], steps, len(visited), 0, t0)


def _manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(grid, start, end, rows, cols):
    h0 = _manhattan(start, end)
    heap = [(h0, 0, 0, start)]
    g = {start: 0}
    parent = {start: None}
    closed = set()
    steps = []
    uid = 1
    t0 = time.perf_counter()

    while heap:
        _f, g_val, _uid, node = heapq.heappop(heap)
        if node in closed:
            continue
        closed.add(node)
        steps.append(node)

        if node == end:
            path = _trace_path(parent, start, end)
            return _pack(path, steps, len(closed), g[end], t0)

        for nb in _neighbors(grid, *node, rows, cols):
            ng = g[node] + 1
            if nb not in g or ng < g[nb]:
                g[nb] = ng
                parent[nb] = node
                f = ng + _manhattan(nb, end)
                heapq.heappush(heap, (f, ng, uid, nb))
                uid += 1

    return _pack([], steps, len(closed), 0, t0)


def ucs(grid, start, end, rows, cols):
    # Uniform Cost Search — orders by cumulative path cost.
    # On unit-weight grids this matches BFS behavior, but the
    # expansion order makes the cost-first logic explicit.
    heap = [(0, 0, start)]
    cost = {start: 0}
    parent = {start: None}
    closed = set()
    steps = []
    uid = 1
    t0 = time.perf_counter()

    while heap:
        c, _uid, node = heapq.heappop(heap)
        if node in closed:
            continue
        closed.add(node)
        steps.append(node)

        if node == end:
            path = _trace_path(parent, start, end)
            return _pack(path, steps, len(closed), cost[end], t0)

        for nb in _neighbors(grid, *node, rows, cols):
            nc = cost[node] + 1
            if nb not in cost or nc < cost[nb]:
                cost[nb] = nc
                parent[nb] = node
                heapq.heappush(heap, (nc, uid, nb))
                uid += 1

    return _pack([], steps, len(closed), 0, t0)


def bidirectional(grid, start, end, rows, cols):
    if start == end:
        return _pack([start], [start], 1, 0, time.perf_counter())

    fq = deque([start])
    bq = deque([end])
    fp = {start: None}
    bp = {end: None}
    steps = []
    t0 = time.perf_counter()

    while fq or bq:
        if fq:
            node = fq.popleft()
            steps.append(('F', node))
            if node in bp:
                path = _join_paths(fp, bp, node)
                all_steps = [n for _, n in steps]
                return _pack(path, all_steps, len(fp) + len(bp) - 1, len(path) - 1, t0)
            for nb in _neighbors(grid, *node, rows, cols):
                if nb not in fp:
                    fp[nb] = node
                    fq.append(nb)

        if bq:
            node = bq.popleft()
            steps.append(('B', node))
            if node in fp:
                path = _join_paths(fp, bp, node)
                all_steps = [n for _, n in steps]
                return _pack(path, all_steps, len(fp) + len(bp) - 1, len(path) - 1, t0)
            for nb in _neighbors(grid, *node, rows, cols):
                if nb not in bp:
                    bp[nb] = node
                    bq.append(nb)

    all_steps = [n for _, n in steps]
    return _pack([], all_steps, len(fp) + len(bp), 0, t0)


def _join_paths(fp, bp, meet):
    fwd = []
    n = meet
    while n is not None:
        fwd.append(n)
        n = fp.get(n)
    fwd.reverse()

    bwd = []
    n = bp.get(meet)
    while n is not None:
        bwd.append(n)
        n = bp.get(n)

    return fwd + bwd


def _pack(path, steps, nodes, cost, t0):
    return {
        'path':     path,
        'steps':    steps,
        'nodes':    nodes,
        'path_len': len(path),
        'cost':     cost,
        'ms':       round((time.perf_counter() - t0) * 1000, 2),
        'found':    len(path) > 0,
    }


ALGORITHMS = {
    'BFS':           bfs,
    'DFS':           dfs,
    'A*':            astar,
    'UCS':           ucs,
    'Bidirectional': bidirectional,
}


def run_algorithm(name, grid, start, end, rows, cols):
    fn = ALGORITHMS.get(name)
    if fn is None:
        raise ValueError(f"Unknown algorithm: {name}")
    return fn(grid, start, end, rows, cols)
