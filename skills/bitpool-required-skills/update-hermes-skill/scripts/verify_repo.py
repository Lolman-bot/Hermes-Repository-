#!/usr/bin/env python3
"""Verify the Bitpool Hermes skills repo against its README house rules.

Usage (from anywhere; stdlib only, PyYAML used if installed):

    python verify_repo.py [REPO_ROOT] [--base origin/main]

REPO_ROOT defaults to the current directory. Skills live two levels deep:
skills/<section>/<skill-name>/SKILL.md. With --base, every skill folder that
differs from that ref (committed, staged or unstaged, including a move between
sections) must also carry a higher `version` than it has on the base ref.

Prints one PASS/FAIL/WARN line per check and exits 1 if anything FAILs.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
SUPPORT_PATH_RE = re.compile(r"(?<![\w/.-])((?:references|assets|scripts|templates)/[A-Za-z0-9_.\-/]+)")
PLATFORMS = {"linux", "macos", "windows"}
# Distinctive Claude-only names and machine-local paths that must not appear in a SKILL.md.
FORBIDDEN = [
    (re.compile(r"\bAskUserQuestion\b"), "Claude tool AskUserQuestion (use clarify)"),
    (re.compile(r"\bToolSearch\b"), "Claude tool ToolSearch"),
    (re.compile(r"\bTodoWrite\b"), "Claude tool TodoWrite (use todo)"),
    (re.compile(r"^allowed-tools:", re.M), "allowed-tools frontmatter"),
    (re.compile(r"~/\.claude|%USERPROFILE%\\\.claude"), "~/.claude path"),
    (re.compile(r"~/\.hermes"), "hardcoded ~/.hermes (use $HERMES_HOME)"),
    (re.compile(r"\b(?:plugin|marketplace)\.json\b"), "Claude plugin manifest"),
    (re.compile(r"[A-Za-z]:\\Users\\[^\\\s`]+"), "Windows user path"),
    (re.compile(r"(?<![\w$])/(?:Users|home)/[a-z][\w.-]*/", re.I), "machine-local home path"),
    (re.compile(r"\bsearchDocumentation\b|\bgetPage\b|\baskQuestion\b"), "live wiki call"),
]

results: list[tuple[str, str, str]] = []


def report(status: str, check: str, detail: str = "") -> None:
    results.append((status, check, detail))


# ---------------------------------------------------------------- frontmatter

def _scalar(v: str):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        return [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        return v[1:-1]
    return v


def _mini_yaml(text: str) -> dict:
    """Tiny parser for the house frontmatter shape (scalars, flow lists, nested maps)."""
    root: dict = {}
    stack = [(-1, root)]
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        m = re.match(r"\s*([A-Za-z0-9_.-]+):\s*(.*)$", raw)
        if not m:
            raise ValueError(f"unparseable line: {raw!r}")
        key, val = m.group(1), m.group(2)
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if val == "":
            parent[key] = {}
            stack.append((indent, parent[key]))
        else:
            parent[key] = _scalar(val)
    return root


def parse_frontmatter(text: str):
    if not text.startswith("---"):
        raise ValueError("does not start with ---")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValueError("no closing ---")
    block = text[3:end].strip("\n")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(block)
    except ImportError:
        data = _mini_yaml(block)
    if not isinstance(data, dict):
        raise ValueError("frontmatter is not a mapping")
    return data, text[end + 4:]


# ---------------------------------------------------------------- checks

def check_skill(d: Path, repo_skills: set[str]) -> None:
    folder = d.name
    sk = d / "SKILL.md"
    if not sk.is_file():
        report("FAIL", f"{folder}: SKILL.md exists")
        return
    text = sk.read_text(encoding="utf-8")
    try:
        fm, body = parse_frontmatter(text)
    except Exception as e:  # noqa: BLE001
        report("FAIL", f"{folder}: frontmatter parses", str(e))
        return

    name = fm.get("name")
    ok = name == folder and isinstance(name, str) and NAME_RE.match(name) and len(name) <= 64
    report("PASS" if ok else "FAIL", f"{folder}: name == folder, lowercase-hyphen, <=64", f"name={name!r}")

    desc = fm.get("description")
    probs = []
    if not isinstance(desc, str):
        probs.append("missing")
    else:
        if len(desc) > 60:
            probs.append(f"{len(desc)} chars > 60")
        if not desc.startswith("Use when"):
            probs.append("does not start 'Use when'")
        if not desc.endswith("."):
            probs.append("does not end with '.'")
    report("FAIL" if probs else "PASS", f"{folder}: description rules", "; ".join(probs) or repr(desc))

    ver = str(fm.get("version", ""))
    report("PASS" if SEMVER_RE.match(ver) else "FAIL", f"{folder}: version is semver", ver)

    author = str(fm.get("author", ""))
    report("PASS" if author.startswith("Bitpool") else "FAIL", f"{folder}: author credits Bitpool first", author)

    lic = fm.get("license")
    report("PASS" if lic == "Proprietary" else "FAIL", f"{folder}: license Proprietary", str(lic))

    plats = fm.get("platforms")
    ok = isinstance(plats, list) and plats and set(plats) <= PLATFORMS
    report("PASS" if ok else "FAIL", f"{folder}: platforms valid", str(plats))

    hermes = (fm.get("metadata") or {}).get("hermes") or {}
    tags = hermes.get("tags") or []
    report("PASS" if isinstance(tags, list) and "bitpool" in tags else "FAIL", f"{folder}: tags include bitpool", str(tags))
    report("PASS" if hermes.get("category") == "bitpool" else "FAIL", f"{folder}: category bitpool", str(hermes.get("category")))
    rel = hermes.get("related_skills") or []
    unknown = [r for r in rel if r not in repo_skills]
    if unknown:
        report("WARN", f"{folder}: related_skills in repo", f"not in this repo: {unknown} (OK only if bundled with Hermes)")
    else:
        report("PASS", f"{folder}: related_skills in repo")

    # support paths named in SKILL.md exist
    missing = []
    for m in SUPPORT_PATH_RE.finditer(text):
        p = m.group(1).rstrip(".,;:)/")
        if any(c in p for c in "<[*{"):
            continue
        if p.endswith("/"):
            p = p[:-1]
        if p.count("/") == 0:
            continue
        if not (d / p).exists():
            missing.append(p)
    report("FAIL" if missing else "PASS", f"{folder}: named support paths exist", ", ".join(sorted(set(missing))))

    # ../ escapes and forbidden strings, across every text file in the skill
    hits = []
    for f in d.rglob("*"):
        if not f.is_file() or f.suffix.lower() not in {".md", ".txt", ".yaml", ".yml", ".template"}:
            continue
        t = f.read_text(encoding="utf-8", errors="replace")
        rel_f = f.relative_to(d).as_posix()
        if re.search(r"\]\((?:\.\./)+", t) or re.search(r"(?:references|assets|scripts|templates)/\.\./", t):
            hits.append(f"{rel_f}: ../ link out of the skill")
        if f.name == "SKILL.md":
            for rx, why in FORBIDDEN:
                for mm in rx.finditer(t):
                    line = t.count("\n", 0, mm.start()) + 1
                    hits.append(f"{rel_f}:{line}: {why}")
    report("FAIL" if hits else "PASS", f"{folder}: no Claude-only names, local paths or ../ escapes", " | ".join(hits))

    lines = body.count("\n")
    report("WARN" if lines > 220 else "PASS", f"{folder}: SKILL.md body size", f"{lines} lines")


def readme_rows(readme: Path) -> dict[str, str]:
    """{skill-name: section} from the README Skills tables. Each table sits under a
    `### `<section>`` heading naming its skills/<section>/ folder."""
    rows: dict[str, str] = {}
    in_skills = False
    section = ""
    for line in readme.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_skills = line.strip() == "## Skills"
        if not in_skills:
            continue
        h = re.match(r"^###\s+`([a-z0-9-]+)`", line)
        if h:
            section = h.group(1)
            continue
        m = re.match(r"^\|\s*`([a-z0-9-]+)`\s*\|", line)
        if m:
            rows[m.group(1)] = section
    return rows


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


def check_versions(repo: Path, base: str, skills: dict[str, Path]) -> None:
    """skills = {name: folder}. A skill is 'touched' if any file under its current folder
    changed, or if its SKILL.md lived at a different path on the base ref (a move)."""
    try:
        changed = set(git(repo, "diff", "--name-only", base, "--", "skills").split())
        changed |= set(git(repo, "ls-files", "--others", "--exclude-standard", "--", "skills").split())
        base_files = git(repo, "ls-tree", "-r", "--name-only", base, "--", "skills").split()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        report("FAIL", f"version bump vs {base}", f"git failed: {e}")
        return
    # where each skill's SKILL.md lived on the base ref (flat or sectioned layout)
    base_path = {p.split("/")[-2]: p for p in base_files if p.endswith("/SKILL.md")}
    for s, folder in sorted(skills.items()):
        rel = folder.relative_to(repo).as_posix() + "/"
        cur_md = rel + "SKILL.md"
        moved = s in base_path and base_path[s] != cur_md
        if not moved and not any(p.startswith(rel) for p in changed):
            continue
        cur = SEMVER_RE.match(str(parse_frontmatter((folder / "SKILL.md").read_text(encoding="utf-8"))[0].get("version", "")))
        if s not in base_path:
            report("PASS" if cur else "FAIL", f"{s}: new skill has a version", "new on this branch")
            continue
        old_text = git(repo, "show", f"{base}:{base_path[s]}")
        old = SEMVER_RE.match(str(parse_frontmatter(old_text)[0].get("version", "")))
        ok = bool(cur and old and tuple(map(int, cur.groups())) > tuple(map(int, old.groups())))
        report("PASS" if ok else "FAIL", f"{s}: version bumped vs {base}",
               f"{old.group(0) if old else '?'} -> {cur.group(0) if cur else '?'}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--base", help="git ref to compare versions against, e.g. origin/main")
    a = ap.parse_args()
    repo = Path(a.repo).resolve()
    skills_dir = repo / "skills"
    if not skills_dir.is_dir():
        print(f"FAIL  no skills/ folder under {repo}")
        return 1
    visible = lambda p: p.is_dir() and not p.name.startswith((".", "_"))  # noqa: E731
    sections = sorted(p for p in skills_dir.iterdir() if visible(p))
    stray = [p.name for p in sections if (p / "SKILL.md").exists()]
    report("FAIL" if stray else "PASS", "layout: no skill directly under skills/ (use skills/<section>/<skill>/)",
           ", ".join(stray))
    bad_sec = [p.name for p in sections if not NAME_RE.match(p.name)]
    report("FAIL" if bad_sec else "PASS", "layout: section folders lowercase-hyphen", ", ".join(bad_sec))
    folders = sorted(d for sec in sections if not (sec / "SKILL.md").exists() for d in sec.iterdir() if visible(d))
    seen: dict[str, Path] = {}
    dupes = []
    for d in folders:
        if d.name in seen:
            dupes.append(f"{d.name} ({seen[d.name].parent.name}, {d.parent.name})")
        seen[d.name] = d
    report("FAIL" if dupes else "PASS", "layout: skill names unique across sections", ", ".join(dupes))
    names = set(seen)
    for d in folders:
        check_skill(d, names)

    readme = repo / "README.md"
    if readme.is_file():
        rows = readme_rows(readme)
        no_row = sorted(names - set(rows))
        no_folder = sorted(set(rows) - names)
        report("FAIL" if no_row else "PASS", "README: every skill folder has a row", ", ".join(no_row))
        report("FAIL" if no_folder else "PASS", "README: every row has a skill folder", ", ".join(no_folder))
        wrong = sorted(f"{n} (README: {rows[n] or 'no section heading'}, folder: {seen[n].parent.name})"
                       for n in names & set(rows) if rows[n] != seen[n].parent.name)
        report("FAIL" if wrong else "PASS", "README: each row sits under its folder's section heading", ", ".join(wrong))
        retired = repo / "retired"
        if retired.is_dir():
            retired_names = {d.name for d in retired.rglob("*") if d.is_dir() and (d / "SKILL.md").exists()}
            stale = sorted(retired_names & set(rows))
            report("FAIL" if stale else "PASS", "README: no rows for retired skills", ", ".join(stale))
    else:
        report("FAIL", "README.md exists")

    if a.base:
        check_versions(repo, a.base, seen)

    width = max(len(c) for _, c, _ in results)
    for status, check, detail in results:
        print(f"{status:4}  {check:<{width}}  {detail}".rstrip())
    fails = sum(1 for s, _, _ in results if s == "FAIL")
    warns = sum(1 for s, _, _ in results if s == "WARN")
    print(f"\n{len(results)} checks: {fails} FAIL, {warns} WARN")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
