## Author
**Name:** Yatharth Singh

**Reg No:** 25BAI10657
**Institution:** VIT Bhopal University

# Algorithm Visualizer — Pathfinding Explorer

An interactive desktop application that **animates five classical AI search algorithms** on a hand-drawn grid and lets you measure their performance side-by-side in real time.

Built as a BYOP capstone submission for **CSA2001 – Fundamentals in AI and ML**
(Course Outcome CO2: Search Strategies · CO4: Analysis & Design using AI Techniques)

---

## Algorithms Covered

| Algorithm | Strategy | Optimal? | Complete? |
|---|---|---|---|
| **BFS** | FIFO queue — expands level by level | ✓ on unit-cost grids | ✓ |
| **DFS** | LIFO stack — goes deep before backtracking | ✗ | ✓ (finite grid) |
| **A\*** | Priority by *g* + *h* (Manhattan heuristic) | ✓ | ✓ |
| **UCS** | Priority by cumulative cost only | ✓ | ✓ |
| **Bidirectional BFS** | Two simultaneous BFS frontiers meeting in the middle | ✓ | ✓ |

---

## Features

- **Live animation** — watch each algorithm explore cells step-by-step with per-algorithm colours
- **Adjustable speed** — Slow / Normal / Fast / Instant (no animation, pure benchmark)
- **Performance stats** — Nodes explored, path length, path cost, elapsed time (ms)
- **Compare All mode** — runs all five algorithms silently on the same grid; table highlights the winner (green) in every column
- **Interactive grid** — left-click drag to draw walls, right-click drag to erase
- **Draw modes** — place/erase walls or reposition Start and End anywhere on the grid
- **Maze generator** — iterative recursive-backtracker producing perfect mazes with guaranteed solvability
- **Random walls** — scatter obstacles at ~28 % density with protected start/end zones
- **Reset / Clear** — reset only the visual overlay (walls stay) or wipe everything

---

## Requirements

- **Python 3.9 or later**
- **tkinter** — ships with CPython on Windows and macOS

On Ubuntu / Debian Linux:
```bash
sudo apt-get install python3-tk
```

No third-party packages are needed. Everything uses the Python standard library.

---

## Setup & Run

```bash
# 1. Clone or download the project folder
git clone https://github.com/YatharthSingh-VIT/Vityarthi-Project-AI-and-ML.git
cd algo-visualizer

# 2. (Optional) create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Launch
python main.py
```

The application window opens immediately. No additional configuration is required.

---

## File Overview

```
algo_visualizer/
├── main.py          Entry point — sets up the module path and launches the app
├── app.py           Tkinter UI (grid canvas, sidebar, comparison panel, animation loop)
├── algorithms.py    BFS, DFS, A*, UCS, Bidirectional BFS — pure Python, no dependencies
├── maze.py          Maze generator (recursive backtracker) + random wall scatterer
├── requirements.txt Dependency declaration (stdlib only)
└── README.md        This file
```

---

## How to Use

### Drawing on the grid

| Action | Result |
|---|---|
| Left-click / drag on empty cell | Place a wall |
| Right-click / drag on any cell | Erase a wall |
| Draw Mode → **Start ▶**, then click | Move the green start node |
| Draw Mode → **End ●**, then click | Move the red end node |
| **🗺 Generate Maze** button | Fill grid with a perfect recursive-backtracker maze |
| **⬛ Random Walls** button | Scatter walls at ~28 % density |
| **⟳ Reset View** | Clear visited/path colours, keep walls |
| **✕ Clear All** | Remove all walls (start and end stay) |

### Running a single algorithm

1. Pick an algorithm from the dropdown.
2. Choose a speed (Slow → Instant).
3. Click **▶ Visualize**.
   - Visited cells animate in the algorithm's dedicated colour.
   - The final shortest path overlays in gold/yellow.
   - **Live Stats** (left panel) update in real time.
4. Click **⏹ Stop** at any point to halt the animation.

### Comparing all algorithms at once

Click **⚡ Compare All** — all five algorithms run silently on the current grid. The **Comparison Table** (right panel) shows nodes explored, path length, and time for each; the lowest value in each column is highlighted green.

---

## Colour Reference

| Colour | Meaning |
|---|---|
| Green cell | Start node |
| Red cell | End node |
| Dark grey | Wall |
| Muted blue | BFS visited |
| Muted purple | DFS visited |
| Muted green | A\* visited |
| Muted yellow | UCS visited |
| Muted orange | Bidirectional visited |
| Gold / amber | Final path |

---

## Extending the Project

- **Weighted cells** — introduce terrain costs (road / grass / mud) so UCS and A\* diverge visibly from BFS.
- **Diagonal movement** — change `_neighbors()` in `algorithms.py` to include 8-directional moves.
- **Greedy Best-First Search** — add a variant of A\* that ignores *g* to show why heuristic-only search isn't optimal.
- **Export results** — write comparison data to CSV after a run.
- **Larger grids** — ROWS / COLS constants in `app.py` are trivially adjustable.

---

## Course Alignment (CSA2001)

| Outcome | How this project addresses it |
|---|---|
| **CO2** | Implements and visually contrasts uninformed (BFS, DFS, UCS) and informed (A\*) search strategies, plus a bidirectional variant |
| **CO4** | Provides a live performance comparison — nodes, cost, and time — enabling analysis of algorithm trade-offs on the same problem instance |
| **CO1** | Demonstrates capabilities and limitations (DFS non-optimality, BFS memory cost, A\* heuristic advantage) through direct observation |

Reference: S. Russell & P. Norvig, *Artificial Intelligence: A Modern Approach*, 3rd ed. — Chapters 3 & 4.
