import random


def generate_maze(rows, cols, start, end):
    """Iterative recursive-backtracker maze. Carves passages on odd cells."""
    grid = [[1] * cols for _ in range(rows)]

    # Anchor the carving to an odd coordinate near top-left
    sr, sc = 1, 1
    grid[sr][sc] = 0
    stack = [(sr, sc)]

    while stack:
        r, c = stack[-1]
        candidates = []
        for dr, dc in [(0, 2), (0, -2), (2, 0), (-2, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                candidates.append((dr, dc, nr, nc))

        if candidates:
            dr, dc, nr, nc = random.choice(candidates)
            grid[r + dr // 2][c + dc // 2] = 0   # knock down wall between
            grid[nr][nc] = 0
            stack.append((nr, nc))
        else:
            stack.pop()

    # Guarantee start and end cells plus one adjacent cell are open
    for pos in (start, end):
        r, c = pos
        grid[r][c] = 0
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                grid[nr][nc] = 0
                break

    return grid


def generate_random_walls(rows, cols, start, end, density=0.28):
    """Scatter walls randomly while keeping start/end clear."""
    protected = {start, end}

    # Also protect the immediate ring around start/end so they're reachable
    for pos in (start, end):
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = pos[0] + dr, pos[1] + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                protected.add((nr, nc))

    grid = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if (r, c) not in protected and random.random() < density:
                grid[r][c] = 1

    return grid
