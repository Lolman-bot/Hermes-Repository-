#!/usr/bin/env python3
"""Run the quarterly configuration-baseline cycle: status, generate, diff, ratify, pack.

WHY THIS EXISTS
---------------
Each part of the cycle already has its own script. The exporter places a dated dump,
generate_baseline.py turns it into rows, diff_baseline.py compares two cycles, and
build_evidence_pack.py renders the auditor artefact. None of them was the problem. The
problem was the glue typed by hand around them each quarter, and every piece of that
glue has a way to go wrong that still produces a convincing answer:

    --generated-at read from the clock    rows never regenerate byte-identical, so git
                                          shows churn and hides the real change
    the wrong id map                      every row renumbered, every citation broken
    diffed against last quarter's folder  a comparison against an unratified dump is
      instead of the RATIFIED one         not a comparison against the standard
    the standard page edited by hand      the page and the rows quietly disagree

This file is that glue, written down once, so "do the diff next time" is one command:

    run_config_cycle.py status
    run_config_cycle.py generate 2026-12-20
    run_config_cycle.py diff                  # RATIFIED against the newest folder
    run_config_cycle.py pack 2026-12-20

It is deliberately thin. It NEVER imports the other scripts. It runs them through their
CLIs with sys.executable, as a person would, so the documented CLI stays the only
contract between them and a rewrite of one cannot quietly change what this does. Before
it passes an optional flag (--definitions, --readme) it reads the script's --help, so
an older script gets a warning rather than a crash.

THE ONE THING IT WRITES ITSELF: RATIFICATION
--------------------------------------------
A standard is normative. It changes only by a deliberate, reviewed act, never
automatically each cycle. So ratify is its own subcommand that nothing else calls, and
it takes the approver's name on the command line:

    run_config_cycle.py ratify 2026-09-25 --approved-by "Eric Sharp" --dry-run
    run_config_cycle.py ratify 2026-09-25 --approved-by "Eric Sharp"

It refuses unless all of these hold: baseline-rows.json was generated from the raw dump
beside it (meta.source_sha256), the raw files still match collection-manifest.json, and
every row id agrees with id-map.json. It also refuses a folder whose provenance would
make a weak standard, unless the named flag says the approver has seen it:

    no collection-manifest.json           --allow-missing-manifest
        undated and unattributed: nothing records when it was collected, by whom, or
        that the raw files are what Graph returned
    the manifest records incidents        --accept-incomplete-baseline
        a truncated list or a failed assignments request reads exactly like a removed
        setting or an unassigned policy. With the flag every incident is printed
        beside the approver's name. A malformed incidents list has no override
    any label is left raw                 --allow-raw-labels
        display resolution is not 'catalog', so every Setting and Required value on
        the pages would be a raw Graph id; or it is 'catalog' but records unresolved
        rows (a definition or option label the export did not fetch), or records no
        usable unresolved count at all. Refusal and --dry-run alike print the count
        and every affected row by BP- id and setting id, so the approver sees them
        before approving. With the flag they are printed beside the approver's name

Every refusal that applies is reported together, so one --dry-run shows the approver
all of them rather than one per attempt.

It then changes three things on each hardening-standard page, and nothing else:

    the lines between  <!-- GENERATED:START -->  and  <!-- GENERATED:END -->
    five approval-header value cells: Version, Approved by, Approved on,
      Effective from, Ratified from
    two frontmatter keys: status, last_reviewed

Every other byte of the page stays exactly as a human wrote it. All three pages are
checked before any is written, so a refusal never leaves the set half-ratified.
RATIFIED is written last. A later date bumps the minor version (1.0 -> 1.1).

Re-ratifying the same date is idempotent when nothing would change: the version, the
approval date and the page bytes stay the same. When something WOULD change -- the rows
were regenerated, the approver differs, --approved-on names another day -- that is a new
approval, not a re-run, and one version number must never carry two contents. So ratify
refuses it unless --re-ratify is given, and with it records a minor bump approved on
today (or --approved-on).

The Deviation cell is the one cell between the markers a human writes: an approved
departure is recorded there as an EXM- reference into the exemption register. ratify
carries each such cell forward, by BP- id, into the re-rendered row, provided the id
still names the same object and setting. A reference it cannot carry, because the row
is gone or the id now names something else, is printed as a WARNING, never dropped
silently.

PATHS
-----
Every path resolves argv > environment > default:

    --standards-repo  STANDARDS_REPO              nearest ancestor of this script that has
                                                  a security-documentation-restricted child
    --dumps-dir       CONFIG_CYCLE_DUMPS_DIR      <repo>/configuration-hardening/dumps
    --standards-dir   CONFIG_CYCLE_STANDARDS_DIR  <repo>/configuration-hardening
    --generator       CONFIG_CYCLE_GENERATOR      <this dir>/generate_baseline.py
    --differ          CONFIG_CYCLE_DIFFER         <this dir>/diff_baseline.py
    --pack-builder    CONFIG_CYCLE_PACK_BUILDER   <this dir>/build_evidence_pack.py

export-intune-config.sh reads the same STANDARDS_REPO variable, so one export sets both.
Under WSL a Windows path (C:\\...) is translated to /mnt/c/...

EXIT CODES
----------
    0   success. For diff: no differences
    1   diff: differences found. This is a normal cycle, not a failure
        status: an integrity problem: a tampered raw file, stale rows, a dump placed
        with recorded incidents, or RATIFIED and a page's Ratified from disagreeing
    2   error or refusal. A refusal writes nothing

Pure stdlib. Run through WSL.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_DIR_NAME = "security-documentation-restricted"

EXIT_OK, EXIT_FINDING, EXIT_ERROR = 0, 1, 2

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
# The default approval date is Bitpool's calendar day in GMT+10 (user decision, 2026-09-28): an
# approval given at 09:48 on the 28th is dated the 28th, not the UTC 27th. A fixed offset, not
# a named zone, because GMT+10 with no daylight saving is what was decided. Collection times
# and dump folder names stay UTC.
APPROVAL_TZ = dt.timezone(dt.timedelta(hours=10), "GMT+10")

# The dated folder, per the v2 contract.
RAW_DUMP = "intune-config-export.json"
DEFINITIONS = "setting-definitions.json"
MANIFEST = "collection-manifest.json"
ROWS = "baseline-rows.json"
README = "README.md"
PACK = "evidence-pack.html"
# The dumps/ root. Both span cycles, so neither lives inside a dated folder.
ID_MAP = "id-map.json"
RATIFIED = "RATIFIED"

NAME_SETTING = "@displayName"
GENERATOR_MAJOR = 2

MARK_START = "<!-- GENERATED:START -->"
MARK_END = "<!-- GENERATED:END -->"

# The differ writes its two records under these names first. They are renamed into place
# only once this run has provably produced them, so a crash can never leave last
# quarter's report sitting under this quarter's name.
PARTIAL = ".partial-run-config-cycle"
TRACEBACK_RE = re.compile(r"(?m)^Traceback \(most recent call last\):")

ROW_ID_RE = re.compile(r"^BP-[A-Z]{3}-\d{4,}$")
# What a Deviation cell holds when there is no deviation. Anything else is a human's
# EXM- reference, and ratify carries it forward rather than overwrite it.
NO_DEVIATION = ("", "none", "—", "-")

# Every approval-header row the contract names. Ratify refuses a page missing any of
# them, because a half-present header is how a page ends up looking approved when it
# is not.
HEADER_LABELS = ("Standard ID", "Version", "Approved by", "Approved on", "Effective from",
                 "Ratified from", "Next review", "Supersedes", "Authority")
# ...and the only ones it writes. Standard ID, Next review, Supersedes and Authority are
# human-owned statements about the standard, not facts about one ratification.
WRITTEN_LABELS = ("Version", "Approved by", "Approved on", "Effective from", "Ratified from")

# platform (as the rows carry it) -> page, and the Standard ID that page must declare.
# Checking the Standard ID stops a mis-named file from receiving another platform's rows.
PAGES = (
    ("windows10", "hardening-standard-windows-endpoints.md", "BP-WIN"),
    ("macOS", "hardening-standard-macos-endpoints.md", "BP-MAC"),
    ("iOS", "hardening-standard-ios-endpoints.md", "BP-IOS"),
)
COLLECTION_ORDER = ("configurationPolicies", "deviceConfigurations",
                    "deviceCompliancePolicies")
ROW_FIELDS = ("row_key", "id", "platform", "collection", "object_id", "object_name",
              "setting_id", "required_value", "mode", "enforced_at")


class CycleError(Exception):
    """A refusal. main() prints it as 'error: ...' and exits 2, never as a traceback."""


# ------------------------------------------------------------------------------ paths

def local_path(value):
    """A path as given, with a Windows drive path translated when running under WSL."""
    text = str(value)
    if os.name == "posix":
        m = re.match(r"^([A-Za-z]):[\\/](.*)$", text)
        if m:
            return Path("/mnt/%s/%s" % (m.group(1).lower(), m.group(2).replace("\\", "/")))
    return Path(text)


def find_standards_repo(start=HERE):
    """The nearest ancestor of this script that has a security-documentation-restricted
    child. In the ai-skills checkout that is the Github-Bitpool folder the two repos
    share. Walking up rather than counting '..' keeps it working if the skill moves."""
    for parent in Path(start).resolve().parents:
        candidate = parent / REPO_DIR_NAME
        if candidate.is_dir():
            return candidate
    return None


def pick(arg_value, env_name, default):
    """argv > environment > default, and say which one won."""
    if arg_value:
        return local_path(arg_value), "argv"
    env_value = os.environ.get(env_name, "").strip()
    if env_value:
        return local_path(env_value), "env %s" % env_name
    value = default() if callable(default) else default
    return (Path(value) if value is not None else None), "default"


class Paths:
    """Every location the cycle touches, resolved once, with where each came from."""

    FIELDS = (
        # attribute, argparse dest, env var, label
        ("standards_repo", "standards_repo", "STANDARDS_REPO", "standards repo"),
        ("dumps", "dumps_dir", "CONFIG_CYCLE_DUMPS_DIR", "dumps"),
        ("standards", "standards_dir", "CONFIG_CYCLE_STANDARDS_DIR", "standards"),
        ("generator", "generator", "CONFIG_CYCLE_GENERATOR", "generator"),
        ("differ", "differ", "CONFIG_CYCLE_DIFFER", "differ"),
        ("pack_builder", "pack_builder", "CONFIG_CYCLE_PACK_BUILDER", "pack builder"),
    )

    def __init__(self, args):
        self.source = {}
        get = lambda dest: getattr(args, dest, None)
        self._set("standards_repo", *pick(get("standards_repo"), "STANDARDS_REPO",
                                          find_standards_repo))
        repo = self.standards_repo
        self._set("dumps", *pick(get("dumps_dir"), "CONFIG_CYCLE_DUMPS_DIR",
                                 lambda: repo / "configuration-hardening" / "dumps"
                                 if repo else None))
        self._set("standards", *pick(get("standards_dir"), "CONFIG_CYCLE_STANDARDS_DIR",
                                     lambda: repo / "configuration-hardening"
                                     if repo else None))
        self._set("generator", *pick(get("generator"), "CONFIG_CYCLE_GENERATOR",
                                     HERE / "generate_baseline.py"))
        self._set("differ", *pick(get("differ"), "CONFIG_CYCLE_DIFFER",
                                  HERE / "diff_baseline.py"))
        self._set("pack_builder", *pick(get("pack_builder"), "CONFIG_CYCLE_PACK_BUILDER",
                                        HERE / "build_evidence_pack.py"))

    def _set(self, name, value, source):
        setattr(self, name, value)
        self.source[name] = source

    def require(self, name):
        value = getattr(self, name)
        if value is None:
            raise CycleError(
                "cannot locate the %s. No security-documentation-restricted checkout was "
                "found beside this script.\n"
                "       Pass --standards-repo PATH or set STANDARDS_REPO." % name)
        return value

    def describe(self, names):
        for attr, _dest, _env, label in self.FIELDS:
            if attr in names:
                print("%-15s %s   (%s)" % (label, getattr(self, attr), self.source[attr]))


# --------------------------------------------------------------------------- helpers

def valid_date(text):
    if not isinstance(text, str) or not DATE_RE.match(text):
        return False
    try:
        dt.date.fromisoformat(text)
    except ValueError:
        return False
    return True


def date_arg(text):
    if not valid_date(text):
        raise argparse.ArgumentTypeError("expected a YYYY-MM-DD date, got %r" % text)
    return text


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path, what):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except OSError as exc:
        raise CycleError("cannot read %s %s: %s" % (what, path, exc))
    except ValueError as exc:
        raise CycleError("%s %s is not valid JSON: %s" % (what, path, exc))


def atomic_write(path, data):
    """Write bytes via a sibling temp file and a rename, so a crash mid-write never
    leaves a half-written standard page or RATIFIED file."""
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp-run-config-cycle")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def dated_folders(dumps):
    if not dumps.is_dir():
        raise CycleError("dumps folder not found: %s" % dumps)
    return sorted(p.name for p in dumps.iterdir() if p.is_dir() and valid_date(p.name))


def existing_folder(dumps, date):
    folder = dumps / date
    if not folder.is_dir():
        have = ", ".join(dated_folders(dumps)) or "none"
        raise CycleError("no dated folder %s under %s (have: %s)" % (date, dumps, have))
    return folder


def read_ratified(dumps):
    """The ratified folder's name, or None. RATIFIED is one YYYY-MM-DD line. Anything
    else is refused rather than guessed at, because it decides what 'the standard' is."""
    path = dumps / RATIFIED
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    value = text.strip()
    if not valid_date(value):
        raise CycleError("%s must hold exactly one YYYY-MM-DD line, found %r"
                         % (path, text[:60]))
    return value


def load_manifest(folder):
    path = folder / MANIFEST
    if not path.is_file():
        return None
    manifest = read_json(path, "manifest")
    if not isinstance(manifest, dict) or not isinstance(manifest.get("files"), dict):
        raise CycleError("%s has no 'files' object, so it cannot vouch for anything" % path)
    return manifest


def check_manifest(folder, manifest):
    """[(file, state, detail)] where state is ok, MISMATCH, MISSING or INVALID. Only files
    the manifest records are checked: generated files are never in it, by design."""
    results = []
    for name in sorted(manifest["files"]):
        record = manifest["files"][name]
        if (not isinstance(name, str) or not name or name in (".", "..")
                or "/" in name or "\\" in name):
            results.append((str(name), "INVALID", "not a plain file name"))
            continue
        path = folder / name
        if not isinstance(record, dict) or not isinstance(record.get("sha256"), str):
            results.append((name, "INVALID", "no sha256 recorded"))
            continue
        if not path.is_file():
            results.append((name, "MISSING", "recorded in the manifest, absent on disk"))
            continue
        actual = sha256_file(path)
        size = path.stat().st_size
        if actual != record["sha256"].lower():
            results.append((name, "MISMATCH", "manifest sha256 %s..., on disk %s..."
                            % (record["sha256"][:16], actual[:16])))
        elif isinstance(record.get("bytes"), int) and record["bytes"] != size:
            results.append((name, "MISMATCH", "manifest %d bytes, on disk %d"
                            % (record["bytes"], size)))
        else:
            results.append((name, "ok", actual[:16]))
    return results


def require_manifest_intact(folder):
    manifest = load_manifest(folder)
    if manifest is None:
        return None
    bad = [r for r in check_manifest(folder, manifest) if r[1] != "ok"]
    if bad:
        raise CycleError(
            "%s/%s no longer matches the files it records:\n%s\n"
            "       The raw files are evidence and must be byte-for-byte what Graph "
            "returned. Restore them from git." % (folder.name, MANIFEST, "\n".join(
                "       %-9s %s  %s" % (state, name, detail) for name, state, detail in bad)))
    return manifest


def load_rows(path):
    doc = read_json(path, "baseline")
    if (not isinstance(doc, dict) or not isinstance(doc.get("rows"), list)
            or not isinstance(doc.get("meta"), dict)):
        raise CycleError("%s is not a baseline (needs 'meta' and a 'rows' list)" % path)
    return doc


def generator_major(doc):
    m = re.match(r"^(\d+)\.", str(doc["meta"].get("generator_version") or ""))
    return int(m.group(1)) if m else None


def rows_current(folder, doc):
    """(ok, detail): do these rows describe the raw dump beside them?"""
    raw = folder / RAW_DUMP
    if not raw.is_file():
        return False, "%s is missing" % RAW_DUMP
    recorded = doc["meta"].get("source_sha256")
    actual = sha256_file(raw)
    if recorded != actual:
        return False, ("rows record source_sha256 %s..., the raw dump is %s..."
                       % (str(recorded)[:16], actual[:16]))
    return True, actual


def text_value(value):
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def terminal_safe(text):
    """Untrusted text (an incident carries Graph's error message) made safe to print:
    control characters, terminal escapes included, shown as '?'."""
    return re.sub(r"[\x00-\x1f\x7f]", "?", str(text))


def indented_list(items):
    return "\n".join("                  - %s" % terminal_safe(item) for item in items)


def manifest_incidents(manifest):
    """(incidents, malformed). incidents is the manifest's list, or None when it records
    none at all -- a manifest from an exporter older than incident recording, which
    therefore says nothing either way about completeness."""
    if "incidents" not in manifest:
        return None, None
    value = manifest["incidents"]
    if not isinstance(value, list) or not all(isinstance(i, str) for i in value):
        return None, "'incidents' is not a list of strings, so completeness is unknown"
    return value, None


def _value_texts(value):
    """The raw value as text, plus each element when it is a rendered collection (a JSON
    array), so an option miss on one element of a choice collection finds its row."""
    texts = {text_value(value)}
    parsed = value
    if isinstance(value, str) and value.startswith("["):
        try:
            parsed = json.loads(value)
        except ValueError:
            parsed = None
    if isinstance(parsed, list):
        texts.update(text_value(v) for v in parsed)
    return texts


def label_resolution(doc):
    """What display resolution left as a raw Graph id, read from meta.display_resolution.

    Returns {mode, resolved, count, rows, unmatched, unfetched}:
        count      the recorded unresolved count, or None when it is absent or not a
                   non-negative integer -- then nobody knows whether every label resolved
        rows       [(row id, setting, reason)] for each row the recorded misses name. A
                   missing definition names every row of that setting; a missing option
                   names a row only when its required value is, or holds, that option
        unmatched  recorded misses no row was tied to, so they are still shown
        unfetched  definition ids the exporter recorded it could not fetch

    The count is the authority. The rows are how the approver finds them on the pages."""
    resolution = doc["meta"].get("display_resolution")
    res = resolution if isinstance(resolution, dict) else {}
    count = res.get("unresolved")
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        count = None

    def strings(key):
        value = res.get(key)
        return [v for v in value if isinstance(v, str)] if isinstance(value, list) else []

    missing_defs = {d.casefold(): d for d in strings("missing_definitions")}
    missing_opts = {}
    for entry in strings("missing_options"):
        base, sep, value = entry.partition(" = ")
        if sep:
            missing_opts.setdefault(base.casefold(), {})[value] = entry
    rows, used = [], set()
    for row in doc["rows"]:
        if not isinstance(row, dict) or row.get("setting_id") == NAME_SETTING:
            continue
        setting_id = str(row.get("setting_id"))
        rid = str(row.get("id") or row.get("row_key"))
        base = setting_id.split("#")[0].casefold()
        if base in missing_defs:
            used.add(missing_defs[base])
            rows.append((rid, setting_id, "no setting definition"))
        elif base in missing_opts:
            hit = sorted(v for v in _value_texts(row.get("required_value"))
                         if v in missing_opts[base])
            if hit:
                used.update(missing_opts[base][v] for v in hit)
                rows.append((rid, "%s = %s" % (setting_id, text_value(row.get("required_value"))),
                             "no option label for %s" % ", ".join(hit)))
    recorded = sorted(missing_defs.values()) + sorted(
        e for per in missing_opts.values() for e in per.values())
    return {"mode": res.get("mode"), "resolved": res.get("resolved"), "count": count,
            "rows": rows, "unmatched": [e for e in recorded if e not in used],
            "unfetched": strings("unfetched_at_export")}


def label_listing(labels):
    """The lines that show an approver every raw label: one per affected row, then any
    recorded miss no row was tied to, then any shortfall against the recorded count."""
    lines = ["%s  %s  (%s)" % row for row in labels["rows"]]
    lines += ["setting %s  (recorded unresolved; no row matched it)" % entry
              for entry in labels["unmatched"]]
    count = labels["count"]
    if count is not None and count > len(labels["rows"]):
        lines.append("%d more unresolved row(s) that the rows file does not name"
                     % (count - len(labels["rows"])))
    if labels["unfetched"]:
        lines.append("the exporter recorded %d setting definition(s) it could not fetch: %s"
                     % (len(labels["unfetched"]), ", ".join(labels["unfetched"])))
    return lines


def label_summary(labels):
    count = labels["count"]
    return ("%s unresolved row(s) in display resolution 'catalog' (%s resolved): each "
            "Setting or Required value below would show a raw Graph id or value, not a "
            "human label" % ("an unknown number of" if count is None else count,
                             labels["resolved"] if labels["resolved"] is not None else "?"))


def split_cells(line):
    """Cells of a GFM table row, stripped. A pipe is escaped only when an odd number of
    backslashes precede it, which is how micromark (GitBook) reads a row and how
    md_text and md_code escape one."""
    cells, cell, run = [], [], 0
    for ch in line_body(line).strip():
        if ch == "|" and run % 2 == 0:
            cells.append("".join(cell))
            cell = []
        else:
            cell.append(ch)
        run = run + 1 if ch == "\\" else 0
    cells.append("".join(cell))
    return [c.strip() for c in cells[1:-1]]


def page_ratified_from(text):
    """(dated folder the page's 'Ratified from' cell names, or None; problem, or None).
    Only lines outside the markers count: a policy named 'Ratified from' is rendered in
    the Excluded table inside them and must never be read as the approval header."""
    hits, inside = [], False
    for line in text.splitlines():
        if line.strip() == MARK_START:
            inside = True
        elif line.strip() == MARK_END:
            inside = False
        elif not inside and re.match(r"^\|[ \t]*Ratified from[ \t]*\|", line):
            hits.append(line)
    if len(hits) != 1:
        return None, "has %d '| Ratified from |' rows outside the markers, not 1" % len(hits)
    m = re.search(r"dumps/(\d{4}-\d{2}-\d{2})", hits[0])
    return (m.group(1) if m else None), None


def page_agreement(paths, ratified):
    """One entry per standard page: the folder its 'Ratified from' names, and a problem
    when that is not the folder RATIFIED names. kind is 'disagree' for a positive
    disagreement and 'unreadable' when the page cannot be checked. None when there is
    no standards folder to check at all.

    RATIFIED and every page must name the same folder. If they do not, the standard the
    pages state and the baseline diff defaults to are two different things."""
    standards = paths.standards
    if standards is None or not Path(standards).is_dir():
        return None
    out = []
    for _platform, name, _sid in PAGES:
        page = Path(standards) / name
        entry = {"page": name, "named": None, "kind": None, "problem": None}
        out.append(entry)
        if not page.is_file():
            entry.update(kind="unreadable", problem="standard page %s not found" % page)
            continue
        try:
            text = page.read_bytes().decode("utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            entry.update(kind="unreadable", problem="cannot read %s: %s" % (page, exc))
            continue
        named, err = page_ratified_from(text)
        entry["named"] = named
        if err:
            entry.update(kind="unreadable", problem="%s %s" % (name, err))
        elif named != ratified:
            if ratified is None:
                problem = ("%s is Ratified from dumps/%s, but no usable RATIFIED file "
                           "names it" % (name, named))
            elif named is None:
                problem = ("RATIFIED names %s, but %s names no folder in its Ratified from "
                           "cell" % (ratified, name))
            else:
                problem = ("RATIFIED names %s, but %s is Ratified from dumps/%s"
                           % (ratified, name, named))
            entry.update(kind="disagree", problem=problem)
    return out


def require_pages_agree(paths, ratified, why):
    """Refuse to use RATIFIED as a default while any page names another folder."""
    agreement = page_agreement(paths, ratified)
    if agreement is None:
        print("warning         no standards folder, so the pages' Ratified from cells were "
              "not checked against RATIFIED")
        return
    for entry in agreement:
        if entry["kind"] == "unreadable":
            print("warning         %s" % entry["problem"])
    disagree = [e["problem"] for e in agreement if e["kind"] == "disagree"]
    if disagree:
        raise CycleError(
            "RATIFIED and the standard pages disagree:\n%s\n"
            "       %s would then not be the standard the pages state. Run status, repair "
            "the disagreement, or pass --baseline explicitly."
            % ("\n".join("       %s" % p for p in disagree), why))


# ------------------------------------------------------------------ running the tools

def child_env():
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    return env


_HELP = {}


def tool_help(script):
    key = str(script)
    if key not in _HELP:
        proc = subprocess.run([sys.executable, key, "--help"], stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, env=child_env())
        _HELP[key] = proc.stdout.decode("utf-8", "replace")
    return _HELP[key]


def supports(script, flag):
    return re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(flag), tool_help(script)) is not None


def run_tool(script, args, capture=False, watch_crash=False):
    """Run a sibling script through its CLI. Returns (exit code, stdout or None).

    watch_crash captures stderr, echoes it, and refuses a run that printed a Python
    traceback. That matters for the differ, whose exit 1 means 'differences found': an
    uncaught exception, or an import that fails, ALSO exits 1, and must never be read
    as a result."""
    script = Path(script)
    if not script.is_file():
        raise CycleError("%s not found at %s" % (script.name, script))
    args = [str(a) for a in args]
    print("run             %s %s" % (script.name, " ".join(shlex.quote(a) for a in args)),
          flush=True)
    cmd = [sys.executable, str(script)] + args
    proc = subprocess.run(cmd, stdout=subprocess.PIPE if capture else None,
                          stderr=subprocess.PIPE if watch_crash else None, env=child_env())
    if watch_crash:
        err = proc.stderr.decode("utf-8", "replace")
        sys.stdout.flush()
        sys.stderr.write(err)
        sys.stderr.flush()
        if TRACEBACK_RE.search(err):
            raise CycleError("%s crashed (exit %d, traceback above). A crash is not a "
                             "result, so nothing from this run was recorded."
                             % (script.name, proc.returncode))
    return proc.returncode, (proc.stdout.decode("utf-8") if capture else None)


# ---------------------------------------------------------------------------- status

def cmd_status(paths, args):
    dumps = paths.require("dumps")
    paths.describe({"standards_repo", "dumps", "standards"})
    problems, notes = [], []

    try:
        ratified = read_ratified(dumps)
    except CycleError as exc:
        ratified = None
        problems.append(str(exc))
    folders = dated_folders(dumps)
    print("%-15s %s" % ("RATIFIED", ratified or "(none -- nothing ratified yet)"))
    if ratified and ratified not in folders:
        problems.append("RATIFIED names %s, but there is no such dated folder" % ratified)

    id_map = dumps / ID_MAP
    if not id_map.is_file():
        print("%-15s (absent -- the first generate creates it)" % "id-map")
    else:
        try:
            data = read_json(id_map, "id map")
        except CycleError as exc:
            data = None
            problems.append(str(exc))
        if isinstance(data, dict) and data.get("schema") == 2 and isinstance(
                data.get("ids"), dict):
            print("%-15s schema 2, %d ids" % ("id-map", len(data["ids"])))
        elif data is not None:
            print("%-15s v1 or unknown shape -- the v2 generator refuses it; delete it and "
                  "regenerate" % "id-map")
            notes.append("id-map.json is not schema 2; generate will be refused until it is "
                         "deleted and regenerated")

    print()
    print("%-11s %-9s %-30s %-24s %s" % ("folder", "ratified", "baseline-rows", "manifest",
                                         "outputs"))
    for name in folders:
        folder = dumps / name
        is_ratified = name == ratified

        rows_state = "-"
        if (folder / ROWS).is_file():
            try:
                doc = load_rows(folder / ROWS)
                version = doc["meta"].get("generator_version") or "?"
                ok, detail = rows_current(folder, doc)
                rows_state = "v%s %s" % (version, "matches dump" if ok else "STALE")
                if not ok and is_ratified:
                    problems.append("%s/%s (RATIFIED): %s -- the ratified standard no "
                                    "longer matches its evidence" % (name, ROWS, detail))
                elif not ok:
                    problems.append("%s/%s: %s -- run generate %s"
                                    % (name, ROWS, detail, name))
                labels = label_resolution(doc)
                if labels["mode"] != "catalog":
                    notes.append("%s/%s has display resolution %s: every Setting and Required "
                                 "value is a raw Graph id, and ratify %s needs "
                                 "--allow-raw-labels"
                                 % (name, ROWS, repr(labels["mode"]) if labels["mode"]
                                    else "not recorded", name))
                elif labels["count"] is None or labels["count"] > 0:
                    notes.append("%s/%s has %s unresolved label(s) in display resolution "
                                 "'catalog', and ratify %s needs --allow-raw-labels. "
                                 "ratify %s --dry-run lists every affected row"
                                 % (name, ROWS, "an unknown number of" if labels["count"]
                                    is None else labels["count"], name, name))
            except CycleError as exc:
                rows_state = "UNREADABLE"
                problems.append(str(exc))

        manifest_state = "none"
        try:
            manifest = load_manifest(folder)
        except CycleError as exc:
            manifest, manifest_state = None, "UNREADABLE"
            problems.append(str(exc))
        if manifest is not None:
            results = check_manifest(folder, manifest)
            bad = [r for r in results if r[1] != "ok"]
            manifest_state = ("ok (%d files)" % len(results) if not bad
                              else "BAD (%d of %d)" % (len(bad), len(results)))
            for file_name, state, detail in bad:
                problems.append("%s/%s: %s -- %s" % (name, file_name, state, detail))
            recorded_date = manifest.get("collection_date")
            if recorded_date and recorded_date != name:
                problems.append("%s/%s records collection_date %s -- the folder is misdated"
                                % (name, MANIFEST, recorded_date))
            incidents, malformed = manifest_incidents(manifest)
            if malformed:
                problems.append("%s/%s: %s" % (name, MANIFEST, malformed))
            elif incidents is None:
                notes.append("%s/%s records no incidents list (an exporter older than "
                             "incident recording), so whether the dump is complete is not "
                             "recorded" % (name, MANIFEST))
            elif incidents:
                manifest_state += " INCOMPLETE"
                problems.append(
                    "%s was placed INCOMPLETE: %s records %d incident(s). Missing data reads "
                    "exactly like a removed setting or an unassigned policy:\n%s"
                    % (name, MANIFEST, len(incidents), indented_list(incidents)))
            tool = manifest.get("tool")
            if isinstance(tool, dict) and tool.get("git_dirty") is True:
                notes.append("%s was collected by an exporter with uncommitted changes "
                             "(tool.git_dirty true, git_commit %s): the code that ran is not "
                             "the code that commit holds"
                             % (name, terminal_safe(tool.get("git_commit") or "null")))
        elif (folder / RAW_DUMP).is_file():
            notes.append("%s has no %s, so its raw files cannot be checked against what "
                         "was collected" % (name, MANIFEST))

        outputs = []
        if (folder / README).is_file():
            outputs.append("README")
        outputs += sorted(p.stem for p in folder.glob("diff-vs-*.md"))
        if (folder / PACK).is_file():
            outputs.append("pack")
        print("%-11s %-9s %-30s %-24s %s" % (name, "RATIFIED" if is_ratified else "",
                                             rows_state, manifest_state,
                                             ", ".join(outputs) or "-"))
    if not folders:
        print("(no dated folders)")

    print()
    agreement = page_agreement(paths, ratified)
    if agreement is None:
        notes.append("no standards folder, so the pages' Ratified from cells were not "
                     "checked against RATIFIED")
    else:
        for entry in agreement:
            shown = ("?" if entry["kind"] == "unreadable"
                     else entry["named"] or "(none)")
            print("%-15s %-42s ratified from %s" % ("page", entry["page"], shown))
            if entry["problem"]:
                problems.append(entry["problem"])

    for note in notes:
        print("note            %s" % note)
    for problem in problems:
        print("PROBLEM         %s" % problem)
    print("status          %s" % ("%d problem(s)" % len(problems) if problems
                                  else "all recorded hashes match"))
    return EXIT_FINDING if problems else EXIT_OK


# -------------------------------------------------------------------------- generate

def generated_at_for(date, manifest):
    """collected_at_utc from the manifest, else midnight UTC on the folder date. Never the
    clock -- that is what makes regenerating a folder byte-identical."""
    if manifest is not None:
        value = manifest.get("collected_at_utc")
        if isinstance(value, str) and TIMESTAMP_RE.match(value):
            return value, "collection-manifest.json collected_at_utc"
        if value is not None:
            print("warning         manifest collected_at_utc %r is not YYYY-MM-DDTHH:MM:SSZ; "
                  "using midnight on the folder date" % (value,))
    return "%sT00:00:00Z" % date, "folder date, midnight UTC (no usable manifest timestamp)"


def cmd_generate(paths, args):
    dumps = paths.require("dumps")
    paths.describe({"dumps", "generator"})
    folder = existing_folder(dumps, args.date)
    raw = folder / RAW_DUMP
    if not raw.is_file():
        raise CycleError("%s/%s is missing -- place the export first" % (args.date, RAW_DUMP))
    manifest = require_manifest_intact(folder)
    generated_at, source = generated_at_for(args.date, manifest)
    print("generated-at    %s   (%s)" % (generated_at, source))

    generator = paths.require("generator")
    if not generator.is_file():
        raise CycleError("generator not found at %s" % generator)
    gen_args = ["--dump", raw, "--out", folder / ROWS, "--id-map", dumps / ID_MAP,
                "--generated-at", generated_at]
    definitions = folder / DEFINITIONS
    if definitions.is_file():
        if supports(generator, "--definitions"):
            gen_args += ["--definitions", definitions]
        else:
            print("warning         %s is present but %s has no --definitions flag; setting "
                  "names and values will be raw" % (DEFINITIONS, generator.name))
    else:
        print("note            no %s in this folder; setting names and values will be raw"
              % DEFINITIONS)
    if supports(generator, "--readme"):
        gen_args += ["--readme", folder / README]

    before = sha256_file(folder / ROWS) if (folder / ROWS).is_file() else None
    code, _ = run_tool(generator, gen_args)
    if code != 0:
        raise CycleError("%s failed (exit %d)" % (generator.name, code))
    if not (folder / ROWS).is_file():
        raise CycleError("%s exited 0 but wrote no %s" % (generator.name, ROWS))
    after = sha256_file(folder / ROWS)
    if not (folder / README).is_file():
        print("warning         %s wrote no %s for %s; the cycle record is missing"
              % (generator.name, README, args.date))

    print("baseline-rows   %s   (%s)" % (after[:16], "unchanged" if before == after else
                                          "new" if before is None else "changed"))
    try:
        ratified = read_ratified(dumps)
    except CycleError:
        ratified = None
    if ratified == args.date and before is not None and before != after:
        print("WARNING         %s is the RATIFIED folder and its rows changed. The standard "
              "pages were rendered from the old rows. Re-rendering them is a new approval "
              "and a new version: review with ratify %s --re-ratify --dry-run first."
              % (args.date, args.date))
    return EXIT_OK


# ------------------------------------------------------------------------------ diff

def yaml_scalar(text):
    if re.match(r"^[A-Za-z0-9][^:#\n\"'`{}\[\]]*$", text) and not text.endswith(" "):
        return text
    return json.dumps(text, ensure_ascii=False)


def with_frontmatter(report, baseline, current):
    """The differ's markdown as a repo page. Leave it alone if the differ already wrote
    frontmatter. Otherwise add frontmatter whose title matches the report's H1, per the
    repo's frontmatter schema."""
    if report.startswith("---\n"):
        return report
    h1 = next((line[2:].strip() for line in report.splitlines() if line.startswith("# ")),
              None)
    title = h1 or "Configuration baseline diff, %s against %s" % (current, baseline)
    body = report if h1 else "# %s\n\n%s" % (title, report)
    front = "\n".join([
        "---",
        "type: Record",
        "title: %s" % yaml_scalar(title),
        "description: %s" % yaml_scalar(
            "Generated comparison of the %s Intune configuration export against the %s "
            "baseline, joined on rename-stable row keys." % (current, baseline)),
        "audience:",
        "  - security-team",
        "  - it-team",
        "  - ai-agents",
        "last_reviewed: %s" % current,
        "status: active",
        "doc_type: record",
        "sources:",
        "  - internal",
        "keywords:",
        "  - configuration-hardening",
        "  - baseline-diff",
        "  - intune",
        "iso27001_controls:",
        "  - \"8.9\"",
        "drata_controls:",
        "  - DCF-12",
        "risk_level: high",
        "requires_admin: false",
        "---",
        "",
    ])
    return front + "\n" + body


def rows_for_diff(dumps, date, role):
    folder = existing_folder(dumps, date)
    path = folder / ROWS
    if not path.is_file():
        raise CycleError("%s folder %s has no %s -- run: generate %s"
                         % (role, date, ROWS, date))
    ok, detail = rows_current(folder, load_rows(path))
    if not ok:
        raise CycleError("%s folder %s: %s. Its rows do not describe its dump, so the "
                         "comparison would be wrong. Run: generate %s" % (role, date, detail,
                                                                         date))
    return path


def cmd_diff(paths, args):
    dumps = paths.require("dumps")
    paths.describe({"dumps", "differ"})
    folders = dated_folders(dumps)
    ratified = read_ratified(dumps)
    baseline = args.baseline or ratified
    if not baseline:
        raise CycleError("no --baseline given and no RATIFIED file in %s. Nothing has been "
                         "ratified, so there is no standard to diff against." % dumps)
    current = args.current or (folders[-1] if folders else None)
    if not current:
        raise CycleError("no dated folders under %s" % dumps)
    print("baseline        %s   (%s)" % (baseline, "argv" if args.baseline else "RATIFIED"))
    print("current         %s   (%s)" % (current, "argv" if args.current else "newest folder"))
    if baseline == current:
        raise CycleError(
            "baseline and current are both %s. A folder diffed against itself always "
            "reports no change, which reads exactly like a clean cycle. Place this "
            "quarter's export first, or pass --current." % baseline)
    if current < baseline:
        print("warning         current %s is older than baseline %s" % (current, baseline))
    if not args.baseline:
        require_pages_agree(paths, ratified, "The default baseline %s" % ratified)

    base_rows = rows_for_diff(dumps, baseline, "baseline")
    curr_rows = rows_for_diff(dumps, current, "current")
    differ = paths.require("differ")
    if not differ.is_file():
        raise CycleError("differ not found at %s" % differ)
    common = ["--baseline", base_rows, "--current", curr_rows]
    if supports(differ, "--baseline-label") and supports(differ, "--current-label"):
        common += ["--baseline-label", baseline, "--current-label", current]
    out_md = dumps / current / ("diff-vs-%s.md" % baseline)
    out_js = dumps / current / ("diff-vs-%s.json" % baseline)

    if supports(differ, "--markdown-out") and supports(differ, "--json-out"):
        return diff_with_records(differ, common, out_md, out_js, baseline, current)
    return diff_per_format(differ, common, out_md, out_js, baseline, current)


def partial_path(path):
    return path.with_name(path.name + PARTIAL)


def remove_quietly(path):
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def earlier_records_note(records):
    """Said on every failure, so a record left over from an earlier run is never taken
    for this run's result."""
    left = [p.name for p in records if p.is_file()]
    if not left:
        return ""
    return ("\n       The %s already in the folder %s from an earlier run, NOT from this one."
            % (" and ".join(left), "is" if len(left) == 1 else "are"))


def decode_record(path, what, differ, note):
    try:
        text = path.read_bytes().decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CycleError("%s wrote a %s record that is not UTF-8 (%s), so this run recorded "
                         "nothing.%s" % (differ.name, what, exc, note))
    if not text.strip():
        raise CycleError("%s wrote an empty %s record, so this run recorded nothing.%s"
                         % (differ.name, what, note))
    return text


def diff_with_records(differ, common, out_md, out_js, baseline, current):
    """One differ run: the text summary to the terminal, the two records to disk.

    The differ writes the records under PARTIAL names this run first cleared, and they
    are renamed into place only after it exited 0 or 1, printed no traceback, and wrote
    both, the json parseable. An exit 1 alone proves nothing: it is 'differences found'
    and also what any uncaught exception exits with. So a crash can never let an earlier
    run's files pass for this run's, and the files already in place are left as they
    were."""
    records = (out_md, out_js)
    tmp_md, tmp_js = partial_path(out_md), partial_path(out_js)
    for path in (tmp_md, tmp_js):
        remove_quietly(path)
    try:
        try:
            code, _ = run_tool(differ, common + ["--format", "text", "--markdown-out",
                                                 tmp_md, "--json-out", tmp_js],
                               watch_crash=True)
        except CycleError as exc:
            raise CycleError("%s%s" % (exc, earlier_records_note(records)))
        note = earlier_records_note(records)
        if code not in (0, 1):
            raise CycleError("%s refused the comparison (exit %d); see its message above.%s"
                             % (differ.name, code, note))
        for path, what in ((tmp_md, "markdown"), (tmp_js, "json")):
            if not path.is_file():
                raise CycleError("%s exited %d but wrote no %s record, so this run recorded "
                                 "nothing.%s" % (differ.name, code, what, note))
        markdown = decode_record(tmp_md, "markdown", differ, note)
        try:
            json.loads(decode_record(tmp_js, "json", differ, note))
        except ValueError as exc:
            raise CycleError("%s wrote a json record that does not parse (%s), so this run "
                             "recorded nothing.%s" % (differ.name, exc, note))
        # The frontmatter is added only to content this run produced.
        if markdown.startswith("---\n"):
            os.replace(tmp_md, out_md)
        else:
            atomic_write(out_md, with_frontmatter(markdown, baseline, current).encode("utf-8"))
        os.replace(tmp_js, out_js)
    finally:
        for path in (tmp_md, tmp_js):
            remove_quietly(path)
    print("wrote           %s" % out_md)
    print("wrote           %s" % out_js)
    return code


def diff_per_format(differ, common, out_md, out_js, baseline, current):
    """An older differ with no record flags: run it once per format. Every run is watched
    for a crash, and nothing is written until the markdown and json runs both succeeded
    with output that is really a report."""
    records = (out_md, out_js)
    nothing = ", so this run recorded nothing."
    try:
        md_code, markdown = run_tool(differ, common + ["--format", "markdown"],
                                     capture=True, watch_crash=True)
        if md_code not in (0, 1):
            raise CycleError("%s refused the comparison (exit %d)%s"
                             % (differ.name, md_code, nothing))
        js_code, js = run_tool(differ, common + ["--format", "json"], capture=True,
                               watch_crash=True)
        if js_code not in (0, 1):
            raise CycleError("%s refused the json report (exit %d)%s"
                             % (differ.name, js_code, nothing))
        if not markdown.strip():
            raise CycleError("%s printed no markdown report%s" % (differ.name, nothing))
        try:
            json.loads(js)
        except ValueError as exc:
            raise CycleError("%s printed a json report that does not parse (%s)%s"
                             % (differ.name, exc, nothing))
    except CycleError as exc:
        raise CycleError("%s%s" % (exc, earlier_records_note(records)))

    atomic_write(out_md, with_frontmatter(markdown, baseline, current).encode("utf-8"))
    atomic_write(out_js, js.encode("utf-8"))
    print("wrote           %s" % out_md)
    print("wrote           %s" % out_js)
    print()
    text_code, _ = run_tool(differ, common + ["--format", "text"], watch_crash=True)
    if text_code not in (0, 1):
        return EXIT_ERROR
    if len({md_code, js_code, text_code}) != 1:
        print("warning         the differ's exit codes disagree across formats (%d/%d/%d)"
              % (md_code, js_code, text_code))
    return max(md_code, js_code, text_code)


# ---------------------------------------------------------------- markdown rendering
# Policy names and setting values are untrusted text: anyone with Intune admin can type
# them. Rendered raw, a '|' breaks the table, a '<script>' or '<!--' becomes live HTML,
# and a policy named '<!-- GENERATED:END -->' would move the marker. Everything below
# escapes before it renders.

_MD_PUNCT = re.compile(r"([\\`*\[\]|~{}])")
_MD_UNDERSCORE = re.compile(r"(?<![A-Za-z0-9])_|_(?![A-Za-z0-9])")
_MD_ENTITY = re.compile(r"&(?=#?[A-Za-z0-9]+;)")


def md_text(value):
    """Plain text for a table cell or heading, rendered literally.

    Only '<' can open raw HTML, so only '<' is always escaped. A '>' mid-cell is
    literal, which keeps 'Intune > collection > name' readable in the page source, and
    '&' is escaped only where it would otherwise read as an entity."""
    s = text_value(value)
    s = _MD_ENTITY.sub("&amp;", s).replace("<", "&lt;")
    s = _MD_PUNCT.sub(r"\\\1", s)
    # An underscore inside a word cannot open emphasis, so only the edges are escaped.
    # That keeps a raw setting id readable in the page source.
    s = _MD_UNDERSCORE.sub(r"\\_", s)
    s = s.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")
    return s.strip()


def md_value(value):
    s = md_text(value)
    return s if s else "*(empty)*"


def md_heading(value):
    return md_text(value).replace("#", "\\#") or "*(unnamed)*"


def md_code(value):
    """A code span that survives a table cell: pipes escaped, line breaks shown as \\n,
    and a fence longer than any backtick run inside.

    Table cells are split before inline parsing, so a pipe needs escaping even inside
    backticks. A backslash run right before a pipe is doubled as well. Otherwise a raw
    value ending in a backslash would turn the escape into an escaped backslash
    followed by a live cell delimiter, which is how micromark (GitBook) reads it."""
    s = text_value(value).replace("\r", "\\r").replace("\n", "\\n")
    s = re.sub(r"(\\*)\|", lambda m: m.group(1) * 2 + "\\|", s)
    longest = max((len(run) for run in re.findall(r"`+", s)), default=0)
    fence = "`" * (longest + 1)
    pad = " " if s.startswith("`") or s.endswith("`") else ""
    return fence + pad + s + pad + fence


def group_objects(rows):
    """Objects in the generator's row order, name row first within each."""
    objects, index = [], {}
    for row in rows:
        key = (row["collection"], row["object_id"])
        if key not in index:
            index[key] = len(objects)
            objects.append({"collection": row["collection"], "object_id": row["object_id"],
                            "object_name": row["object_name"],
                            "object_type": row.get("object_type") or "", "rows": []})
        objects[index[key]]["rows"].append(row)
    for obj in objects:
        obj["rows"].sort(key=lambda r: 0 if r["setting_id"] == NAME_SETTING else 1)
    return objects


def render_block(doc, platform, date, rows_sha, deviations=None):
    """The lines that sit between the markers for one platform. No line endings.

    deviations maps a row id to the Deviation cell to carry forward, verbatim, as a
    human wrote it. Every other row reads 'none'."""
    deviations = deviations or {}
    rows = [r for r in doc["rows"] if r["platform"] == platform]
    scope = doc["meta"].get("scope") or {}
    excluded = [o for o in scope.get("excluded_objects") or []
                if isinstance(o, dict) and o.get("platform") == platform]
    disagreements = [o for o in scope.get("assignment_disagreements") or []
                     if not isinstance(o, dict) or o.get("platform") in (None, platform)]
    objects = group_objects(rows)
    authority = "bitpool:ratified %s" % date

    out = ["",
           "<!-- Generated by run_config_cycle.py ratify from dumps/%s/%s (sha256 %s). "
           "Do not edit between the markers, except a row's Deviation cell (an EXM- "
           "reference), which ratify carries forward by ID. -->" % (date, ROWS,
                                                                   rows_sha[:16]),
           "",
           "### In scope",
           "",
           "| Collection | Objects | Setting instances | Rows |",
           "| --- | --- | --- | --- |"]
    present = [c for c in COLLECTION_ORDER if any(o["collection"] == c for o in objects)]
    present += sorted({o["collection"] for o in objects} - set(COLLECTION_ORDER))
    totals = [0, 0, 0]
    for collection in present:
        objs = [o for o in objects if o["collection"] == collection]
        n_rows = sum(len(o["rows"]) for o in objs)
        n_settings = sum(1 for o in objs for r in o["rows"] if r["setting_id"] != NAME_SETTING)
        counts = (len(objs), n_settings, n_rows)
        totals = [a + b for a, b in zip(totals, counts)]
        out.append("| %s | %d | %d | %d |" % ((md_code(collection),) + counts))
    if present:
        out.append("| **Total** | %d | %d | %d |" % tuple(totals))
    else:
        out.append("| *(none)* | 0 | 0 | 0 |")
    out += ["",
            "Rows are the setting instances plus one `Policy name` row per object, so a "
            "rename shows as one changed row, not as a policy deleted and re-added.",
            "",
            "### Excluded, and why",
            "",
            "| Object | Collection | Object ID | Reason |",
            "| --- | --- | --- | --- |"]
    for obj in excluded:
        out.append("| %s | %s | %s | %s |" % (
            md_value(obj.get("name")), md_code(obj.get("collection") or ""),
            md_code(obj.get("object_id") or ""), md_value(obj.get("reason"))))
    if not excluded:
        out.append("| *(none)* | — | — | — |")
    out.append("")
    if disagreements:
        out += ["**Assignment disagreements: %d.** `isAssigned` and the `assignments` "
                "array disagree. See `meta.scope.assignment_disagreements` in "
                "`dumps/%s/%s`." % (len(disagreements), date, ROWS), ""]

    for obj in objects:
        n_settings = sum(1 for r in obj["rows"] if r["setting_id"] != NAME_SETTING)
        out += ["### %s" % md_heading(obj["object_name"]),
                "",
                "Object ID %s · %s%s · %d setting instance%s" % (
                    md_code(obj["object_id"]), md_code(obj["collection"]),
                    (" · " + md_code(obj["object_type"])) if obj["object_type"] else "",
                    n_settings, "" if n_settings == 1 else "s"),
                "",
                "| ID | Setting | Required value | Authority | Mode | Enforced at | "
                "Deviation | Verify |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        for row in obj["rows"]:
            setting = row.get("setting_name") or row["setting_id"]
            shown = row.get("display_value")
            if shown is None:
                shown = row["required_value"]
            out.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
                md_text(row["id"]), md_value(setting), md_value(shown), authority,
                md_text(row["mode"]), md_value(row["enforced_at"]),
                deviations.get(row["id"], "none"),
                md_code("%s = %s" % (row["setting_id"], text_value(row["required_value"])))))
        out.append("")
    return out


# ---------------------------------------------------------------------------- ratify

def line_body(line):
    return line.rstrip("\r\n")


def line_end(line):
    return line[len(line_body(line)):]


def unescape_cell(text):
    """The inverse of md_text for one cell: backslash escapes, then '&lt;', then '&amp;',
    undone in the reverse of the order md_text applied them."""
    text = re.sub(r"\\(.)", r"\1", text).strip()
    return text.replace("&lt;", "<").replace("&amp;", "&")


def verify_names_setting(cell, setting_id):
    """Does a rendered Verify cell, the code span '<setting_id> = <raw value>', name this
    setting? Reverses md_code's pipe escaping and padding, then checks the prefix."""
    m = re.match(r"^(`+)(.*)\1$", cell, re.S)
    if not m:
        return False
    inner = re.sub(r"(\\+)\|", lambda b: "\\" * ((len(b.group(1)) - 1) // 2) + "|",
                   m.group(2))
    if (len(inner) >= 2 and inner.startswith(" ") and inner.endswith(" ")
            and (inner[1] == "`" or inner[-2] == "`")):
        inner = inner[1:-1]
    return inner.startswith(setting_id + " = ")


def existing_deviations(block_lines):
    """{row id: {cell, object_id, verify}} for each row of an already rendered block whose
    Deviation cell holds something other than 'none'. That cell is the one piece of
    human-written content between the markers, so it is read back before re-rendering."""
    found, object_id = {}, None
    for line in block_lines:
        body = line_body(line)
        m = re.match(r"^Object ID (`+) ?([^`]+?) ?\1", body)
        if m:
            object_id = m.group(2).strip()
            continue
        if not body.lstrip().startswith("|"):
            continue
        cells = split_cells(body)
        if len(cells) != 8 or not ROW_ID_RE.match(unescape_cell(cells[0])):
            continue
        if unescape_cell(cells[6]).lower() in NO_DEVIATION:
            continue
        found[unescape_cell(cells[0])] = {"cell": cells[6], "object_id": object_id,
                                          "verify": cells[7]}
    return found


def carry_deviations(old_block, doc, platform, date):
    """(deviations to render, carried, dropped). A deviation is carried by row id only
    while that id still names the same object and setting. An id is permanent, so a
    mismatch means the id map was rebuilt, and pinning an exemption on whatever setting
    now holds the id would be worse than dropping it loudly."""
    rows_by_id = {r["id"]: r for r in doc["rows"] if r["platform"] == platform}
    deviations, carried, dropped = {}, [], []
    for rid, info in sorted(existing_deviations(old_block).items()):
        row = rows_by_id.get(rid)
        if row is None:
            dropped.append("%s Deviation %s: the row is not in dumps/%s/%s"
                           % (rid, info["cell"], date, ROWS))
        elif ((info["object_id"] or "").lower() != str(row["object_id"]).lower()
              or not verify_names_setting(info["verify"], row["setting_id"])):
            dropped.append("%s Deviation %s: the id now names %s in object %s, not the "
                           "setting the deviation was recorded against -- check id-map.json"
                           % (rid, info["cell"], row["setting_id"], row["object_id"]))
        else:
            deviations[rid] = info["cell"]
            carried.append("%s %s" % (rid, info["cell"]))
    return deviations, carried, dropped


def ratify_page(text, page_name, std_id, doc, platform, date, raw_sha, rows_sha,
                approver, approved_on_arg, today, re_ratify=False):
    """Return (new text, report). Raises CycleError, and so writes nothing, if the page is
    not shaped the way the contract says, or if re-running the same date would change
    an approval without --re-ratify."""
    lines = text.splitlines(keepends=True)
    newline = "\r\n" if lines and lines[0].endswith("\r\n") else "\n"

    if not lines or line_body(lines[0]).strip() != "---":
        raise CycleError("%s has no frontmatter block" % page_name)
    fm_end = next((i for i in range(1, len(lines)) if line_body(lines[i]).strip() == "---"),
                  None)
    if fm_end is None:
        raise CycleError("%s: frontmatter is not closed with ---" % page_name)

    starts = [i for i, line in enumerate(lines) if line.strip() == MARK_START]
    ends = [i for i, line in enumerate(lines) if line.strip() == MARK_END]
    if len(starts) != 1 or len(ends) != 1 or not fm_end < starts[0] < ends[0]:
        raise CycleError(
            "%s: needs exactly one %s line followed by exactly one %s line after the "
            "frontmatter (found %d start, %d end). Refusing: without the markers there is "
            "no boundary between generated and human-written content."
            % (page_name, MARK_START, MARK_END, len(starts), len(ends)))
    start, end = starts[0], ends[0]

    def outside(i):
        return fm_end < i < start or i > end

    # The approval header is the one table holding the Standard ID row. Searching only
    # that table means a later revision-history table with its own "| Version |" column
    # can never be mistaken for it.
    anchor = [i for i in range(len(lines))
              if outside(i) and re.match(r"^\|[ \t]*Standard ID[ \t]*\|", lines[i])]
    if len(anchor) != 1:
        raise CycleError("%s: needs exactly one '| Standard ID |' approval-header row "
                         "outside the markers, found %d" % (page_name, len(anchor)))
    top = bottom = anchor[0]
    while top - 1 > fm_end and lines[top - 1].lstrip().startswith("|"):
        top -= 1
    while bottom + 1 < len(lines) and lines[bottom + 1].lstrip().startswith("|"):
        bottom += 1
    table = [i for i in range(top, bottom + 1)]
    if not all(outside(i) for i in table):
        raise CycleError("%s: the approval header table overlaps the generated markers"
                         % page_name)

    cells = {}
    for label in HEADER_LABELS:
        loose = re.compile(r"^\|[ \t]*%s[ \t]*\|" % re.escape(label))
        hits = [i for i in table if loose.match(lines[i])]
        if len(hits) != 1:
            raise CycleError("%s: the approval header table needs exactly one '| %s |' "
                             "row, found %d" % (page_name, label, len(hits)))
        exact = re.match(r"^(\|[ \t]*%s[ \t]*\|)((?:[^|\\\r\n]|\\.)*)(\|[ \t]*)$"
                         % re.escape(label), line_body(lines[hits[0]]))
        if not exact:
            raise CycleError("%s: the '| %s |' approval row is not a two-column table row"
                             % (page_name, label))
        cells[label] = (hits[0], exact)

    current = {label: unescape_cell(m.group(2)) for label, (_i, m) in cells.items()}
    raw_cell = {label: m.group(2).strip() for label, (_i, m) in cells.items()}
    if current["Standard ID"] != std_id:
        raise CycleError("%s declares Standard ID %r, expected %r for platform %s"
                         % (page_name, current["Standard ID"], std_id, platform))

    # Render first: the block depends on neither the version nor the approval date, and
    # whether it would change decides whether a same-date run is a re-run or a new act.
    old_block = lines[start + 1:end]
    deviations, carried, dropped = carry_deviations(old_block, doc, platform, date)
    block_body = render_block(doc, platform, date, rows_sha, deviations)
    block_changed = [line_body(line) for line in old_block] != block_body

    previous = re.search(r"dumps/(\d{4}-\d{2}-\d{2})", current["Ratified from"])
    previous = previous.group(1) if previous else None
    same_date = previous == date
    version_m = re.match(r"^(\d+)\.(\d+)$", current["Version"])
    bumped = ("%d.%d" % (int(version_m.group(1)), int(version_m.group(2)) + 1)
              if version_m else "1.0")
    approver_cell = md_text(approver)
    ratified_from = "dumps/%s (sha256 %s)" % (date, raw_sha[:16])

    # The same folder again. That is a re-run only while nothing about the approval would
    # change. Anything else is a new approval, and must never land silently under the
    # version and date of the old one.
    reapproval = []
    if same_date:
        if block_changed:
            old_sha = re.search(r"/%s \(sha256 ([0-9a-f]{16})\)" % re.escape(ROWS),
                                "".join(old_block))
            if old_sha and old_sha.group(1) != rows_sha[:16]:
                reapproval.append("%s changed since it was ratified (sha256 %s -> %s)"
                                  % (ROWS, old_sha.group(1), rows_sha[:16]))
            else:
                reapproval.append(
                    "the generated block would change although %s is %s: a hand edit "
                    "between the markers, or a newer run_config_cycle.py rendering it "
                    "differently" % (ROWS, "unchanged" if old_sha else "not named in it"))
        if raw_cell["Approved by"] != approver_cell:
            reapproval.append("Approved by %r -> %r" % (current["Approved by"], approver))
        if approved_on_arg and approved_on_arg != current["Approved on"]:
            reapproval.append("Approved on %r -> %r" % (current["Approved on"],
                                                        approved_on_arg))
        if raw_cell["Ratified from"] != ratified_from:
            reapproval.append("Ratified from %r -> %r" % (current["Ratified from"],
                                                          ratified_from))
    if reapproval and not re_ratify:
        raise CycleError(
            "%s is already ratified from dumps/%s as version %s, approved by %s on %s, and "
            "this run would change that approval:\n%s\n"
            "       Re-ratifying the same folder with different content or a different "
            "approver is a new approval, and one version number must never stand for two. "
            "Review with --dry-run, then pass --re-ratify to record it as version %s "
            "approved on %s. Nothing was written."
            % (page_name, date, current["Version"] or "-", current["Approved by"] or "-",
               current["Approved on"] or "-",
               "\n".join("       - %s" % terminal_safe(r) for r in reapproval),
               bumped, approved_on_arg or today))

    if same_date and version_m and not reapproval:
        version = current["Version"]
    elif previous and version_m:
        version = bumped
    else:
        version = "1.0"
    if approved_on_arg:
        approved_on = effective = approved_on_arg
    elif same_date and not reapproval and valid_date(current["Approved on"]):
        # A same-date re-run with nothing changed keeps the original approval date, so
        # running it again next week changes nothing.
        approved_on = current["Approved on"]
        effective = (current["Effective from"] if valid_date(current["Effective from"])
                     else approved_on)
    else:
        approved_on = effective = today

    new_cells = {
        "Version": version,
        "Approved by": approver_cell,
        "Approved on": approved_on,
        "Effective from": effective,
        "Ratified from": ratified_from,
    }
    changed = []
    for label in WRITTEN_LABELS:
        i, m = cells[label]
        rebuilt = "%s %s %s" % (m.group(1), new_cells[label], m.group(3))
        if rebuilt != line_body(lines[i]):
            changed.append("%s: %r -> %r" % (label, current[label], new_cells[label]))
        lines[i] = rebuilt + line_end(lines[i])

    for key, value in (("status", "active"), ("last_reviewed", approved_on)):
        hits = [i for i in range(1, fm_end) if re.match(r"^%s:" % key, lines[i])]
        if len(hits) != 1:
            raise CycleError("%s: frontmatter needs exactly one top-level '%s:' key, found %d"
                             % (page_name, key, len(hits)))
        i = hits[0]
        rebuilt = "%s: %s" % (key, value)
        if rebuilt != line_body(lines[i]):
            changed.append("frontmatter %s -> %s" % (line_body(lines[i]), value))
        lines[i] = rebuilt + line_end(lines[i])

    block = [line + newline for line in block_body]
    new_lines = lines[:start + 1] + block + lines[end:]
    report = {
        "version": (current["Version"], version),
        "rows": sum(1 for r in doc["rows"] if r["platform"] == platform),
        "block": (len(old_block), len(block)),
        "block_changed": block_changed,
        "changes": changed,
        "reapproval": reapproval,
        "deviations": (carried, dropped),
    }
    return "".join(new_lines), report


def check_rows_for_ratify(doc, rows_path):
    for n, row in enumerate(doc["rows"]):
        if not isinstance(row, dict):
            raise CycleError("%s row %d is not an object" % (rows_path, n))
        missing = [f for f in ROW_FIELDS if f not in row or row[f] is None]
        if missing:
            raise CycleError("%s row %d (%s) lacks %s -- not a v2 row"
                             % (rows_path, n, row.get("row_key"), ", ".join(missing)))


def check_id_map(dumps, doc):
    path = dumps / ID_MAP
    if not path.is_file():
        raise CycleError("%s is missing. Ids are permanent and the map is their authority; "
                         "ratifying rows whose ids nothing reserves would let them be "
                         "reissued. Run generate first." % path)
    data = read_json(path, "id map")
    if not isinstance(data, dict) or data.get("schema") != 2 or not isinstance(
            data.get("ids"), dict):
        raise CycleError("%s is not a schema 2 id map. Delete it and run generate to "
                         "regenerate it." % path)
    ids = data["ids"]
    bad = [r["row_key"] for r in doc["rows"] if ids.get(r["row_key"]) != r["id"]]
    if bad:
        raise CycleError("%d row(s) carry an id that id-map.json does not, e.g. %s. The "
                         "rows were generated against a different map. Run generate "
                         "again." % (len(bad), bad[0]))


def ratify_provenance(folder, manifest, doc, args):
    """Refuse a folder whose provenance would make a weak standard, unless the flag that
    says the approver has seen it was given. Every refusal that applies is raised
    together, so one --dry-run shows the approver all of them. Returns (warnings, notes,
    accepted incidents, accepted raw labels or None) for the plan, which prints them in
    --dry-run and real runs alike."""
    date = folder.name
    warnings, notes, incidents, raw_labels, refusals = [], [], [], None, []
    if manifest is None:
        if not args.allow_missing_manifest:
            refusals.append(
                "%s has no %s. Nothing then records when this dump was collected, by whom, "
                "or that its raw files are what Graph returned, and ratifying it would make "
                "an undated, unattributed dump the normative baseline. Ratify a folder the "
                "exporter placed (it writes the manifest), or pass --allow-missing-manifest "
                "to ratify this one knowingly." % (date, MANIFEST))
        warnings.append("%s has no %s: this baseline is undated and unattributed "
                        "(--allow-missing-manifest)" % (date, MANIFEST))
    else:
        found, malformed = manifest_incidents(manifest)
        if malformed:
            # No override: a list nobody can read cannot be accepted either.
            refusals.append("%s/%s: %s. Refusing to ratify a dump whose completeness "
                            "cannot be read." % (date, MANIFEST, malformed))
        elif found is None:
            warnings.append("%s/%s records no incidents list (an exporter older than "
                            "incident recording), so the dump's completeness is not "
                            "recorded" % (date, MANIFEST))
        elif found:
            if not args.accept_incomplete_baseline:
                refusals.append(
                    "%s was placed INCOMPLETE: %s records %d incident(s):\n%s\n"
                    "       Missing data reads exactly like a removed setting or an "
                    "unassigned policy, so ratifying this dump would write the gaps into "
                    "the standard. Re-export, or pass --accept-incomplete-baseline to "
                    "ratify it with every incident listed beside the approver."
                    % (date, MANIFEST, len(found), indented_list(found)))
            incidents = found
        collector = manifest.get("collector")
        if not isinstance(collector, dict) or not collector.get("upn"):
            warnings.append("%s/%s names no collector upn: nobody is recorded as having "
                            "collected this dump" % (date, MANIFEST))
        tool = manifest.get("tool")
        if isinstance(tool, dict) and tool.get("git_dirty") is True:
            warnings.append("the exporter that collected %s had uncommitted changes "
                            "(tool.git_dirty true, git_commit %s): the code that ran is not "
                            "the code that commit holds"
                            % (date, terminal_safe(tool.get("git_commit") or "null")))

    labels = label_resolution(doc)
    mode = labels["mode"]
    if mode != "catalog":
        if not args.allow_raw_labels:
            if (folder / DEFINITIONS).is_file():
                how = "%s is in the folder: run generate %s first, " % (DEFINITIONS, date)
            else:
                how = ("The folder has no %s: ratify a fresh export (the exporter writes "
                       "it), " % DEFINITIONS)
            refusals.append(
                "%s/%s was generated with display resolution %s, so every Setting and "
                "Required value on the pages would be a raw Graph id rather than a human "
                "label. %sor pass --allow-raw-labels to ratify raw labels knowingly."
                % (date, ROWS, repr(mode) if mode else "not recorded", how))
        warnings.append("display resolution %s: Setting and Required value show raw Graph "
                        "ids (--allow-raw-labels)" % (repr(mode) if mode else "not recorded"))
    elif labels["count"] is None or labels["count"] > 0:
        # 'catalog' is not the same as 'every label resolved'. A definition the export
        # did not fetch leaves that row's Setting as a raw id, and nothing on the page
        # tells a reader which rows those are. An unknown count is refused the same way.
        if not args.allow_raw_labels:
            refusals.append(
                "%s/%s: %s:\n%s\n"
                "       Fetch the missing definitions with a fresh export and run generate, "
                "or pass --allow-raw-labels to ratify these rows with raw labels knowingly."
                % (date, ROWS, label_summary(labels), indented_list(label_listing(labels))))
        raw_labels = labels
    if refusals:
        if len(refusals) == 1:
            raise CycleError(refusals[0])
        raise CycleError("%d reasons to refuse, all shown so one --dry-run lists them:\n\n"
                         "       %s" % (len(refusals), "\n\n       ".join(
                             "%d. %s" % (n, r) for n, r in enumerate(refusals, 1))))
    return warnings, notes, incidents, raw_labels


def clean_approver(name):
    name = (name or "").strip()
    if not name or name in ("-", "—") or any(ord(c) < 32 for c in name):
        raise CycleError("--approved-by needs the approver's name on one line")
    return name


def cmd_ratify(paths, args):
    dumps = paths.require("dumps")
    standards = paths.require("standards")
    paths.describe({"dumps", "standards"})
    approver = clean_approver(args.approved_by)
    folder = existing_folder(dumps, args.date)
    raw, rows_path = folder / RAW_DUMP, folder / ROWS
    if not raw.is_file():
        raise CycleError("%s/%s is missing" % (args.date, RAW_DUMP))
    if not rows_path.is_file():
        raise CycleError("%s/%s is missing -- run: generate %s" % (args.date, ROWS, args.date))

    doc = load_rows(rows_path)
    if generator_major(doc) != GENERATOR_MAJOR:
        raise CycleError("%s was written by generator %s; ratify needs %d.x rows. Run: "
                         "generate %s" % (rows_path, doc["meta"].get("generator_version"),
                                          GENERATOR_MAJOR, args.date))
    raw_sha = sha256_file(raw)
    if doc["meta"].get("source_sha256") != raw_sha:
        raise CycleError(
            "hash mismatch: %s records source_sha256 %s..., but %s is %s...\n"
            "       The rows do not describe the dump beside them, so ratifying them would "
            "approve a configuration nobody collected. Restore the raw dump, or run: "
            "generate %s" % (ROWS, str(doc["meta"].get("source_sha256"))[:16], RAW_DUMP,
                             raw_sha[:16], args.date))
    manifest = require_manifest_intact(folder)
    definitions_sha = doc["meta"].get("definitions_sha256")
    if definitions_sha:
        if not (folder / DEFINITIONS).is_file():
            raise CycleError("the rows were resolved against %s, which is missing"
                             % DEFINITIONS)
        if sha256_file(folder / DEFINITIONS) != definitions_sha:
            raise CycleError("%s does not match meta.definitions_sha256 -- run: generate %s"
                             % (DEFINITIONS, args.date))
    check_rows_for_ratify(doc, rows_path)
    check_id_map(dumps, doc)
    warnings, notes, incidents, raw_labels = ratify_provenance(folder, manifest, doc, args)

    mapped = {platform for platform, _f, _s in PAGES}
    unmapped = sorted({r["platform"] for r in doc["rows"]} - mapped)
    if unmapped and not args.allow_unmapped_platforms:
        raise CycleError("rows exist for platform(s) %s, which no hardening-standard page "
                         "covers. They would be dropped from the ratified standard without "
                         "a trace. Add a page, or pass --allow-unmapped-platforms."
                         % ", ".join(unmapped))

    previous = read_ratified(dumps)
    if previous and previous > args.date and not args.allow_backdate:
        raise CycleError("RATIFIED is %s, which is later than %s. Ratifying an older dump "
                         "rolls the standard back. Pass --allow-backdate if that is the "
                         "intent." % (previous, args.date))

    rows_sha = sha256_file(rows_path)
    today = dt.datetime.now(APPROVAL_TZ).date().isoformat()
    plans = []
    for platform, file_name, std_id in PAGES:
        page = standards / file_name
        if not page.is_file():
            raise CycleError("standard page not found: %s" % page)
        try:
            original = page.read_bytes().decode("utf-8")
        except UnicodeDecodeError as exc:
            raise CycleError("%s is not UTF-8: %s" % (page, exc))
        new_text, report = ratify_page(original, file_name, std_id, doc, platform,
                                       args.date, raw_sha, rows_sha, approver,
                                       args.approved_on, today, args.re_ratify)
        plans.append((page, original, new_text, report))

    print("ratify          %s   (dump sha256 %s, rows sha256 %s)"
          % (args.date, raw_sha[:16], rows_sha[:16]))
    print("approved by     %s" % approver)
    if incidents:
        print("INCOMPLETE      %d incident(s), accepted by %s with "
              "--accept-incomplete-baseline:" % (len(incidents), approver))
        print(indented_list(incidents))
    if raw_labels is not None:
        print("RAW LABELS      %s. Accepted by %s with --allow-raw-labels:"
              % (label_summary(raw_labels), approver))
        print(indented_list(label_listing(raw_labels)))
    for warning in warnings:
        print("WARNING         %s" % warning)
    for note in notes:
        print("note            %s" % note)
    if unmapped:
        print("WARNING         platform(s) %s are not on any page" % ", ".join(unmapped))
    for page, original, new_text, report in plans:
        old_v, new_v = report["version"]
        print("page            %s   %s   version %s -> %s, %d rows, generated block %d -> %d "
              "lines%s" % (page.name, "unchanged" if new_text == original else "CHANGES",
                           old_v or "-", new_v, report["rows"], report["block"][0],
                           report["block"][1],
                           "" if report["block_changed"] else " (identical)"))
        for change in report["changes"]:
            print("                  %s" % change)
        if report["reapproval"]:
            print("                  re-ratified (--re-ratify) because: %s"
                  % terminal_safe("; ".join(report["reapproval"])))
        carried, dropped = report["deviations"]
        if carried:
            print("                  Deviation carried forward: %s"
                  % terminal_safe(", ".join(carried)))
        for item in dropped:
            print("WARNING         %s: %s. Not carried forward: update the exemption "
                  "register entry." % (page.name, terminal_safe(item)))
    if args.re_ratify and previous == args.date and not any(
            report["reapproval"] for _p, _o, _n, report in plans):
        print("note            nothing about the approval would change, so --re-ratify has "
              "no effect")
    print("RATIFIED        %s -> %s" % (previous or "(none)", args.date))
    if previous and previous != args.date and not (
            folder / ("diff-vs-%s.json" % previous)).is_file():
        # A later dump replaces the baseline only after every difference against the
        # current one has a disposition. No diff record means nobody has seen them.
        print("WARNING         %s holds no diff-vs-%s record. Run diff --current %s and "
              "give every difference a disposition before this replaces the baseline."
              % (args.date, previous, args.date))

    if args.dry_run:
        print("dry run         nothing written")
        return EXIT_OK
    for page, original, new_text, _report in plans:
        if new_text != original:
            atomic_write(page, new_text.encode("utf-8"))
    ratified_path = dumps / RATIFIED
    wanted = (args.date + "\n").encode("ascii")
    if not ratified_path.is_file() or ratified_path.read_bytes() != wanted:
        atomic_write(ratified_path, wanted)
    print("done            review the page changes with git diff; commit is yours")
    return EXIT_OK


# ------------------------------------------------------------------------------ pack

def cmd_pack(paths, args):
    dumps = paths.require("dumps")
    paths.describe({"dumps", "standards", "pack_builder"})
    folder = existing_folder(dumps, args.date)
    if args.no_baseline:
        baseline, why = None, "--no-baseline"
    elif args.baseline:
        baseline, why = args.baseline, "argv"
    else:
        ratified = read_ratified(dumps)
        if ratified and ratified != args.date:
            baseline, why = ratified, "RATIFIED"
        else:
            baseline, why = None, ("this folder is the RATIFIED one" if ratified
                                   else "nothing ratified yet")
    if baseline == args.date:
        raise CycleError("--baseline %s is the folder being packed" % baseline)
    print("baseline        %s   (%s)" % (baseline or "none", why))
    if why == "RATIFIED":
        require_pages_agree(paths, baseline, "The default baseline %s" % baseline)

    builder = paths.require("pack_builder")
    if not builder.is_file():
        raise CycleError("pack builder not found at %s" % builder)
    pack_args = ["--folder", folder]
    if baseline:
        pack_args += ["--baseline", existing_folder(dumps, baseline)]
    out = folder / PACK
    pack_args += ["--out", out]
    # The pack runs the differ itself. Hand it the one this run resolved, so an override
    # (argv or CONFIG_CYCLE_DIFFER) reaches the pack too, not only the diff subcommand.
    if supports(builder, "--differ"):
        pack_args += ["--differ", paths.require("differ")]
    # Likewise the standards folder: the pack shows the approval each page records. When
    # none resolves, the builder falls back to the parent of the dumps directory itself.
    if paths.standards is not None and supports(builder, "--standards-dir"):
        pack_args += ["--standards-dir", paths.standards]
    if args.allow_missing_manifest:
        if not supports(builder, "--allow-missing-manifest"):
            raise CycleError("%s has no --allow-missing-manifest flag" % builder.name)
        pack_args += ["--allow-missing-manifest"]
    code, _ = run_tool(builder, pack_args)
    if code != 0:
        raise CycleError("%s failed (exit %d)" % (builder.name, code))
    if not out.is_file():
        raise CycleError("%s exited 0 but wrote no %s" % (builder.name, out))
    print("wrote           %s   (sha256 %s)" % (out, sha256_file(out)[:16]))
    return EXIT_OK


# ------------------------------------------------------------------------------ main

def add_path_args(parser, suppress):
    """Path options on the main parser AND every subcommand, so they work either side of
    the subcommand. Subparsers default to SUPPRESS so they never overwrite a value given
    before the subcommand."""
    default = argparse.SUPPRESS if suppress else None
    group = parser.add_argument_group("paths (argv > env > default)")
    for flag, env, what in (
            ("--standards-repo", "STANDARDS_REPO", "security-documentation-restricted checkout"),
            ("--dumps-dir", "CONFIG_CYCLE_DUMPS_DIR", "configuration-hardening/dumps"),
            ("--standards-dir", "CONFIG_CYCLE_STANDARDS_DIR", "folder holding the "
                                                              "hardening-standard pages"),
            ("--generator", "CONFIG_CYCLE_GENERATOR", "generate_baseline.py"),
            ("--differ", "CONFIG_CYCLE_DIFFER", "diff_baseline.py"),
            ("--pack-builder", "CONFIG_CYCLE_PACK_BUILDER", "build_evidence_pack.py")):
        group.add_argument(flag, default=default, metavar="PATH",
                           help="%s (env %s)" % (what, env))


def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    add_path_args(common, suppress=True)
    parser = argparse.ArgumentParser(
        prog="run_config_cycle.py",
        description="Run the quarterly configuration-baseline cycle.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Exit codes: 0 ok / no differences, 1 differences (diff) or integrity "
               "problem (status), 2 error or refusal.")
    add_path_args(parser, suppress=False)
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    sub.add_parser("status", parents=[common],
                   help="every dated folder, which is ratified, and whether each raw file "
                        "still matches its manifest")

    gen = sub.add_parser("generate", parents=[common],
                         help="write baseline-rows.json and README.md for one folder")
    gen.add_argument("date", type=date_arg)

    diff = sub.add_parser("diff", parents=[common],
                          help="compare two cycles; defaults RATIFIED vs the newest folder")
    diff.add_argument("--baseline", type=date_arg, help="default: the RATIFIED folder")
    diff.add_argument("--current", type=date_arg, help="default: the newest dated folder")

    rat = sub.add_parser("ratify", parents=[common],
                         help="render a folder into the standard pages and mark it RATIFIED")
    rat.add_argument("date", type=date_arg)
    rat.add_argument("--approved-by", required=True, metavar="NAME")
    rat.add_argument("--approved-on", type=date_arg, metavar="DATE",
                     help="default: today in GMT+10, or the recorded date when re-running the "
                          "same folder with nothing changed")
    rat.add_argument("--re-ratify", action="store_true",
                     help="the folder is already ratified and its rows, approver or "
                          "approval date would change: record that as a new approval, a "
                          "minor version bump approved on today or --approved-on")
    rat.add_argument("--allow-missing-manifest", action="store_true",
                     help="ratify a folder with no collection-manifest.json: an undated, "
                          "unattributed dump")
    rat.add_argument("--accept-incomplete-baseline", action="store_true",
                     help="ratify a dump whose manifest records incidents; each is printed "
                          "beside the approver")
    rat.add_argument("--allow-raw-labels", action="store_true",
                     help="ratify rows generated without display resolution, so the pages "
                          "show raw Graph ids")
    rat.add_argument("--dry-run", action="store_true", help="report, write nothing")
    rat.add_argument("--allow-backdate", action="store_true",
                     help="permit ratifying a folder older than the current RATIFIED one")
    rat.add_argument("--allow-unmapped-platforms", action="store_true",
                     help="proceed when rows exist for a platform no page covers")

    pack = sub.add_parser("pack", parents=[common], help="build evidence-pack.html")
    pack.add_argument("date", type=date_arg)
    which = pack.add_mutually_exclusive_group()
    which.add_argument("--baseline", type=date_arg,
                       help="default: the RATIFIED folder, unless it is this one")
    which.add_argument("--no-baseline", action="store_true")
    pack.add_argument("--allow-missing-manifest", action="store_true",
                      help="passed to the pack builder: build for a folder with no "
                           "collection-manifest.json (provenance then reads NOT RECORDED)")
    return parser


COMMANDS = {"status": cmd_status, "generate": cmd_generate, "diff": cmd_diff,
            "ratify": cmd_ratify, "pack": cmd_pack}


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return COMMANDS[args.command](Paths(args), args)
    except CycleError as exc:
        sys.stdout.flush()
        sys.stderr.write("error: %s\n" % exc)
        return EXIT_ERROR


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(EXIT_ERROR)
