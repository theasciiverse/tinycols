"""drive.py SESSION: plays tinycols in a 100x30 tmux pane for the catalog
preview (asciiverse/record.sh).

The board is read from the pane: the default 6x13 well, centred, its
corner found from the frame. A new piece has spawned when the "next" box
changes; the piece in play is then the one the box showed before, at the
top of the middle column. For every column and every turn of the three
jewels the driver drops the piece in a copy of the well, runs the game's
own matching (rows, columns and both diagonals of three or more, with
the jewels above falling in after every clear, chain after chain) and
scores the result: points first, then a low, even stack with like
colours next to each other. It turns the piece with 'a', walks it with
the arrows and presses Down until the next piece appears. Plays until
SECONDS_LIMIT (default 50) has passed or the game is over."""
import os, subprocess, sys, time

S = sys.argv[1]
secs = float(os.environ.get("SECONDS_LIMIT", "50"))
TMUX = ["tmux", "-L", os.environ.get("TMUX_SOCKET", "default")]
COLS, ROWS = 6, 13


def key(*k):
    subprocess.run(TMUX + ["send-keys", "-t", S, *k])


def screen():
    out = subprocess.run(TMUX + ["capture-pane", "-p", "-t", S],
                         capture_output=True, text=True).stdout
    return [r.ljust(100) for r in (out.split("\n") + [""] * 30)[:30]]


def corner(rows):
    # the well's top-left corner: a box corner, or the DEC line-drawing
    # "l" tmux shows when the game draws with the alternate character set
    for y, r in enumerate(rows):
        for mark in ("┌", "lqq"):
            x = r.find(mark)
            if x >= 0:
                return y, x
    return None


def read(rows, c):
    oy, ox = c
    grid = [[0] * COLS for _ in range(ROWS)]
    for y in range(ROWS):
        for x in range(COLS):
            ch = rows[oy + 1 + y][ox + 1 + 2 * x]
            grid[y][x] = int(ch) if ch.isdigit() else 0
    nx = ox + (COLS + 1) * 2 + 1
    nxt = tuple(int(rows[oy + 1 + i][nx]) if rows[oy + 1 + i][nx].isdigit()
                else 0 for i in range(3))
    return grid, nxt


def scan(g):
    hit = set()
    for y in range(ROWS):
        for x in range(COLS):
            c = g[y][x]
            if not c:
                continue
            for dy, dx in ((0, 1), (1, 0), (1, -1), (1, 1)):
                run = [(y, x)]
                yy, xx = y + dy, x + dx
                while 0 <= yy < ROWS and 0 <= xx < COLS and g[yy][xx] == c:
                    run.append((yy, xx))
                    yy, xx = yy + dy, xx + dx
                if len(run) >= 3:
                    hit.update(run)
    return hit


def settle(g):
    for x in range(COLS):
        col = [g[y][x] for y in range(ROWS) if g[y][x]]
        for y in range(ROWS):
            g[y][x] = 0
        for i, c in enumerate(reversed(col)):
            g[ROWS - 1 - i][x] = c


def drop(g, col, piece):
    """The well after dropping piece (top to bottom) in col, and points."""
    land = ROWS
    for y in range(ROWS):
        if g[y][col]:
            land = y
            break
    if land < 3:
        return None, 0
    g = [r[:] for r in g]
    for i in range(3):
        g[land - 3 + i][col] = piece[i]
    pts, chain = 0, 0
    while True:
        hit = scan(g)
        if not hit:
            break
        chain += 1
        pts += len(hit) * chain
        for y, x in hit:
            g[y][x] = 0
        settle(g)
    return g, pts


def judge(g, pts):
    heights = []
    for x in range(COLS):
        h = 0
        for y in range(ROWS):
            if g[y][x]:
                h = ROWS - y
                break
        heights.append(h)
    near = 0
    for y in range(ROWS):
        for x in range(COLS):
            c = g[y][x]
            if c:
                for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < ROWS and 0 <= xx < COLS and g[yy][xx] == c:
                        near += 1
    bump = sum(abs(a - b) for a, b in zip(heights, heights[1:]))
    return pts * 40 + near * 3 - max(heights) * 4 - sum(heights) - bump * 2


def reachable(g, col):
    """The top row of every column between the middle and col is free."""
    lo, hi = sorted((COLS // 2, col))
    return all(g[0][x] == 0 for x in range(lo, hi + 1))


def best_move(g, piece):
    best = None
    for turn in range(3):
        p = piece
        for _ in range(turn):          # 'a' turns the jewels upwards
            p = (p[1], p[2], p[0])
        for col in range(COLS):
            if not reachable(g, col):
                continue
            after, pts = drop(g, col, p)
            if after is None:
                continue
            v = judge(after, pts)
            if best is None or v > best[0]:
                best = (v, turn, col)
    return best


def main():
    t0 = time.time()
    c = None
    while c is None and time.time() - t0 < 15:
        time.sleep(0.2)
        rows = screen()
        c = corner(rows)
    if c is None:
        sys.exit("no board on the screen")
    time.sleep(0.8)
    rows = screen()
    grid, nxt = read(rows, c)
    current = None
    while time.time() - t0 < secs:
        rows = screen()
        if "GAME OVER" in "".join(rows):
            break
        grid, shown_next = read(rows, c)
        for y in range(3):             # the piece in play, top of the middle
            if grid[y][COLS // 2]:
                grid[y][COLS // 2] = 0
        if current is None:            # the first piece is not known yet
            move = (0, 0, COLS // 2)
        else:
            move = best_move(grid, current)
        if move is None:
            move = (0, 0, COLS // 2)
        _, turn, col = move
        time.sleep(0.25)
        for _ in range(turn):
            key("a")
            time.sleep(0.12)
        step = "Right" if col > COLS // 2 else "Left"
        for _ in range(abs(col - COLS // 2)):
            key(step)
            time.sleep(0.12)
        time.sleep(0.2)
        # drop until the next box changes: a new piece is in play
        while time.time() - t0 < secs:
            key("Down")
            time.sleep(0.05)
            rows = screen()
            if "GAME OVER" in "".join(rows):
                return
            _, now_next = read(rows, c)
            if now_next != nxt:
                current = nxt
                nxt = now_next
                break


main()
