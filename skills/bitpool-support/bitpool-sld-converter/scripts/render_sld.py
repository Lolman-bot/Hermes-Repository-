#!/usr/bin/env python3
"""Render a traced single line diagram (topology JSON) as a Bitpool-styled SVG + PNG.

Usage:  python3 render_sld.py topology.json --out ./out [--dx 400] [--scale 1.5]
Writes: <board>-single-line.svg, <board>-single-line.png (transparent), <board>-meters.json

Topology shape (worked example: assets/example-msb-1a.json):
{
  "board": "MSB-1A",
  "groups": [                     # group 1 sits on the end of the incoming line; every later
    {                             # group drops off the incoming line, further left each time
      "name": "Unmetered tenant",
      "main_meter": "MSB-1A-EY TENANT SB-1",   # or null when the feeder has no meter
      "join": 1.5,                # which row the feed enters the riser at: 0 = top row,
                                  # 2 = third row, 1.5 = between rows 2 and 3
      "rows": [["TDB-L05-B-P", "TDB-L05-B-L"], ["..."]]   # meters along each branch, left to right
    }
  ]
}
A row item is a label, or {"label": "...", "children": [[...], [...]]} when that meter feeds a
sub-board with meters of its own. "children" takes rows in the same shape as "rows" and nests to any
depth (worked example: assets/example-nested.json).
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile

# ---- Layout (diagram units; 1 unit = --scale px in the PNG) -----------------------------
S = 100          # vertical spacing between branch rows (room for a data card above each dot)
GROUP_GAP = 140  # extra vertical gap between groups, so cards don't collide across groups
R = 12           # corner radius on riser ends and drop bends
RX = 560         # x of every group's riser
FIRST = 120      # riser -> first branch meter
MAIN_OFF = 110   # group 1's main meter sits this far left of the riser, on the incoming line
DROP0 = 230      # group 2's drop sits this far left of the riser...
DROP_STEP = 130  # ...and each later group this much further left
SRC_LEAD = 180   # incoming line starts this far left of the leftmost drop
TOP = 90
NEST_GAP = 250   # gap after a meter's sub-board before the next meter on its row (room for a card)
# ---- Consistent dashboard padding, PNG pixels (the agreed MSB-1A reference) -------------
PAD_L, PAD_R, PAD_T, PAD_B = 1360, 1500, 1780, 1700
# ---- Bitpool colours ---------------------------------------------------------------------
INK, CYAN = "#1B2732", "#00ADEF"
CSS = f""".feed{{stroke:{INK};stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round;fill:none}}
.bus{{stroke:{CYAN};stroke-width:4;stroke-linecap:round;fill:none}}
.jn{{fill:{INK}}}
.mt{{fill:#ffffff;stroke:{CYAN};stroke-width:2.5}}
.sm{{fill:#ffffff;stroke:{INK};stroke-width:2.5}}
.sc,.src{{fill:{CYAN}}}"""


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def esc(s):
    return (s or "").replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def item(it):
    """A row item is a bare label or {"label", "children"}; return it as a dict."""
    return it if isinstance(it, dict) else {"label": it}


def row_layout(row, dx):
    """x offsets of a row's meters from the row's start, and how far the row reaches in total.
    Meters sit dx apart; a meter with a sub-board pushes the next one right by the sub-board's width."""
    offs, x, reach = [], 0, 0
    for it in row:
        w = reach_of(item(it).get("children"), dx)
        offs.append(x)
        reach = max(reach, x + (FIRST + w if item(it).get("children") else 0))
        x += max(dx, FIRST + w + NEST_GAP) if item(it).get("children") else dx
    return offs, reach


def reach_of(rows, dx):
    return max((row_layout(r, dx)[1] for r in rows or []), default=0)


def build(topo, dx):
    groups = topo.get("groups") or sys.exit("topology has no groups")
    paths, dots, meters, mains = [], set(), [], []

    def lay_rows(rows, rx, y, group, depth, parent):
        """Place rows of meters starting at y, their riser at x=rx. Sub-boards are placed recursively
        under their parent meter. Returns each row's y, each row's last x, and the lowest y used."""
        ys, ends, low = [], [], y
        for ri, row in enumerate(rows):
            offs = row_layout(row, dx)[0] or [0]
            xs = [rx + FIRST + o for o in offs]
            ys.append(y); ends.append(xs[-1]); low = y
            for it, mx in zip(row, xs):
                it = item(it)
                meters.append(dict(label=it["label"], role="branch", group=group, row=ri, depth=depth,
                                   parent=parent, x=mx, y=y))
                if it.get("children"):
                    if not all(isinstance(r, list) and r for r in it["children"]):
                        sys.exit(f"meter '{it['label']}' needs children as a list of non-empty rows")
                    cys, ces, clow = lay_rows(it["children"], mx, y + S, group, depth + 1, it["label"])
                    low = max(low, clow)
                    if len(cys) == 1:
                        paths.append(("feed", f"M{mx} {y} V{cys[0]-R} Q{mx} {cys[0]} {mx+R} {cys[0]} H{ces[0]}"))
                    else:
                        paths.append(("feed", f"M{mx} {y} V{cys[-1]-R} Q{mx} {cys[-1]} {mx+R} {cys[-1]} H{ces[-1]}"))
                        for cy, ce in zip(cys[:-1], ces[:-1]):
                            paths.append(("feed", f"M{mx} {cy} H{ce}"))
                            dots.add((mx, cy))
            y = low + S
        return ys, ends, low

    # vertical placement: every group's rows, with sub-boards pushing later rows down
    y, layout = TOP, []
    for gi, g in enumerate(groups):
        if not g.get("rows"):
            sys.exit(f"group '{g.get('name')}' has no rows")
        if gi:
            y += GROUP_GAP
        rows, ends, low = lay_rows(g["rows"], RX, y, g.get("name", ""), 0, None)
        n = len(rows)
        join = min(max(float(g.get("join", (n - 1) / 2)), 0), n - 1)
        k = int(join)
        feed = rows[k] + (join - k) * (rows[k + 1] - rows[k]) if k < n - 1 else rows[-1]
        layout.append((rows, ends, feed))
        y = low
    bus = layout[0][2]
    last = len(groups) - 1
    for gi, (g, (rows, ends, feed)) in enumerate(zip(groups, layout)):
        if len(rows) == 1:
            paths.append(("feed", f"M{RX} {rows[0]} H{ends[0]}"))
        else:
            paths.append(("feed", f"M{ends[0]} {rows[0]} H{RX+R} Q{RX} {rows[0]} {RX} {rows[0]+R} "
                                  f"V{rows[-1]-R} Q{RX} {rows[-1]} {RX+R} {rows[-1]} H{ends[-1]}"))
            for ry, e in zip(rows[1:-1], ends[1:-1]):
                paths.append(("feed", f"M{RX} {ry} H{e}"))
                dots.add((RX, ry))
        if len(rows) > 1:
            dots.add((RX, feed))
        if gi == 0:
            if g.get("main_meter"):
                mains.append(dict(label=g["main_meter"], role="main", group=g.get("name", ""), x=RX - MAIN_OFF, y=bus))
        else:
            drop = RX - DROP0 - DROP_STEP * (gi - 1)
            paths.append(("feed", f"M{drop} {bus} V{feed-R} Q{drop} {feed} {drop+R} {feed} H{RX}"))
            dots.add((drop, bus))
            if g.get("main_meter"):
                mains.append(dict(label=g["main_meter"], role="main", group=g.get("name", ""),
                                  x=(drop + RX) // 2 + 10, y=feed))
    left = RX - DROP0 - DROP_STEP * (last - 1) if last else RX - MAIN_OFF - 60
    src = (left - SRC_LEAD, bus)
    paths.append(("bus", f"M{src[0]} {bus} H{RX}"))
    return paths, sorted(dots), meters, mains, src


def png_via_browser(svg_p, png_p, w, h):
    """Fallback when cairosvg or the Cairo library is missing (common on Windows): screenshot the
    SVG with headless Edge/Chrome on a transparent background."""
    cands = [shutil.which(n) for n in ("msedge", "chrome", "google-chrome", "chromium", "chromium-browser")]
    cands += [os.path.join(os.environ.get(v, ""), r) for v in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA")
              for r in (r"Microsoft\Edge\Application\msedge.exe", r"Google\Chrome\Application\chrome.exe")]
    exe = next((c for c in cands if c and os.path.isfile(c)), None)
    if not exe:
        sys.exit("PNG needs cairosvg with the Cairo library, or Edge/Chrome installed. The SVG was written.")
    with tempfile.TemporaryDirectory() as d:
        page = os.path.join(d, "p.html")
        open(page, "w").write('<body style="margin:0;background:transparent"><img src="file:///%s" width="%d" height="%d" '
                              'style="display:block"></body>' % (os.path.abspath(svg_p).replace("\\", "/"), w, h))
        subprocess.run([exe, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        "--default-background-color=00000000", f"--window-size={w},{h}",
                        f"--screenshot={os.path.abspath(png_p)}", "--user-data-dir=" + d, "file:///" + page.replace("\\", "/")],
                       check=True, capture_output=True)


def render(topo, out, dx, scale):
    paths, dots, meters, mains, src = build(topo, dx)
    xs = [m["x"] for m in meters + mains] + [src[0]]
    ys = [m["y"] for m in meters + mains]
    x0 = round(min(xs) - 8 - PAD_L / scale); y0 = round(min(ys) - 8 - PAD_T / scale)
    W = round(max(xs) + 8 + PAD_R / scale - x0); H = round(max(ys) + 8 + PAD_B / scale - y0)
    body = [f'<path class="feed" d="{d}"/>' for c, d in paths if c == "feed"]
    body += [f'<path class="bus" d="{d}"/>' for c, d in paths if c == "bus"]
    body += [f'<circle class="jn" cx="{x}" cy="{y}" r="4"/>' for x, y in dots]
    body.append(f'<circle class="src" cx="{src[0]}" cy="{src[1]}" r="6"/>')
    for m in meters:  # labels live only in id/data-label: never drawn
        body.append(f'<circle class="mt" id="{slug(m["label"])}" data-label="{esc(m["label"])}" '
                    f'cx="{m["x"]}" cy="{m["y"]}" r="6.5"/>')
    for m in mains:
        body.append(f'<g id="{slug(m["label"])}" data-label="{esc(m["label"])}"><circle class="sm" cx="{m["x"]}" '
                    f'cy="{m["y"]}" r="11"/><circle class="sc" cx="{m["x"]}" cy="{m["y"]}" r="4.5"/></g>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {W} {H}" width="{W}" height="{H}" '
           f'fill="none">\n<style>\n{CSS}\n</style>\n' + "\n".join(body) + "\n</svg>\n")
    os.makedirs(out, exist_ok=True)
    b = slug(topo.get("board", "board"))
    svg_p, png_p, js_p = (os.path.join(out, f"{b}-{s}") for s in ("single-line.svg", "single-line.png", "meters.json"))
    open(svg_p, "w").write(svg)
    try:
        import cairosvg
        cairosvg.svg2png(bytestring=svg.encode(), write_to=png_p, scale=scale)
    except (ImportError, OSError):
        png_via_browser(svg_p, png_p, round(W * scale), round(H * scale))
    for m in mains + meters:
        m["px"], m["py"] = round((m["x"] - x0) * scale), round((m["y"] - y0) * scale)
        m["pct_x"], m["pct_y"] = round(m["px"] / round(W * scale) * 100, 3), round(m["py"] / round(H * scale) * 100, 3)
    json.dump(dict(board=topo.get("board"), png_size=[round(W * scale), round(H * scale)], meters=mains + meters),
              open(js_p, "w"), indent=2)
    print(f"{svg_p}\n{png_p}  {round(W*scale)} x {round(H*scale)} px\n{js_p}\n"
          f"{len(mains)} main meters, {len(meters)} branch meters")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("topology")
    ap.add_argument("--out", default=".")
    ap.add_argument("--dx", type=int, default=400, help="horizontal spacing between branch meters (default 400)")
    ap.add_argument("--scale", type=float, default=1.5, help="PNG pixels per diagram unit (default 1.5)")
    a = ap.parse_args()
    render(json.load(open(a.topology)), a.out, a.dx, a.scale)
