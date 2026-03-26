**Name:** Yatharth Singh

**Registration No:** 25BAI10657

# Project Statement
## Algorithm Visualizer + Performance Comparator

**Course:** CSA2001 — Fundamentals in AI and ML
**Submission Type:** Bring Your Own Project (BYOP)
**Course Outcomes Addressed:** CO2, CO4

---

## 1. The Problem I Chose to Solve

When I was going through the search algorithms unit in this course, I hit a point where I could write out the pseudocode for BFS and A* without thinking, but still wasn't confident I actually *understood* them. I knew BFS was optimal on unit-cost graphs. I knew A* used a heuristic. But what did that look like in practice? What exactly makes A* faster? Why does DFS so often produce a terrible path even when a short one is sitting right there?

I started looking for something I could just run and watch. Most visualizers I found online were tied to a browser, had weird dependencies, or only showed one algorithm at a time with no way to compare. None of them were something I could open locally, tweak, and actually learn from.

That felt like a problem worth solving — not just for me, but for anyone going through this course. The idea I started with was simple: what if you could draw a maze, press a button, and watch five different search algorithms try to solve the exact same problem?

---

## 2. Why This Matters

Search algorithms underpin a massive chunk of AI. Navigation, game agents, robot path planning, puzzle solving — it all comes back to some version of what CO2 covers. If you don't have a real feel for how these strategies differ from each other, everything built on top of them stays vague.

The way I think most students learn this material — including how I was learning it — is in isolation. BFS in one section, DFS in another, A* in a third. You never actually watch them compete on the same problem. And that comparison is where things start to click. Seeing BFS flood-fill an entire room while A* cuts a direct line toward the goal says more than a paragraph of text ever could.

---

## 3. What I Built

The project is a desktop application written entirely in Python. No external libraries — just the standard library. It renders a grid you can draw walls on, place a start and end node wherever you want, and then run any of five search algorithms with a live animation.

The five algorithms are BFS, DFS, A*, UCS, and Bidirectional BFS. Each one runs through the grid, records every cell it visits, and the app plays that sequence back as an animation. Once the path is found, the stats panel shows nodes explored, path length, path cost, and time in milliseconds.

There's also a "Compare All" button that runs all five algorithms silently on the same grid and puts the results into a table. The best value in each column turns green. That table is honestly the most useful feature for studying the differences — you can see at a glance which algorithm wasted the most effort and which one found the shortest path.

Beyond that there's a maze generator, a random walls mode, adjustable animation speed, and the ability to stop mid-run and restart.

---

## 4. How I Approached Building It

I split things into four files from the start. The algorithms are in `algorithms.py`, maze logic in `maze.py`, the UI in `app.py`, and `main.py` just launches everything. The best part of this structure is that the algorithm code has zero knowledge that a UI exists — it takes a grid and returns a result. I could test everything from the terminal without opening a window, which made debugging far less painful.

Every algorithm returns the same dictionary: path, steps, nodes explored, path length, cost, time. That consistent format meant adding a new algorithm later would only require writing one function and registering it — nothing else changes. I didn't plan this that carefully upfront, it just became obvious it was the right call after the second algorithm.

Animation gave me more trouble than expected. My first attempt used a loop with `time.sleep()` and the window completely froze — tkinter runs everything on one thread. Switching to `root.after()` callbacks fixed it; each frame gets scheduled and hands control back to the event loop in between. Once I understood that pattern, the rest came together smoothly.

---

## 5. What I Noticed Once It Was Running

A few things surprised me once I could actually see the algorithms go.

DFS explores fewer total nodes than BFS on a lot of grids. I didn't expect that. But the path it lands on is usually much longer and more winding, which makes the "fast but not optimal" trade-off feel real instead of just something written in a textbook.

A* was the most satisfying to watch. On an open grid with the goal far away, it barely glances at cells behind the start — it just moves toward the target. Compared to BFS radiating outward in every direction, the difference in wasted exploration is genuinely striking.

UCS and BFS produce identical results on this grid because every step costs 1. I left a note about this in the README because it's actually a useful thing to understand — they only diverge when edge weights differ.

Bidirectional BFS often has the lowest node count in the comparison table. Seeing that number be consistently lower than the others makes the "searching from both ends cuts the space in half" claim feel like a concrete fact rather than a hand-wavy theoretical point.

---

## 6. Challenges I Ran Into

The trickiest part was reconstructing the path for Bidirectional BFS. When the two frontiers meet at some node, you have to walk backward through two separate parent dictionaries and join them correctly. Getting the direction wrong produces a path that doubles back or goes the wrong way. I had to sketch it on paper before the logic became clear enough to code.

Maze generation had a subtle issue too. The recursive backtracker carves passages on odd-coordinate cells, so if the start or end node lands on an even coordinate — which is a wall in the generated structure — it ends up trapped with no way in or out. I fixed it by forcibly opening the start/end cells and one neighbour after generation, so they're always reachable regardless of where the user placed them.

---

## 7. What I Actually Learned

Implementing these algorithms properly taught me more about them than studying for exams did. You cannot fake A* — you have to understand why ordering by f = g + h produces an optimal result, or the heap entries come out wrong and the whole thing breaks. Same with Bidirectional BFS — "meet in the middle" sounds obvious until you have to figure out what that actually means in terms of two dictionaries and an index.

I also came away with a better sense of why clean interfaces between modules matter. Because the UI never calls algorithms directly — it just reads the result dictionary — I could rewrite any algorithm without touching the UI code at all. I'd read about separation of concerns before but hadn't really felt the value of it until I was in the middle of this project and changing things became genuinely easy.

---

## 8. References

1. Russell, S. & Norvig, P. — *Artificial Intelligence: A Modern Approach*, 3rd Edition. Prentice Hall, 2009. *(Main reference for all five algorithms — Chapters 3 and 4)*
2. Python Software Foundation — `tkinter` documentation. https://docs.python.org/3/library/tkinter.html
3. Python Software Foundation — `heapq` module documentation. https://docs.python.org/3/library/heapq.html
4. Jamis Buck — *Mazes for Programmers*, Pragmatic Bookshelf, 2015. *(Recursive backtracker algorithm)*
