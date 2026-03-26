import tkinter as tk
from tkinter import ttk
import random
import ctypes

# ── Windows DPI Awareness (fix blurriness) ────────────────────────────────────
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)   # Per-Monitor V2
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()    # Fallback
    except Exception:
        pass

from algorithms import run_algorithm, ALGORITHMS
from maze import generate_maze, generate_random_walls

# ── Grid dimensions ──────────────────────────────────────────────────────────
ROWS, COLS = 22, 34
CELL       = 26
GAP        = 2

# ── Colour palette ────────────────────────────────────────────────────────────
T = {
    'bg':       '#0d1117',
    'surface':  '#161b22',
    'card':     '#21262d',
    'border':   '#30363d',
    'text':     '#e6edf3',
    'dim':      '#8b949e',
    'blue':     '#58a6ff',
    'green':    '#3fb950',
    'yellow':   '#d29922',
    'red':      '#f85149',
    'purple':   '#bc8cff',
    'orange':   '#db6d28',
    # grid cell states
    'empty':    '#1c2128',
    'wall':     '#484f58',
    'start':    '#2ea043',
    'end':      '#da3633',
    'visited':  '#1f3552',
    'path':     '#b08800',
}

ALGO_COLORS = {
    'BFS':           '#58a6ff',
    'DFS':           '#bc8cff',
    'A*':            '#3fb950',
    'UCS':           '#d29922',
    'Bidirectional': '#f0883e',
}

# delay_ms, batch_size  (batch=0 → instant, no animation)
SPEED = {
    'Slow':    (50, 1),
    'Normal':  (18, 2),
    'Fast':    (6,  6),
    'Instant': (0,  0),
}

EMPTY, WALL = 0, 1


# ── Helpers ──────────────────────────────────────────────────────────────────

def hex_blend(c1: str, c2: str, t: float) -> str:
    """Linear blend between two #rrggbb colours. t=0→c1, t=1→c2."""
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f'#{r:02x}{g:02x}{b:02x}'


# ── Application ───────────────────────────────────────────────────────────────

class AlgoVizApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Algorithm Visualizer  ·  Pathfinding Explorer")
        self.root.configure(bg=T['bg'])

        # state
        self.grid      = [[EMPTY] * COLS for _ in range(ROWS)]
        self.start     = (2, 2)
        self.end       = (ROWS - 3, COLS - 3)
        self.running   = False
        self._job      = None
        self._cache    = {}      # algo → result after compare

        self._build_ui()
        self._draw_grid()
        self._refresh_markers()

        # Ensure window is tall enough for all sidebar content
        self.root.update_idletasks()
        req_w = self.root.winfo_reqwidth()
        req_h = self.root.winfo_reqheight()
        screen_h = self.root.winfo_screenheight()
        final_h = min(max(req_h, 820), screen_h - 80)
        self.root.geometry(f"{req_w}x{final_h}")
        self.root.minsize(req_w, final_h)
        self.root.resizable(False, False)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_titlebar()
        body = tk.Frame(self.root, bg=T['bg'])
        body.pack(fill='both', expand=True)

        self._build_left(body)
        self._build_center(body)
        self._build_right(body)
        self._build_statusbar()

    # title bar ----------------------------------------------------------------

    def _build_titlebar(self):
        bar = tk.Frame(self.root, bg=T['surface'], height=48)
        bar.pack(fill='x')
        bar.pack_propagate(False)

        tk.Label(bar, text='  ⬡  Algorithm Visualizer',
                 bg=T['surface'], fg=T['text'],
                 font=('Segoe UI', 14, 'bold')).pack(side='left', padx=6, pady=10)

        tk.Label(bar, text='BFS · DFS · A* · UCS · Bidirectional Search',
                 bg=T['surface'], fg=T['dim'],
                 font=('Segoe UI', 9)).pack(side='left', padx=8)

        self._title_tag = tk.Label(bar, text='', bg=T['surface'],
                                   font=('Segoe UI', 9, 'bold'))
        self._title_tag.pack(side='right', padx=16)

    # left sidebar -------------------------------------------------------------

    def _build_left(self, parent):
        frame = tk.Frame(parent, bg=T['surface'], width=260)
        frame.pack(side='left', fill='y', padx=(0, 1))
        frame.pack_propagate(False)

        self._sec(frame, 'Algorithm')
        self.algo_var = tk.StringVar(value='BFS')
        self._style_combobox()
        cb = ttk.Combobox(frame, textvariable=self.algo_var,
                          values=list(ALGORITHMS.keys()),
                          state='readonly', style='Dark.TCombobox',
                          font=('Segoe UI', 10))
        cb.pack(fill='x', padx=10, pady=3)
        cb.bind('<<ComboboxSelected>>', self._on_algo_changed)

        self._sec(frame, 'Speed')
        spd_grid = tk.Frame(frame, bg=T['surface'])
        spd_grid.pack(fill='x', padx=10, pady=2)
        self.speed_var = tk.StringVar(value='Normal')
        for i, s in enumerate(('Slow', 'Normal', 'Fast', 'Instant')):
            tk.Radiobutton(spd_grid, text=s, variable=self.speed_var, value=s,
                           bg=T['surface'], fg=T['text'], activebackground=T['surface'],
                           selectcolor=T['card'], font=('Segoe UI', 9),
                           indicatoron=1, cursor='hand2'
                           ).grid(row=i // 2, column=i % 2, sticky='w', padx=2, pady=0)
        spd_grid.columnconfigure(0, weight=1)
        spd_grid.columnconfigure(1, weight=1)

        self._sec(frame, 'Draw Mode')
        grid_modes = tk.Frame(frame, bg=T['surface'])
        grid_modes.pack(fill='x', padx=10, pady=2)
        self.mode_var = tk.StringVar(value='wall')
        modes = [('Wall ✏', 'wall'), ('Erase ⌫', 'erase'),
                 ('Start ▶', 'start'), ('End ●', 'end')]
        for i, (lbl, val) in enumerate(modes):
            rb = tk.Radiobutton(grid_modes, text=lbl, variable=self.mode_var, value=val,
                                bg=T['surface'], fg=T['text'], activebackground=T['surface'],
                                selectcolor=T['card'], font=('Segoe UI', 9),
                                indicatoron=0, relief='flat', bd=1, pady=2,
                                cursor='hand2')
            rb.grid(row=i // 2, column=i % 2, padx=2, pady=1, sticky='ew')
        grid_modes.columnconfigure(0, weight=1)
        grid_modes.columnconfigure(1, weight=1)

        self._sec(frame, 'Actions')
        self.run_btn = self._btn(frame, '▶  Visualize',    self._start_viz,      T['green'])
        self._btn(frame, '⚡  Compare All',                self._compare_all,    T['orange'])
        self._btn(frame, '🗺  Generate Maze',              self._gen_maze,       T['purple'])
        self._btn(frame, '⬛  Random Walls',               self._random_walls,   T['blue'])
        self._btn(frame, '⟳  Reset View',                  self._reset_view,     T['dim'])
        self._btn(frame, '✕  Clear All',                   self._clear_all,      T['red'])

        self._sec(frame, 'Live Stats')
        self.sv_nodes = self._stat_row(frame, 'Nodes')
        self.sv_path  = self._stat_row(frame, 'Path Len')
        self.sv_cost  = self._stat_row(frame, 'Cost')
        self.sv_time  = self._stat_row(frame, 'Time')

        tk.Frame(frame, bg=T['surface']).pack(fill='both', expand=True)

        self.algo_dot = tk.Label(frame, text='', bg=T['surface'],
                                 font=('Segoe UI', 9, 'bold'))
        self.algo_dot.pack(pady=(0, 6))
        self._on_algo_changed()

    # center canvas ------------------------------------------------------------

    def _build_center(self, parent):
        wrapper = tk.Frame(parent, bg=T['bg'])
        wrapper.pack(side='left', fill='both', expand=True)

        cw = COLS * (CELL + GAP) + GAP
        ch = ROWS * (CELL + GAP) + GAP

        self.canvas = tk.Canvas(wrapper, width=cw, height=ch,
                                bg=T['bg'], highlightthickness=0,
                                cursor='crosshair')
        self.canvas.pack(padx=14, pady=14)

        self.canvas.bind('<Button-1>',   self._mouse_press)
        self.canvas.bind('<B1-Motion>',  self._mouse_drag)
        self.canvas.bind('<Button-3>',   self._erase_press)
        self.canvas.bind('<B3-Motion>',  self._erase_drag)

    # right panel --------------------------------------------------------------

    def _build_right(self, parent):
        frame = tk.Frame(parent, bg=T['surface'], width=340)
        frame.pack(side='right', fill='y', padx=(1, 0))
        frame.pack_propagate(False)

        # ── Comparison Table FIRST (most important, always visible) ──
        self._sec(frame, 'Comparison Table')
        self.cmp_frame = tk.Frame(frame, bg=T['card'], bd=0, relief='flat',
                                  highlightbackground=T['border'], highlightthickness=1)
        self.cmp_frame.pack(fill='x', padx=8, pady=4)
        self._draw_empty_table()

        # ── Combined Legend & Algorithm Colors in compact grid ──
        self._sec(frame, 'Legend & Colors')
        legend_grid = tk.Frame(frame, bg=T['surface'])
        legend_grid.pack(fill='x', padx=10, pady=2)

        legend_items = [
            (T['start'],   'Start'),
            (T['end'],     'End'),
            (T['wall'],    'Wall'),
            (T['visited'], 'Visited'),
            (T['path'],    'Path'),
            (T['empty'],   'Empty'),
        ]
        for i, (color, label) in enumerate(legend_items):
            row_i, col_i = divmod(i, 3)
            cell = tk.Frame(legend_grid, bg=T['surface'])
            cell.grid(row=row_i, column=col_i, padx=2, pady=2, sticky='w')
            tk.Label(cell, bg=color, width=2, height=1
                     ).pack(side='left', padx=(0, 4))
            tk.Label(cell, text=label, bg=T['surface'], fg=T['text'],
                     font=('Segoe UI', 9)).pack(side='left')
        for c in range(3):
            legend_grid.columnconfigure(c, weight=1)

        # Algorithm color indicators (compact row)
        algo_grid = tk.Frame(frame, bg=T['surface'])
        algo_grid.pack(fill='x', padx=10, pady=(4, 2))
        for i, (algo, color) in enumerate(ALGO_COLORS.items()):
            cell = tk.Frame(algo_grid, bg=T['surface'])
            cell.grid(row=i // 3, column=i % 3, padx=2, pady=1, sticky='w')
            tk.Label(cell, bg=color, width=2, height=1
                     ).pack(side='left', padx=(0, 4))
            tk.Label(cell, text=algo, bg=T['surface'], fg=T['text'],
                     font=('Segoe UI', 9)).pack(side='left')
        for c in range(3):
            algo_grid.columnconfigure(c, weight=1)

        tk.Frame(frame, bg=T['surface']).pack(fill='both', expand=True)

        tk.Label(frame,
                 text='Left click · drag = draw walls\nRight click · drag = erase',
                 bg=T['surface'], fg=T['dim'],
                 font=('Segoe UI', 9), justify='center').pack(pady=8)

    # status bar ---------------------------------------------------------------

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=T['card'], height=26)
        bar.pack(fill='x', side='bottom')
        bar.pack_propagate(False)

        self.status_var = tk.StringVar(value='Ready  ·  Draw walls then click ▶ Visualize')
        tk.Label(bar, textvariable=self.status_var,
                 bg=T['card'], fg=T['dim'],
                 font=('Segoe UI', 8)).pack(side='left', padx=12, pady=4)

        info = f'Grid: {ROWS}×{COLS}   Algorithms: BFS, DFS, A*, UCS, Bidirectional'
        tk.Label(bar, text=info, bg=T['card'], fg=T['dim'],
                 font=('Segoe UI', 8)).pack(side='right', padx=12)

    # ── Widget helpers ────────────────────────────────────────────────────────

    def _sec(self, parent, label):
        row = tk.Frame(parent, bg=T['surface'])
        row.pack(fill='x', padx=10, pady=(8, 0))
        tk.Label(row, text=label.upper(), bg=T['surface'], fg=T['dim'],
                 font=('Segoe UI', 8, 'bold')).pack(anchor='w')
        tk.Frame(parent, bg=T['border'], height=1).pack(fill='x', padx=10, pady=(2, 2))

    def _btn(self, parent, text, cmd, fg):
        f = tk.Frame(parent, bg=T['surface'])
        f.pack(fill='x', padx=10, pady=1)
        b = tk.Button(f, text=text, command=cmd,
                      bg=T['card'], fg=fg,
                      activebackground=T['border'], activeforeground=fg,
                      relief='flat', bd=0, font=('Segoe UI', 9, 'bold'),
                      pady=4, cursor='hand2')
        b.pack(fill='x')
        return b

    def _stat_row(self, parent, label):
        row = tk.Frame(parent, bg=T['surface'])
        row.pack(fill='x', padx=10, pady=1)
        tk.Label(row, text=label, bg=T['surface'], fg=T['dim'],
                 font=('Segoe UI', 9), anchor='w', width=10
                 ).pack(side='left')
        var = tk.StringVar(value='—')
        tk.Label(row, textvariable=var, bg=T['surface'], fg=T['text'],
                 font=('Segoe UI', 9, 'bold'), anchor='e'
                 ).pack(side='right', fill='x', expand=True)
        return var

    def _style_combobox(self):
        s = ttk.Style()
        s.theme_use('clam')
        s.configure('Dark.TCombobox',
                    fieldbackground=T['card'], background=T['card'],
                    foreground=T['text'], selectbackground=T['card'],
                    selectforeground=T['text'], bordercolor=T['border'],
                    arrowcolor=T['dim'], insertcolor=T['text'])
        s.map('Dark.TCombobox',
              fieldbackground=[('readonly', T['card'])],
              foreground=[('readonly', T['text'])])

    # ── Grid canvas ───────────────────────────────────────────────────────────

    def _cell_bbox(self, r, c):
        x0 = GAP + c * (CELL + GAP)
        y0 = GAP + r * (CELL + GAP)
        return x0, y0, x0 + CELL, y0 + CELL

    def _draw_grid(self):
        self.canvas.delete('all')
        self._rects = {}
        for r in range(ROWS):
            for c in range(COLS):
                x0, y0, x1, y1 = self._cell_bbox(r, c)
                rid = self.canvas.create_rectangle(
                    x0, y0, x1, y1,
                    fill=T['empty'], outline='')
                self._rects[(r, c)] = rid

    def _paint(self, r, c, color):
        key = (r, c)
        if key in self._rects:
            self.canvas.itemconfig(self._rects[key], fill=color)

    def _refresh_markers(self):
        self._paint(*self.start, T['start'])
        self._paint(*self.end,   T['end'])

    def _cell_at(self, x, y):
        c = (x - GAP) // (CELL + GAP)
        r = (y - GAP) // (CELL + GAP)
        return (r, c) if 0 <= r < ROWS and 0 <= c < COLS else None

    # ── Mouse interaction ─────────────────────────────────────────────────────

    def _mouse_press(self, ev):
        pos = self._cell_at(ev.x, ev.y)
        if pos:
            self._apply_mode(pos)

    def _mouse_drag(self, ev):
        pos = self._cell_at(ev.x, ev.y)
        if pos:
            self._apply_mode(pos)

    def _erase_press(self, ev):
        pos = self._cell_at(ev.x, ev.y)
        if pos and pos not in (self.start, self.end):
            self.grid[pos[0]][pos[1]] = EMPTY
            self._paint(*pos, T['empty'])

    def _erase_drag(self, ev):
        self._erase_press(ev)

    def _apply_mode(self, pos):
        r, c = pos
        mode = self.mode_var.get()

        if mode == 'wall':
            if pos not in (self.start, self.end):
                self.grid[r][c] = WALL
                self._paint(r, c, T['wall'])

        elif mode == 'erase':
            if pos not in (self.start, self.end):
                self.grid[r][c] = EMPTY
                self._paint(r, c, T['empty'])

        elif mode == 'start':
            prev = self.start
            self.start = pos
            self.grid[prev[0]][prev[1]] = EMPTY
            self._paint(*prev, T['empty'] if self.grid[prev[0]][prev[1]] == EMPTY else T['wall'])
            self.grid[r][c] = EMPTY
            self._paint(r, c, T['start'])

        elif mode == 'end':
            prev = self.end
            self.end = pos
            self.grid[prev[0]][prev[1]] = EMPTY
            self._paint(*prev, T['empty'] if self.grid[prev[0]][prev[1]] == EMPTY else T['wall'])
            self.grid[r][c] = EMPTY
            self._paint(r, c, T['end'])

    # ── Algorithm events ──────────────────────────────────────────────────────

    def _on_algo_changed(self, _ev=None):
        algo  = self.algo_var.get()
        color = ALGO_COLORS.get(algo, T['text'])
        self.algo_dot.config(text=f'● {algo}', fg=color)
        self._title_tag.config(text=f'Selected: {algo}', fg=color)

    def _start_viz(self):
        if self.running:
            self._stop()
            return

        self._reset_view()
        algo   = self.algo_var.get()
        result = run_algorithm(algo, self.grid, self.start, self.end, ROWS, COLS)
        self._cache[algo] = result

        found = result['found']
        self.status_var.set(
            f'Running {algo}  ·  {len(result["steps"])} nodes to explore'
            if found else f'{algo}  ·  No path found — {len(result["steps"])} nodes explored'
        )

        delay, batch = SPEED[self.speed_var.get()]
        vis_color    = ALGO_COLORS.get(algo, T['blue'])
        vis_fill     = hex_blend(vis_color, T['empty'], 0.55)

        if batch == 0:
            self._draw_instant(result, vis_fill)
            self._show_stats(result)
            return

        self.running = True
        self.run_btn.config(text='⏹  Stop')
        self._animate(result['steps'], result['path'], vis_fill, delay, batch, result)

    def _draw_instant(self, result, vis_fill):
        for pos in result['steps']:
            if pos not in (self.start, self.end):
                self._paint(*pos, vis_fill)
        for pos in result['path']:
            if pos not in (self.start, self.end):
                self._paint(*pos, T['path'])
        self._refresh_markers()

    def _animate(self, steps, path, vis_fill, delay, batch, result):
        total = len(steps)

        def step_visit(i):
            if not self.running:
                return
            end_i = min(i + batch, total)
            for k in range(i, end_i):
                pos = steps[k]
                if pos not in (self.start, self.end):
                    self._paint(*pos, vis_fill)
            self.sv_nodes.set(str(end_i))

            if end_i < total:
                self._job = self.root.after(delay, step_visit, end_i)
            else:
                self._job = self.root.after(delay, step_path, 0)

        def step_path(i):
            if not self.running:
                return
            if i < len(path):
                pos = path[i]
                if pos not in (self.start, self.end):
                    self._paint(*pos, T['path'])
                self._job = self.root.after(15, step_path, i + 1)
            else:
                self._refresh_markers()
                self._show_stats(result)
                self.running = False
                self.run_btn.config(text='▶  Visualize')
                done_txt = 'Path found!' if result['found'] else 'No path exists'
                self.status_var.set(
                    f'{self.algo_var.get()}  ·  {done_txt}  '
                    f'·  {result["nodes"]} nodes  ·  length {result["path_len"]}  '
                    f'·  {result["ms"]} ms'
                )

        step_visit(0)

    def _stop(self):
        self.running = False
        if self._job:
            self.root.after_cancel(self._job)
            self._job = None
        self.run_btn.config(text='▶  Visualize')
        self.status_var.set('Stopped.')

    def _show_stats(self, r):
        self.sv_nodes.set(str(r['nodes']))
        self.sv_path.set(str(r['path_len']) if r['found'] else '—')
        self.sv_cost.set(str(r['cost'])     if r['found'] else '—')
        self.sv_time.set(f"{r['ms']} ms")

    # ── Compare all ───────────────────────────────────────────────────────────

    def _compare_all(self):
        if self.running:
            return
        self._reset_view()
        self.status_var.set('Running all algorithms…')
        self.root.update_idletasks()

        results = {algo: run_algorithm(algo, self.grid, self.start, self.end, ROWS, COLS)
                   for algo in ALGORITHMS}
        self._cache = results

        # Show the currently selected algo's visited region
        algo     = self.algo_var.get()
        res      = results[algo]
        vc       = ALGO_COLORS.get(algo, T['blue'])
        vis_fill = hex_blend(vc, T['empty'], 0.55)

        self._draw_instant(res, vis_fill)
        self._show_stats(res)
        self._draw_comparison_table(results)

        best_algo = min(
            (a for a, r in results.items() if r['found']),
            key=lambda a: results[a]['path_len'],
            default='—'
        )
        self.status_var.set(
            f'Comparison complete  ·  Shortest path: {best_algo}  '
            f'·  Showing: {algo}'
        )

    def _draw_comparison_table(self, results):
        for w in self.cmp_frame.winfo_children():
            w.destroy()

        headers = ['Algorithm', 'Nodes', 'Path', 'Cost', 'Time']
        col_widths = [10, 7, 6, 6, 7]
        num_cols = len(headers)

        # Header row with accent background
        hdr_bg = T['border']
        for ci, (h, w) in enumerate(zip(headers, col_widths)):
            tk.Label(self.cmp_frame, text=h, bg=hdr_bg, fg=T['text'],
                     font=('Segoe UI', 9, 'bold'), width=w,
                     anchor='center' if ci > 0 else 'w',
                     padx=4, pady=4
                     ).grid(row=0, column=ci, padx=(0, 1), pady=(0, 1), sticky='ew')

        # Separator
        tk.Frame(self.cmp_frame, bg=T['blue'], height=2).grid(
            row=1, column=0, columnspan=num_cols, sticky='ew')

        found_results = {a: r for a, r in results.items() if r['found']}
        best_nodes = min((r['nodes']    for r in found_results.values()), default=None)
        best_path  = min((r['path_len'] for r in found_results.values()), default=None)
        best_cost  = min((r['cost']     for r in found_results.values()), default=None)
        best_ms    = min((r['ms']       for r in found_results.values()), default=None)

        row_bg_even = T['card']
        row_bg_odd  = hex_blend(T['card'], T['surface'], 0.5)

        for ri, (algo, res) in enumerate(results.items(), start=2):
            ac = ALGO_COLORS.get(algo, T['text'])
            rbg = row_bg_even if ri % 2 == 0 else row_bg_odd

            # Algorithm name — full name, colored
            tk.Label(self.cmp_frame, text=algo, bg=rbg, fg=ac,
                     font=('Segoe UI', 9, 'bold'), width=col_widths[0], anchor='w',
                     padx=4, pady=3
                     ).grid(row=ri, column=0, padx=(0, 1), pady=0, sticky='ew')

            # Data columns: Nodes, Path, Cost, Time
            for ci, (val, best) in enumerate(
                zip([res['nodes'], res['path_len'], res['cost'], res['ms']],
                    [best_nodes,   best_path,       best_cost,  best_ms]), start=1
            ):
                if not res['found']:
                    txt, fg = '✕', T['dim']
                else:
                    if ci == 4:  # Time column
                        txt = f"{val} ms"
                    else:
                        txt = str(val)
                    fg = T['green'] if val == best else T['text']
                weight = 'bold' if (res['found'] and val == best) else 'normal'
                tk.Label(self.cmp_frame, text=txt, bg=rbg, fg=fg,
                         font=('Segoe UI', 9, weight), width=col_widths[ci],
                         anchor='center', padx=3, pady=3
                         ).grid(row=ri, column=ci, padx=(0, 1), pady=0, sticky='ew')

        # Configure columns to expand evenly
        for ci in range(num_cols):
            self.cmp_frame.columnconfigure(ci, weight=1)

    def _draw_empty_table(self):
        for w in self.cmp_frame.winfo_children():
            w.destroy()

        headers = ['Algorithm', 'Nodes', 'Path', 'Cost', 'Time']
        col_widths = [10, 7, 6, 6, 7]
        num_cols = len(headers)

        hdr_bg = T['border']
        for ci, (h, w) in enumerate(zip(headers, col_widths)):
            tk.Label(self.cmp_frame, text=h, bg=hdr_bg, fg=T['text'],
                     font=('Segoe UI', 9, 'bold'), width=w,
                     anchor='center' if ci > 0 else 'w',
                     padx=4, pady=4
                     ).grid(row=0, column=ci, padx=(0, 1), pady=(0, 1), sticky='ew')

        tk.Frame(self.cmp_frame, bg=T['blue'], height=2).grid(
            row=1, column=0, columnspan=num_cols, sticky='ew')

        row_bg_even = T['card']
        row_bg_odd  = hex_blend(T['card'], T['surface'], 0.5)

        for ri, algo in enumerate(ALGORITHMS, start=2):
            color = ALGO_COLORS.get(algo, T['text'])
            rbg = row_bg_even if ri % 2 == 0 else row_bg_odd

            tk.Label(self.cmp_frame, text=algo, bg=rbg, fg=color,
                     font=('Segoe UI', 9, 'bold'), width=col_widths[0], anchor='w',
                     padx=4, pady=3
                     ).grid(row=ri, column=0, padx=(0, 1), pady=0, sticky='ew')
            for ci in range(1, num_cols):
                tk.Label(self.cmp_frame, text='—', bg=rbg, fg=T['dim'],
                         font=('Segoe UI', 9), width=col_widths[ci], anchor='center',
                         padx=3, pady=3
                         ).grid(row=ri, column=ci, padx=(0, 1), pady=0, sticky='ew')

        for ci in range(num_cols):
            self.cmp_frame.columnconfigure(ci, weight=1)

    # ── Grid operations ───────────────────────────────────────────────────────

    def _gen_maze(self):
        if self.running:
            return
        self.grid = generate_maze(ROWS, COLS, self.start, self.end)
        self._redraw_walls()
        self.status_var.set('Maze generated  ·  Click ▶ Visualize to run an algorithm')

    def _random_walls(self):
        if self.running:
            return
        self.grid = generate_random_walls(ROWS, COLS, self.start, self.end)
        self._redraw_walls()
        self.status_var.set('Random walls placed  ·  Click ▶ Visualize to run an algorithm')

    def _redraw_walls(self):
        for r in range(ROWS):
            for c in range(COLS):
                if (r, c) == self.start:
                    self._paint(r, c, T['start'])
                elif (r, c) == self.end:
                    self._paint(r, c, T['end'])
                elif self.grid[r][c] == WALL:
                    self._paint(r, c, T['wall'])
                else:
                    self._paint(r, c, T['empty'])

    def _reset_view(self):
        if self.running:
            self._stop()
        for r in range(ROWS):
            for c in range(COLS):
                if   (r, c) == self.start:         self._paint(r, c, T['start'])
                elif (r, c) == self.end:            self._paint(r, c, T['end'])
                elif self.grid[r][c] == WALL:       self._paint(r, c, T['wall'])
                else:                               self._paint(r, c, T['empty'])
        self.sv_nodes.set('—'); self.sv_path.set('—')
        self.sv_cost.set('—');  self.sv_time.set('—')
        self.status_var.set('View cleared  ·  Walls preserved')

    def _clear_all(self):
        if self.running:
            self._stop()
        self.grid = [[EMPTY] * COLS for _ in range(ROWS)]
        self._redraw_walls()
        self.sv_nodes.set('—'); self.sv_path.set('—')
        self.sv_cost.set('—');  self.sv_time.set('—')
        self._draw_empty_table()
        self.status_var.set('Grid cleared  ·  Start and end positions preserved')

    # ── Entry point ───────────────────────────────────────────────────────────

    def run(self):
        self.root.mainloop()
