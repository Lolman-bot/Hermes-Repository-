#!/usr/bin/env python3
"""Per-skill, per-user config store for Bitpool Hermes skills (stdlib only).

Usage:
  python user_config.py path  <skill>
  python user_config.py get   <skill> [<key>]
  python user_config.py set   <skill> <key> <value> [--overwrite]
  python user_config.py unset <skill> <key>

Every command prints one JSON object. Exit code 0 = ok, 1 = refused/not found, 2 = usage error.

Location (first that resolves wins, re-resolved on every call):
  1. OneDrive for Business / personal OneDrive root from the environment
     (OneDriveCommercial, then OneDrive) -- Windows.
  2. macOS: exactly one ~/Library/CloudStorage/OneDrive-* folder (shared-library
     folders excluded; a folder containing "Bitpool" wins if there are several).
  3. Fallback: $HERMES_HOME/bitpool-config/ (HERMES_HOME defaults to
     %LOCALAPPDATA%\\hermes on Windows, $HOME/.hermes elsewhere).
On OneDrive the folder is <root>/skill-config/. The file is <folder>/<skill>.md
holding "- key: value" lines. Never put secrets in it.
"""
import json
import os
import re
import sys
from pathlib import Path

HEADER = (
    "# {skill} \u2014 stored user values\n\n"
    "<!-- Written by user-config-store. Never store secrets, passwords, or credentials here. -->\n\n"
)
# "- key: value" is canonical; bare "key: value" (seen in hand/PowerShell-written files) is read
# too and normalised to the canonical form on the next write.
LINE_RE = re.compile(r"^(?:- )?([A-Za-z0-9_.-]{2,}):[ \t]?(.*)$")
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
KEY_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
SECRET_HINT = re.compile(r"(pass(word)?|secret|token|api[_-]?key|credential|private[_-]?key)", re.I)


def hermes_home() -> Path:
    env = os.environ.get("HERMES_HOME")
    if env:
        return Path(os.path.expandvars(os.path.expanduser(env)))
    if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"]) / "hermes"
    return Path.home() / ".hermes"


def onedrive_root():
    for var in ("OneDriveCommercial", "OneDrive"):
        val = os.environ.get(var)
        if val and Path(val).is_dir():
            return Path(val), var
    cloud = Path.home() / "Library" / "CloudStorage"
    if cloud.is_dir():
        cands = [p for p in cloud.glob("OneDrive-*")
                 if p.is_dir() and not p.name.startswith("OneDrive-SharedLibraries")]
        bp = [p for p in cands if "bitpool" in p.name.lower()]
        if len(bp) == 1:
            return bp[0], "macOS CloudStorage"
        if len(cands) == 1:
            return cands[0], "macOS CloudStorage"
    return None, None


def locations():
    """Return [(label, folder)] in read-priority order; first entry is the write target."""
    locs = []
    root, how = onedrive_root()
    if root:
        locs.append((f"onedrive ({how})", root / "skill-config"))
    locs.append(("hermes-home fallback", hermes_home() / "bitpool-config"))
    return locs


def read_values(path: Path) -> dict:
    vals = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            m = LINE_RE.match(line.rstrip())
            if m:
                vals[m.group(1)] = m.group(2).strip()
    return vals


def write_values(path: Path, skill: str, vals: dict, keep_text: str = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if keep_text is None:
        body = HEADER.format(skill=skill)
        body += "".join(f"- {k}: {v}\n" for k, v in vals.items())
    else:
        # Preserve non-key lines; rewrite/append key lines in place.
        out, seen = [], set()
        for line in keep_text.splitlines():
            m = LINE_RE.match(line.rstrip())
            if m:
                k = m.group(1)
                if k in vals and k not in seen:
                    out.append(f"- {k}: {vals[k]}")
                    seen.add(k)
                continue  # dropped (unset) or duplicate
            out.append(line)
        while out and out[-1] == "":
            out.pop()
        for k, v in vals.items():
            if k not in seen:
                out.append(f"- {k}: {v}")
        body = "\n".join(out) + "\n"
    # UTF-8, no BOM, LF newlines on every OS.
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)


def emit(obj, code=0):
    print(json.dumps(obj, ensure_ascii=False))
    sys.exit(code)


def main(argv):
    if len(argv) < 2 or argv[0] not in ("path", "get", "set", "unset"):
        emit({"ok": False, "error": __doc__.strip().splitlines()[2:8]}, 2)
    cmd, skill = argv[0], argv[1]
    if not NAME_RE.match(skill):
        emit({"ok": False, "error": f"bad skill name: {skill!r}"}, 2)
    locs = locations()
    target_label, target_dir = locs[0]
    target = target_dir / f"{skill}.md"

    if cmd == "path":
        emit({"ok": True, "write_target": str(target), "target_kind": target_label,
              "read_order": [str(d / f"{skill}.md") for _, d in locs],
              "onedrive_found": target_label.startswith("onedrive")})

    if cmd == "get":
        key = argv[2] if len(argv) > 2 else None
        for label, d in locs:
            vals = read_values(d / f"{skill}.md")
            if key is None and vals:
                emit({"ok": True, "values": vals, "file": str(d / f"{skill}.md"), "location": label})
            if key is not None and key in vals:
                emit({"ok": True, "key": key, "value": vals[key],
                      "file": str(d / f"{skill}.md"), "location": label,
                      "in_write_target": d == target_dir})
        emit({"ok": False, "found": False, "key": key, "write_target": str(target)}, 1)

    if cmd == "set":
        if len(argv) < 4:
            emit({"ok": False, "error": "set needs <skill> <key> <value>"}, 2)
        key, value = argv[2], argv[3]
        overwrite = "--overwrite" in argv[4:]
        if not KEY_RE.match(key):
            emit({"ok": False, "error": f"bad key: {key!r}"}, 2)
        if "\n" in value or "\r" in value:
            emit({"ok": False, "error": "value must be a single line"}, 2)
        if SECRET_HINT.search(key):
            emit({"ok": False, "error": "key looks like a secret; secrets never go in this store "
                  "(use $HERMES_HOME/.env via required_environment_variables)"}, 1)
        text = target.read_text(encoding="utf-8-sig") if target.is_file() else None
        vals = read_values(target)
        if key in vals and vals[key] != value and not overwrite:
            emit({"ok": False, "refused": "exists", "key": key, "current": vals[key],
                  "file": str(target), "hint": "confirm with the user, then re-run with --overwrite"}, 1)
        vals[key] = value
        write_values(target, skill, vals, text)
        check = read_values(target).get(key)
        emit({"ok": check == value, "key": key, "value": check, "file": str(target),
              "location": target_label}, 0 if check == value else 1)

    if cmd == "unset":
        if len(argv) < 3:
            emit({"ok": False, "error": "unset needs <skill> <key>"}, 2)
        key = argv[2]
        removed = []
        for label, d in locs:
            f = d / f"{skill}.md"
            vals = read_values(f)
            if key in vals:
                text = f.read_text(encoding="utf-8-sig")
                del vals[key]
                write_values(f, skill, vals, text)
                removed.append(str(f))
        emit({"ok": bool(removed), "key": key, "removed_from": removed}, 0 if removed else 1)


if __name__ == "__main__":
    main(sys.argv[1:])
