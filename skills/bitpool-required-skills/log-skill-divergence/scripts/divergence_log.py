#!/usr/bin/env python3
"""Location + file helper for log-skill-divergence (stdlib only).

  python divergence_log.py locate
      -> {"dir", "kind": "shared"|"local", "index_exists", "library": <team library or null>}
  python divergence_log.py free-name <YYYY-MM-DD_HHmm> <slug>
      -> {"name", "path"}  first free <stamp>_<slug>[-N].md in the resolved dir (never overwrites)
  python divergence_log.py index-add <row>
      -> inserts <row> directly under the index table header, creating index.md from
         assets/index.md.template first if needed. Rows already present are never touched.
  python divergence_log.py slug <text>
      -> {"slug"}  lowercased, non-alphanumerics -> '-', trimmed to 60 chars at a word boundary

All text is read/written as UTF-8 without BOM, LF newlines.
Shared location: <Team library>/Hermes Skill logging/, where the Team library is the synced
"Bitpool-Team - Documents" SharePoint library. Local fallback: $HERMES_HOME/skill-divergence/.
"""
import json
import os
import re
import sys
from pathlib import Path

LIB_NAME = "Bitpool-Team - Documents"
LOG_FOLDER = "Hermes Skill logging"
HERE = Path(__file__).resolve().parent
INDEX_TEMPLATE = HERE.parent / "assets" / "index.md.template"


def hermes_home() -> Path:
    env = os.environ.get("HERMES_HOME")
    if env:
        return Path(os.path.expandvars(os.path.expanduser(env)))
    if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"]) / "hermes"
    return Path.home() / ".hermes"


def team_library():
    home = Path.home()
    cands = [home / "Bitpool Pty Ltd" / LIB_NAME]                     # Windows OneDrive sync
    cloud = home / "Library" / "CloudStorage"                          # macOS File Provider
    if cloud.is_dir():
        cands += sorted(cloud.glob(f"OneDrive-SharedLibraries-*/{LIB_NAME}"))
    for c in cands:
        if c.is_dir():
            return c
    return None


def locate():
    lib = team_library()
    if lib:
        d, kind = lib / LOG_FOLDER, "shared"
    else:
        d, kind = hermes_home() / "skill-divergence", "local"
    return d, kind, lib


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if len(s) > 60:
        cut = s[:60]
        s = cut.rsplit("-", 1)[0] if "-" in cut else cut
    return s or "untitled"


def emit(obj, code=0):
    print(json.dumps(obj, ensure_ascii=False))
    sys.exit(code)


def main(a):
    if not a:
        emit({"ok": False, "usage": __doc__.strip().splitlines()[2:14]}, 2)
    d, kind, lib = locate()
    if a[0] == "locate":
        emit({"ok": True, "dir": str(d), "kind": kind, "dir_exists": d.is_dir(),
              "index_exists": (d / "index.md").is_file(), "library": str(lib) if lib else None})
    if a[0] == "slug" and len(a) > 1:
        emit({"ok": True, "slug": slugify(" ".join(a[1:]))})
    if a[0] == "free-name" and len(a) == 3:
        stamp, slug = a[1], slugify(a[2])
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}_\d{4}", stamp):
            emit({"ok": False, "error": "stamp must be YYYY-MM-DD_HHmm"}, 2)
        d.mkdir(parents=True, exist_ok=True)
        n, name = 1, f"{stamp}_{slug}.md"
        while (d / name).exists():
            n += 1
            name = f"{stamp}_{slug}-{n}.md"
        emit({"ok": True, "name": name, "path": str(d / name), "kind": kind})
    if a[0] == "index-add" and len(a) == 2:
        row = a[1].strip()
        if not (row.startswith("|") and row.endswith("|")) or "\n" in row:
            emit({"ok": False, "error": "row must be one markdown table line"}, 2)
        d.mkdir(parents=True, exist_ok=True)
        idx = d / "index.md"
        if not idx.is_file():
            idx.write_text(INDEX_TEMPLATE.read_text(encoding="utf-8-sig"), encoding="utf-8", newline="\n")
        lines = idx.read_text(encoding="utf-8-sig").splitlines()
        sep = next((i for i, l in enumerate(lines) if re.match(r"^\|(\s*-+\s*\|)+\s*$", l)), None)
        if sep is None:
            emit({"ok": False, "error": "no table header found in index.md; fix by hand"}, 1)
        lines.insert(sep + 1, row)
        with open(idx, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(lines) + "\n")
        ok = row in idx.read_text(encoding="utf-8").splitlines()
        emit({"ok": ok, "index": str(idx), "kind": kind}, 0 if ok else 1)
    emit({"ok": False, "error": f"bad arguments: {a}"}, 2)


if __name__ == "__main__":
    main(sys.argv[1:])
