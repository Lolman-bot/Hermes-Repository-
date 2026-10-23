"""Assemble a single, self-contained Bitpool diagram animation HTML file.

Joins the skill's assets/animation-template.html with the embedded Inter font, the
motion recipes the diagram borrows, and the diagram's own markup and CSS, then checks
the result has no unfilled markers and nothing fetched from the network.

Usage:
  python assemble.py --markup diagram.html --css diagram.css --theme light|dark
                     --title "Plain title" --out "C:/path/name.html"
                     [--recipes flow,ripple] [--section-classes "m-flow"]
"""
import argparse
import re
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
RECIPE_NAME = re.compile(r"(?:\.|@keyframes\s+)m-([a-z0-9]+)")


def statements(css):
    """Split CSS into top-level statements (comments kept), by brace depth."""
    out, buf, depth, i = [], [], 0, 0
    while i < len(css):
        if css.startswith("/*", i):
            end = css.index("*/", i) + 2
            if depth == 0 and not "".join(buf).strip():
                out.append(css[i:end])
                buf = []
            else:
                buf.append(css[i:end])
            i = end
            continue
        ch = css[i]
        buf.append(ch)
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                out.append("".join(buf).strip())
                buf = []
        i += 1
    tail = "".join(buf).strip()
    if tail:
        out.append(tail)
    return out


def pick_recipes(css, wanted):
    """Keep the shared base rules plus only the recipes named in `wanted`."""
    kept = []
    for st in statements(css):
        if st.startswith("/*"):
            continue
        names = set(RECIPE_NAME.findall(st.split("{", 1)[0] if not st.startswith("@keyframes") else st[:80]))
        if not names or names & wanted:
            kept.append(st)
    return "\n".join(kept)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--markup", required=True, help="the diagram's HTML, placed inside .w-stage")
    ap.add_argument("--css", required=True, help="the diagram's own CSS")
    ap.add_argument("--theme", choices=["light", "dark"], required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--recipes", default="", help="comma list of library recipes to include, e.g. flow,ripple")
    ap.add_argument("--section-classes", default="", help="extra classes on the section, e.g. m-flow")
    a = ap.parse_args()

    wanted = {r.strip().removeprefix("m-") for r in a.recipes.split(",") if r.strip()}
    known = set(RECIPE_NAME.findall((ASSETS / "motion-recipes.css").read_text(encoding="utf-8")))
    unknown = wanted - known
    if unknown:
        sys.exit(f"Unknown recipe(s): {', '.join(sorted(unknown))}. Known: {', '.join(sorted(known))}")

    html = (ASSETS / "animation-template.html").read_text(encoding="utf-8")
    recipes = pick_recipes((ASSETS / "motion-recipes.css").read_text(encoding="utf-8"), wanted)
    title = a.title.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")
    parts = {
        "/*@@FONT@@*/": (ASSETS / "inter-font.css").read_text(encoding="utf-8"),
        "/*@@RECIPES@@*/": recipes,
        "/*@@DIAGRAM_CSS@@*/": Path(a.css).read_text(encoding="utf-8"),
        "<!--@@DIAGRAM@@-->": Path(a.markup).read_text(encoding="utf-8"),
        "@@SECTION_CLASSES@@": a.section_classes,
        "@@THEME@@": "dk" if a.theme == "dark" else "",
        "@@TITLE@@": title,
    }
    for marker, value in parts.items():
        html = html.replace(marker, value)

    problems = []
    if "@@" in html:
        problems.append("unfilled @@ marker left in the output")
    for m in re.finditer(r"""(?:src|href)\s*=\s*["'](https?:)?//|url\(\s*["']?(https?:)?//|@import""", html):
        problems.append(f"external reference: {html[m.start():m.start() + 80]!r}")
    if problems:
        sys.exit("Not written:\n  " + "\n  ".join(problems))

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out} ({out.stat().st_size // 1024} KB, theme {a.theme}, recipes: {', '.join(sorted(wanted)) or 'none'})")

    # Several library recipes hard-code white surfaces; on the dark theme those stay white
    # and swallow white text. Name them so they can be overridden with var(--bp-white).
    if a.theme == "dark":
        css = recipes + "\n" + parts["/*@@DIAGRAM_CSS@@*/"]
        hits = [st.split("{", 1)[0].strip() for st in statements(css)
                if re.search(r"background(?:-color)?:\s*(?:#fff\b|#ffffff\b|white\b)", st, re.I)
                and not st.startswith("@keyframes")]
        if hits:
            print("WARNING: dark theme, but these rules paint a white background; "
                  "override them with var(--bp-white) / var(--bp-surface-2) in the diagram CSS:")
            for h in hits:
                print("  " + h)


if __name__ == "__main__":
    main()
