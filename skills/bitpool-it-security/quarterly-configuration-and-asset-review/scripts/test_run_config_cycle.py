#!/usr/bin/env python3
"""Tests for run_config_cycle.py, the quarterly cycle wrapper.

Every test runs against a TEMP copy of the dumps tree and temp copies of the three
hardening-standard pages. The real repo is read (the real 2026-09-27 dump, the real page
text) and never written.

Two layers:

    Stubbed   tiny stand-ins for the generator, differ and pack builder, so the wrapper's
              own behaviour is pinned down whatever state the real scripts are in. The
              stubs are written into the temp dir and selected through the wrapper's own
              env-var path resolution, which gets tested along the way.
    Real      the same flows against the real sibling scripts and a copy of the real
              2026-09-27 dump. Skipped, with the reason printed, when a real script is not
              v2-ready yet.

What each test guards, and why it would fail quietly otherwise:

    ratify touches only the generated block, five approval cells and two frontmatter keys.
        Anything else it rewrote would be a human-authored statement silently replaced.
    ratify is idempotent for the same date. If it were not, every re-run would show up
        as a new approval in git history.
    ratify refuses a hash mismatch or missing markers, and writes NOTHING, not even the
        pages that were fine. A half-ratified set is worse than none.
    status detects a tampered raw file. The dumps are evidence.
    generate is byte-identical on re-run. Otherwise git shows churn every cycle.
    diff defaults to RATIFIED against the newest folder. Diffing against the wrong folder
        still produces a clean-looking report.
    a same-date re-ratify that would change the rows or the approver is refused without
        --re-ratify, and with it bumps the version. Otherwise one version number carries
        two contents, or a new approver sits against the old approver's date.
    ratify refuses a folder with no manifest, a manifest that records incidents, or rows
        with no display resolution, unless the matching flag says so, and then warns.
    ratify refuses 'catalog' rows that record unresolved labels, or no usable count, unless
        --allow-raw-labels, and the refusal and --dry-run list every affected row by id.
        Otherwise raw Graph ids are ratified as if they were human-readable labels.
    every refusal that applies is reported at once, and a malformed incidents list has no
        override. Otherwise the approver clears one gate only to meet the next.
    an EXM- reference in a Deviation cell survives every re-render, and one that cannot
        be carried is warned about. Otherwise the next ratify erases an approved exemption.
    a crashing differ never lets an earlier run's diff record pass for this run's.
    status reports incidents and a RATIFIED that disagrees with a page's Ratified from,
        and notes a folder whose rows carry raw or unresolved labels.

Pure stdlib. Run through WSL:
    python3 -m unittest discover -s scripts -p 'test_run_config_cycle.py' -v
    python3 scripts/test_run_config_cycle.py
"""

import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
WRAPPER = HERE / "run_config_cycle.py"
sys.path.insert(0, str(HERE))
import run_config_cycle as rcc  # noqa: E402  (only its own helpers; it imports no sibling)

REAL_REPO = rcc.find_standards_repo()
REAL_HARDENING = REAL_REPO / "configuration-hardening" if REAL_REPO else None
REAL_DUMP = (REAL_HARDENING / "dumps" / "2026-09-27" / rcc.RAW_DUMP) if REAL_REPO else None
PAGE_FILES = [(platform, name, sid) for platform, name, sid in rcc.PAGES]

APPROVED_ON = "2026-09-30"  # a date no page copy already carries, so the rewrite is exercised

# ----------------------------------------------------------------------------- stubs

STUB_GENERATOR = r'''
import argparse, hashlib, json, os, sys
from pathlib import Path
ap = argparse.ArgumentParser()
for flag in ("--dump", "--out", "--id-map", "--generated-at"):
    ap.add_argument(flag, required=True)
ap.add_argument("--definitions")
if not os.environ.get("STUB_NO_README"):
    ap.add_argument("--readme")
a = ap.parse_args()
raw = Path(a.dump).read_bytes()
dump = json.loads(raw)
ORDER = ["windows10", "macOS", "iOS"]
PFX = {"windows10": "WIN", "macOS": "MAC", "iOS": "IOS"}
rows, excluded = [], []
for p in dump["configurationPolicies"]:
    if not p["isAssigned"]:
        excluded.append({"collection": "configurationPolicies", "object_id": p["id"],
                         "name": p["name"], "platform": p["platforms"], "reason": "unassigned"})
        continue
    base = {"platform": p["platforms"], "collection": "configurationPolicies",
            "object_type": "#microsoft.graph.deviceManagementConfigurationPolicy",
            "object_id": p["id"], "object_name": p["name"],
            "enforced_at": "Intune > configurationPolicies > " + p["name"]}
    rows.append(dict(base, setting_id="@displayName", setting_name="Policy name",
                     required_value=p["name"], display_value=p["name"], mode="identity",
                     verify="$.name"))
    for sid in sorted(p["settings"]):
        rows.append(dict(base, setting_id=sid,
                         setting_name=sid + os.environ.get("STUB_LABEL_SUFFIX", ""),
                         required_value=p["settings"][sid], display_value=p["settings"][sid],
                         mode="enforced", verify="$.settings"))
for r in rows:
    r["row_key"] = "configurationPolicies|%s|%s" % (r["object_id"].lower(), r["setting_id"].lower())
rows.sort(key=lambda r: (ORDER.index(r["platform"]), r["object_name"].casefold(),
                         r["object_id"], r["setting_id"] != "@displayName",
                         r["setting_id"].casefold()))
mp = Path(a.id_map)
m = json.loads(mp.read_text()) if mp.exists() else {"schema": 2, "ids": {}}
if m.get("schema") != 2:
    sys.exit("v1 id map refused: delete and regenerate")
for r in rows:
    if r["row_key"] not in m["ids"]:
        pfx = "BP-%s-" % PFX[r["platform"]]
        n = max([int(v[-4:]) for v in m["ids"].values() if v.startswith(pfx)] or [0]) + 1
        m["ids"][r["row_key"]] = pfx + "%04d" % n
    r["id"] = m["ids"][r["row_key"]]
mp.write_text(json.dumps(m, indent=2, sort_keys=True) + "\n")
defs = hashlib.sha256(Path(a.definitions).read_bytes()).hexdigest() if a.definitions else None
resolution = {"mode": "catalog" if a.definitions else "none", "resolved": 0, "unresolved": 0}
# STUB_MISSING_DEFINITIONS / STUB_MISSING_OPTIONS: comma-separated setting ids whose
# definition, or whose chosen option, the catalog lacked -- recorded the way the real
# generator records them. STUB_RESOLUTION replaces the whole object, for malformed meta.
miss_defs = [s for s in os.environ.get("STUB_MISSING_DEFINITIONS", "").split(",") if s]
miss_opts = [s for s in os.environ.get("STUB_MISSING_OPTIONS", "").split(",") if s]
if a.definitions and (miss_defs or miss_opts):
    settings = [r for r in rows if r["setting_id"] != "@displayName"]
    hit = [r for r in settings if r["setting_id"] in miss_defs + miss_opts]
    resolution.update(resolved=len(settings) - len(hit), unresolved=len(hit),
                      missing_definitions=sorted({r["setting_id"] for r in hit
                                                  if r["setting_id"] in miss_defs}),
                      missing_options=sorted({"%s = %s" % (r["setting_id"], r["required_value"])
                                              for r in hit if r["setting_id"] in miss_opts}),
                      unfetched_at_export=sorted(miss_defs))
if os.environ.get("STUB_RESOLUTION"):
    resolution = json.loads(os.environ["STUB_RESOLUTION"])
doc = {"meta": {"generator_version": "2.0", "generated_from": Path(a.dump).name,
                "generated_at": a.generated_at, "source_sha256": hashlib.sha256(raw).hexdigest(),
                "definitions_sha256": defs, "row_count": len(rows),
                "display_resolution": resolution,
                "scope": {"assigned_only": True, "excluded_objects": excluded,
                          "assignment_disagreements": []}},
       "rows": rows}
Path(a.out).write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
if getattr(a, "readme", None):
    Path(a.readme).write_text("---\ntype: Record\ndoc_type: record\n---\n\n# Cycle %s\n"
                              % a.generated_at, encoding="utf-8")
print("stub generator: %d rows, definitions=%s" % (len(rows), bool(a.definitions)))
'''

STUB_DIFFER = r'''
import argparse, json, os, sys
ap = argparse.ArgumentParser()
ap.add_argument("--baseline", required=True)
ap.add_argument("--current", required=True)
ap.add_argument("--format", default="text", choices=["text", "markdown", "json"])
ap.add_argument("-o", "--out")
a = ap.parse_args()
if os.path.realpath(a.baseline) == os.path.realpath(a.current):
    sys.exit(2)
b, c = (json.load(open(p, encoding="utf-8")) for p in (a.baseline, a.current))
if not all(str(d["meta"]["generator_version"]).startswith("2.") for d in (b, c)):
    sys.stderr.write("error: generator major versions differ\n")
    sys.exit(2)
B = {r["row_key"]: r for r in b["rows"]}
C = {r["row_key"]: r for r in c["rows"]}
both = sorted(set(B) & set(C))
renamed = [[B[k]["required_value"], C[k]["required_value"]] for k in both
           if k.endswith("|@displayname") and B[k]["required_value"] != C[k]["required_value"]]
changed = [k for k in both if not k.endswith("|@displayname")
           and B[k]["required_value"] != C[k]["required_value"]]
res = {"added": sorted(set(C) - set(B)), "removed": sorted(set(B) - set(C)),
       "changed": changed, "renamed": renamed}
n = sum(len(v) for v in res.values())
if a.format == "json":
    out = json.dumps(res, indent=2, sort_keys=True)
elif a.format == "markdown":
    out = "# Baseline diff\n\n" + "".join("- RENAMED %s -> %s\n" % tuple(x) for x in renamed)
    out += "\nTotal differences: %d" % n
else:
    out = "SUMMARY differences=%d added=%d removed=%d changed=%d renamed=%d" % (
        n, len(res["added"]), len(res["removed"]), len(changed), len(renamed))
print(out)
sys.exit(1 if n else 0)
'''

# A differ that dies with Python's default exit 1 -- the same code as "differences
# found". STUB_NO_RECORD_FLAGS hides --markdown-out/--json-out so the wrapper takes its
# once-per-format path; STUB_WRITE_THEN_CRASH writes both records before dying.
CRASH_DIFFER = r'''
import argparse, os, sys
from pathlib import Path
ap = argparse.ArgumentParser()
ap.add_argument("--baseline", required=True)
ap.add_argument("--current", required=True)
ap.add_argument("--format", default="text")
if not os.environ.get("STUB_NO_RECORD_FLAGS"):
    ap.add_argument("--markdown-out")
    ap.add_argument("--json-out")
a = ap.parse_args()
if os.environ.get("STUB_WRITE_THEN_CRASH"):
    Path(a.markdown_out).write_text("---\ntype: Record\n---\n\n# half a report\n")
    Path(a.json_out).write_text("{}\n")
raise RuntimeError("differ crashed before its own exit-2 handler")
'''

STUB_PACK = r'''
import argparse, json
from pathlib import Path
ap = argparse.ArgumentParser()
ap.add_argument("--folder", required=True)
ap.add_argument("--baseline")
ap.add_argument("--out", required=True)
ap.add_argument("--standards-dir")
a = ap.parse_args()
Path(a.out).write_text("<!doctype html><pre>%s</pre>\n" % json.dumps(
    {"folder": Path(a.folder).name, "baseline": Path(a.baseline).name if a.baseline else None,
     "standards": a.standards_dir}))
'''

# A stand-in page, used only when the real pages are not readable from here.
FALLBACK_PAGE = """---
type: Standard
title: Test endpoint hardening standard
last_reviewed: 2026-09-24
status: draft
doc_type: standard
sources:
  - internal
---

# Test endpoint hardening standard

## Approval

| Field | Value |
| --- | --- |
| Standard ID | {sid} |
| Version | 1.0 (pending) |
| Approved by | — |
| Approved on | — |
| Effective from | — |
| Ratified from | — |
| Next review | Quarterly |
| Supersedes | nothing |
| Authority | *Asset Management Policy* |

## Settings

<!-- GENERATED:START -->
*(populated at ratification)*
<!-- GENERATED:END -->
"""

HUMAN_TAIL = "\n## Change log\n\nHuman-written text after the END marker. Never touched.\n"


UNRATIFIED_REVIEWED = "2000-01-01"

# A sitecustomize that pins datetime.now for the wrapper subprocess: 2026-09-28T15:00Z, a
# moment when the UTC and GMT+10 calendar days differ.
PINNED_CLOCK = '''
import datetime as _dt

class _Pinned(_dt.datetime):
    @classmethod
    def now(cls, tz=None):
        moment = _dt.datetime(2026, 9, 28, 15, 0, tzinfo=_dt.timezone.utc)
        return moment.astimezone(tz) if tz else moment.replace(tzinfo=None)

_dt.datetime = _Pinned
'''


def unratify(text):
    """Return a copy of a page to its shape before any ratification: the five cells ratify
    writes back to '—', status draft, last_reviewed a sentinel no test approves on, the
    generated block emptied. The real pages carry an approval from the first cycle on
    (2026-09-28), and every test here must still start from an unapproved standard, or a
    first ratification is never exercised -- and no line ratify owns may already hold the
    value a test expects it to write. Line endings kept."""
    nl = "\r\n" if "\r\n" in text else "\n"
    for label in rcc.WRITTEN_LABELS:
        text = re.sub(r"(?m)^\|[ \t]*%s[ \t]*\|[^\r\n]*" % re.escape(label),
                      "| %s | — |" % label, text, count=1)
    text = re.sub(r"(?m)^status: active(?=[ \t]*\r?$)", "status: draft", text, count=1)
    text = re.sub(r"(?m)^last_reviewed:[^\r\n]*", "last_reviewed: %s" % UNRATIFIED_REVIEWED,
                  text, count=1)
    start, end = text.find(rcc.MARK_START), text.find(rcc.MARK_END)
    if 0 <= start < end:
        text = (text[:start + len(rcc.MARK_START)] + nl + "*(populated at ratification)*" + nl
                + text[end:])
    return text


def prepare_page(text):
    """Make a copy of a real page ratifiable: unratified, and with the markers and the
    Ratified from row even if the page owner has not yet added them."""
    text = unratify(text)
    if rcc.MARK_START not in text:
        idx = text.find("\n## Settings")
        head = text if idx == -1 else text[:idx]
        text = (head.rstrip("\n") + "\n\n## Settings\n\n" + rcc.MARK_START
                + "\n*(populated at ratification)*\n" + rcc.MARK_END + "\n")
    if "| Ratified from |" not in text:
        text = re.sub(r"(\| Effective from \|[^\n]*\n)", r"\1| Ratified from | — |\n", text,
                      count=1)
    if not text.rstrip("\n").endswith(rcc.MARK_END) or HUMAN_TAIL in text:
        return text
    # Give the "after the END marker" half of the byte-identity check something to hold.
    return text + HUMAN_TAIL


def page_source(name, sid):
    real = REAL_HARDENING / name if REAL_HARDENING else None
    if real and real.is_file():
        return prepare_page(real.read_bytes().decode("utf-8"))
    return prepare_page(FALLBACK_PAGE.format(sid=sid))


def stub_dump(renames=None, value="setting_two_1", hostile=False, drop=()):
    names = {"1": "Win Defender", "2": "Mac FileVault", "3": "iOS Restrictions",
             "4": "TROUBLESHOOTING Disable all firewalls"}
    names.update(renames or {})
    pols = [
        {"id": "AAAAAAAA-0000-0000-0000-000000000001", "name": names["1"],
         "platforms": "windows10", "isAssigned": True,
         "settings": {"device_vendor_msft_defender_allowrealtime":
                      "device_vendor_msft_defender_allowrealtime_1", "setting_two": value}},
        {"id": "AAAAAAAA-0000-0000-0000-000000000002", "name": names["2"],
         "platforms": "macOS", "isAssigned": True,
         "settings": {"com.apple.mcx.filevault2_enable": "com.apple.mcx.filevault2_enable_0"}},
        {"id": "AAAAAAAA-0000-0000-0000-000000000003", "name": names["3"],
         "platforms": "iOS", "isAssigned": True,
         "settings": {"com.apple.applicationaccess_allowcamera":
                      "com.apple.applicationaccess_allowcamera_true"}},
        {"id": "AAAAAAAA-0000-0000-0000-000000000004", "name": names["4"],
         "platforms": "windows10", "isAssigned": False, "settings": {"x": "y"}},
    ]
    for setting in drop:
        del pols[0]["settings"][setting]
    if hostile:
        for n, name in enumerate(HOSTILE_NAMES):
            pols.append({"id": "BBBBBBBB-0000-0000-0000-%012d" % n, "name": name,
                         "platforms": "windows10", "isAssigned": True,
                         "settings": {"hostile_value": HOSTILE_VALUES[n % len(HOSTILE_VALUES)]}})
    return {"configurationPolicies": pols, "deviceConfigurations": [],
            "deviceCompliancePolicies": []}


HOSTILE_NAMES = ["Evil | pipe", "<script>alert(1)</script>", rcc.MARK_END,
                 "back`tick``s", "line\nbreak", "_emph_ and *star*", "trailing ###"]
HOSTILE_VALUES = ["a|b`c<d>", "C:\\path\\|x", "<!-- x -->", "``", "\\",
                  "&lt;looks-like-an-entity&gt; & plain"]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def set_manifest_incidents(folder, value):
    """Rewrite a placed manifest's incidents. The manifest is never among the files it
    records, so this leaves every recorded hash intact."""
    path = folder / rcc.MANIFEST
    body = json.loads(path.read_text())
    body["incidents"] = value
    path.write_text(json.dumps(body, indent=2) + "\n")


# --------------------------------------------------------------------------- harness

class Tree:
    """A throwaway security-documentation-restricted with a dumps tree and page copies."""

    def __init__(self, test):
        self.root = Path(tempfile.mkdtemp(prefix="run-config-cycle-"))
        test.addCleanup(shutil.rmtree, str(self.root), True)
        self.repo = self.root / rcc.REPO_DIR_NAME
        self.hardening = self.repo / "configuration-hardening"
        self.dumps = self.hardening / "dumps"
        self.dumps.mkdir(parents=True)
        for _platform, name, sid in PAGE_FILES:
            (self.hardening / name).write_bytes(page_source(name, sid).encode("utf-8"))
        self.stubs = self.root / "stubs"
        self.stubs.mkdir()
        for name, body in (("gen.py", STUB_GENERATOR), ("diff.py", STUB_DIFFER),
                           ("pack.py", STUB_PACK), ("crash-diff.py", CRASH_DIFFER)):
            (self.stubs / name).write_text(body, encoding="utf-8")

    STUBS = {"generator": ("gen.py", "CONFIG_CYCLE_GENERATOR"),
             "differ": ("diff.py", "CONFIG_CYCLE_DIFFER"),
             "pack": ("pack.py", "CONFIG_CYCLE_PACK_BUILDER")}

    def env(self, stubs, extra=None):
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("CONFIG_CYCLE_", "STUB_")) and k != "STANDARDS_REPO"}
        env["STANDARDS_REPO"] = str(self.repo)
        env["PYTHONIOENCODING"] = "utf-8"
        for name in stubs:
            file_name, var = self.STUBS[name]
            env[var] = str(self.stubs / file_name)
        env.update(extra or {})
        return env

    def run(self, *args, real=False, stubs=None, extra=None):
        """real=True: every sibling is the real script. stubs=(...): only those are
        stubbed. Default: all three stubbed."""
        stubs = () if real else (tuple(self.STUBS) if stubs is None else stubs)
        proc = subprocess.run([sys.executable, str(WRAPPER)] + [str(a) for a in args],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              env=self.env(stubs, extra), cwd=str(self.root))
        return proc.returncode, proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8")

    def add_folder(self, date, dump=None, raw=None, manifest=True,
                   collected_at="default", definitions=True, incidents=(),
                   git_dirty=False, record_incidents=True):
        """A dated folder as the exporter places it. definitions writes a (minimal)
        setting-definitions.json, so the stub generator resolves labels; incidents and
        git_dirty go into the manifest; record_incidents=False writes a manifest from
        an exporter older than incident recording."""
        folder = self.dumps / date
        folder.mkdir()
        raw = raw if raw is not None else json.dumps(dump or stub_dump(), indent=2).encode()
        (folder / rcc.RAW_DUMP).write_bytes(raw)
        (folder / "intune-config-export-readable.json").write_bytes(raw)
        placed = [rcc.RAW_DUMP, "intune-config-export-readable.json"]
        if definitions:
            (folder / rcc.DEFINITIONS).write_text('{"_unresolved": []}\n')
            placed.append(rcc.DEFINITIONS)
        if manifest:
            if collected_at == "default":
                collected_at = "%sT03:14:15Z" % date
            files = {n: {"sha256": sha((folder / n).read_bytes()),
                         "bytes": (folder / n).stat().st_size} for n in placed}
            body = {"schema": 1, "collected_at_utc": collected_at, "collection_date": date,
                    "collector": {"upn": "collector@example.invalid",
                                  "object_id": "00000000-0000-0000-0000-000000000000",
                                  "source": "access-token claims"},
                    "tool": {"name": "export-intune-config.sh", "git_commit": None,
                             "git_dirty": git_dirty},
                    "files": files}
            if record_incidents:
                body["incidents"] = list(incidents)
            (folder / rcc.MANIFEST).write_text(json.dumps(body, indent=2) + "\n")
        return folder

    def page(self, name):
        return (self.hardening / name).read_bytes().decode("utf-8")

    def pages(self):
        return {name: (self.hardening / name).read_bytes() for _p, name, _s in PAGE_FILES}

    def ratified(self):
        path = self.dumps / rcc.RATIFIED
        return path.read_bytes() if path.exists() else None

    def rows(self, date):
        return json.loads((self.dumps / date / rcc.ROWS).read_text(encoding="utf-8"))


NETWORK_REF = re.compile(
    r"""\b(?:src|srcset|href|action|formaction|poster|data)\s*=\s*["']?\s*(?:https?:)?//"""
    r"""|url\(\s*["']?\s*(?:https?:)?//|@import|http-equiv\s*=\s*["']?refresh""", re.I)


def network_references(html):
    """Whatever would make a browser fetch something: an attribute or CSS url() pointing
    off the page, an @import, a meta refresh. A URL that is only DATA, such as a tenant
    setting whose value is a sign-in URL shown HTML-escaped in a <td>, fetches nothing.
    That is why this checks the property, not a literal grep for 'http'."""
    return NETWORK_REF.findall(html)


def split_page(text):
    lines = text.splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if line.strip() == rcc.MARK_START]
    ends = [i for i, line in enumerate(lines) if line.strip() == rcc.MARK_END]
    assert len(starts) == 1 and len(ends) == 1, (starts, ends)
    return lines[:starts[0] + 1], lines[starts[0] + 1:ends[0]], lines[ends[0]:]


ALLOWED_OUTSIDE = [re.compile(r"^status: "), re.compile(r"^last_reviewed: ")] + [
    re.compile(r"^\|\s*%s\s*\|" % re.escape(label)) for label in rcc.WRITTEN_LABELS]


def table_cells(line):
    """Cells of a GFM table row, split the STRICT way: a pipe is escaped only when an odd
    number of backslashes precede it. That is how micromark (GitBook) reads a row, and
    the looser cmark-gfm reading accepts everything this one does."""
    cells, cell, run = [], [], 0
    for ch in line.strip():
        if ch == "|" and run % 2 == 0:
            cells.append("".join(cell))
            cell = []
        else:
            cell.append(ch)
        run = run + 1 if ch == "\\" else 0
    cells.append("".join(cell))
    return cells[1:-1]


class CycleTestCase(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.tree = Tree(self)

    def ok(self, result, code=0):
        rc, out, err = result
        self.assertEqual(rc, code, "exit %d, wanted %d\nstdout:\n%s\nstderr:\n%s"
                         % (rc, code, out, err))
        return out, err

    def generate(self, date, **kw):
        return self.ok(self.tree.run("generate", date, **kw))

    def ratify(self, date, *extra, code=0, **kw):
        return self.ok(self.tree.run("ratify", date, "--approved-by", "Eric Sharp",
                                     "--approved-on", APPROVED_ON, *extra, **kw), code)

    def assert_outside_unchanged(self, before, after):
        """Everything outside the markers is byte-identical except the seven lines the
        contract lets ratify write. Returns the changed lines."""
        b_head, _b_block, b_tail = split_page(before)
        a_head, _a_block, a_tail = split_page(after)
        self.assertEqual(b_tail, a_tail, "text after the END marker changed")
        self.assertEqual(len(b_head), len(a_head), "line count before START changed")
        changed = [(x, y) for x, y in zip(b_head, a_head) if x != y]
        for old, new in changed:
            matching = [p for p in ALLOWED_OUTSIDE if p.match(new)]
            self.assertTrue(matching, "ratify rewrote a line it does not own: %r" % new)
            self.assertTrue(matching[0].match(old), "a line changed kind: %r -> %r"
                            % (old, new))
            self.assertEqual(old[len(old.rstrip("\r\n")):], new[len(new.rstrip("\r\n")):],
                             "line ending changed on %r" % new)
        kinds = [next(p.pattern for p in ALLOWED_OUTSIDE if p.match(new)) for _o, new in changed]
        self.assertEqual(len(kinds), len(set(kinds)), "one owned line changed twice")
        return changed


# -------------------------------------------------------------------- path resolution

class PathResolution(unittest.TestCase):
    """argv > env > default, as the user asked. Wrong precedence would make a test or a
    one-off override silently hit the real repo."""

    def setUp(self):
        saved = dict(os.environ)
        self.addCleanup(lambda: (os.environ.clear(), os.environ.update(saved)))
        for key in list(os.environ):
            if key.startswith("CONFIG_CYCLE_") or key == "STANDARDS_REPO":
                del os.environ[key]

    def paths(self, *argv):
        return rcc.Paths(rcc.build_parser().parse_args(list(argv) + ["status"]))

    def test_argv_beats_env_beats_default(self):
        os.environ["STANDARDS_REPO"] = "/tmp/from-env"
        p = self.paths()
        self.assertEqual((p.standards_repo, p.source["standards_repo"]),
                         (Path("/tmp/from-env"), "env STANDARDS_REPO"))
        self.assertEqual(p.dumps, Path("/tmp/from-env/configuration-hardening/dumps"))
        p = self.paths("--standards-repo", "/tmp/from-argv")
        self.assertEqual((p.standards_repo, p.source["standards_repo"]),
                         (Path("/tmp/from-argv"), "argv"))
        os.environ["CONFIG_CYCLE_DUMPS_DIR"] = "/tmp/dumps-env"
        self.assertEqual(self.paths("--standards-repo", "/tmp/r").dumps, Path("/tmp/dumps-env"))
        self.assertEqual(self.paths("--dumps-dir", "/tmp/dumps-argv").dumps,
                         Path("/tmp/dumps-argv"))

    def test_path_options_work_after_the_subcommand_too(self):
        args = rcc.build_parser().parse_args(["status", "--dumps-dir", "/tmp/after"])
        self.assertEqual(rcc.Paths(args).dumps, Path("/tmp/after"))
        # ...and a value given BEFORE the subcommand survives the subparser's defaults.
        args = rcc.build_parser().parse_args(["--dumps-dir", "/tmp/before", "status"])
        self.assertEqual(rcc.Paths(args).dumps, Path("/tmp/before"))

    def test_default_repo_is_the_sibling_checkout(self):
        # HERE is .../ai-skills/desktop/bitpool-it-security/skills/<skill>/scripts
        if len(HERE.parents) < 6 or HERE.parents[4].name != "ai-skills":
            self.skipTest("not running from the ai-skills checkout")
        expected = HERE.parents[5] / rcc.REPO_DIR_NAME
        if not expected.is_dir():
            self.skipTest("no security-documentation-restricted checkout beside it")
        p = self.paths()
        self.assertEqual((p.standards_repo, p.source["standards_repo"]), (expected, "default"))
        self.assertEqual(p.generator, HERE / "generate_baseline.py")

    @unittest.skipUnless(os.name == "posix", "WSL path translation only applies on posix")
    def test_windows_path_translated_for_wsl(self):
        self.assertEqual(rcc.local_path(r"C:\BitpoolDev\Github-Bitpool\x y"),
                         Path("/mnt/c/BitpoolDev/Github-Bitpool/x y"))


# ----------------------------------------------------------------------------- status

class Status(CycleTestCase):

    def test_clean_tree_reports_hashes_match(self):
        self.tree.add_folder("2026-09-25")
        self.generate("2026-09-25")
        out, _ = self.ok(self.tree.run("status"))
        self.assertIn("all recorded hashes match", out)
        self.assertRegex(out, r"2026-09-25\s+v2\.0 matches dump\s+ok \(3 files\)")

    def test_detects_tampered_raw_file(self):
        folder = self.tree.add_folder("2026-09-25")
        self.ok(self.tree.run("status"))
        raw = folder / rcc.RAW_DUMP
        raw.write_bytes(raw.read_bytes().replace(b"Win Defender", b"Win Defendr "))
        out, _ = self.ok(self.tree.run("status"), code=1)
        self.assertIn("PROBLEM         2026-09-25/intune-config-export.json: MISMATCH", out)
        self.assertIn("BAD (1 of 3)", out)

    def test_detects_missing_recorded_file(self):
        folder = self.tree.add_folder("2026-09-25")
        (folder / "intune-config-export-readable.json").unlink()
        out, _ = self.ok(self.tree.run("status"), code=1)
        self.assertIn("intune-config-export-readable.json: MISSING", out)

    def test_marks_ratified_and_flags_stale_ratified_rows(self):
        folder = self.tree.add_folder("2026-09-25", manifest=False)
        self.generate("2026-09-25")
        self.ratify("2026-09-25", "--allow-missing-manifest")
        out, _ = self.ok(self.tree.run("status"))
        self.assertRegex(out, r"2026-09-25\s+RATIFIED\s+v2\.0 matches dump")
        self.assertIn("has no collection-manifest.json", out)
        (folder / rcc.RAW_DUMP).write_bytes(b'{"configurationPolicies": []}')
        out, _ = self.ok(self.tree.run("status"), code=1)
        self.assertIn("(RATIFIED): rows record source_sha256", out)

    def test_ratified_naming_a_missing_folder_is_a_problem(self):
        (self.tree.dumps / rcc.RATIFIED).write_text("2026-01-01\n")
        out, _ = self.ok(self.tree.run("status"), code=1)
        self.assertIn("RATIFIED names 2026-01-01, but there is no such dated folder", out)

    def test_incomplete_dump_is_a_problem(self):
        # The incident text comes from Graph's error body, so it is untrusted: a terminal
        # escape in it must not reach the operator's terminal.
        incident = "deviceConfigurations: list TRUNCATED after 1 page(s) (HTTP 503): \x1b[31mx"
        self.tree.add_folder("2026-09-25", incidents=[incident])
        out, _ = self.ok(self.tree.run("status"), code=1)
        self.assertIn("PROBLEM         2026-09-25 was placed INCOMPLETE: "
                      "collection-manifest.json records 1 incident(s)", out)
        self.assertIn("- deviceConfigurations: list TRUNCATED after 1 page(s) (HTTP 503): "
                      "?[31mx", out)
        self.assertNotIn("\x1b", out)
        self.assertRegex(out, r"ok \(3 files\) INCOMPLETE")

    def test_every_incident_is_listed_and_a_malformed_list_is_a_problem(self):
        incidents = ["deviceConfigurations: list TRUNCATED after 1 page(s) (HTTP 503)",
                     "Settings Catalog policies: assignments UNAVAILABLE for 2 object(s)"]
        self.tree.add_folder("2026-09-25", incidents=incidents)
        folder = self.tree.add_folder("2026-12-20")
        set_manifest_incidents(folder, "none")
        out, _ = self.ok(self.tree.run("status"), code=1)
        self.assertIn("2026-09-25 was placed INCOMPLETE: collection-manifest.json records "
                      "2 incident(s)", out)
        for incident in incidents:
            self.assertIn("                  - " + incident, out)
        # A list nobody can read says nothing about completeness either way.
        self.assertIn("PROBLEM         2026-12-20/collection-manifest.json: 'incidents' is "
                      "not a list of strings, so completeness is unknown", out)

    def test_raw_and_unresolved_labels_are_noted(self):
        self.tree.add_folder("2026-09-25", definitions=False)
        self.generate("2026-09-25")
        self.tree.add_folder("2026-12-20")
        self.generate("2026-12-20", extra={"STUB_MISSING_DEFINITIONS": "setting_two"})
        self.tree.add_folder("2027-03-20")
        self.generate("2027-03-20")
        out, _ = self.ok(self.tree.run("status"))  # a note, not an integrity problem
        self.assertIn("note            2026-09-25/baseline-rows.json has display resolution "
                      "'none': every Setting and Required value is a raw Graph id, and ratify "
                      "2026-09-25 needs --allow-raw-labels", out)
        self.assertIn("note            2026-12-20/baseline-rows.json has 1 unresolved label(s) "
                      "in display resolution 'catalog', and ratify 2026-12-20 needs "
                      "--allow-raw-labels. ratify 2026-12-20 --dry-run lists every affected "
                      "row", out)
        self.assertNotIn("2027-03-20/baseline-rows.json has", out)

    def test_dirty_exporter_and_an_older_manifest_are_noted(self):
        self.tree.add_folder("2026-09-25", git_dirty=True)
        self.tree.add_folder("2026-12-20", record_incidents=False)
        out, _ = self.ok(self.tree.run("status"))
        self.assertIn("note            2026-09-25 was collected by an exporter with "
                      "uncommitted changes (tool.git_dirty true", out)
        self.assertIn("note            2026-12-20/collection-manifest.json records no "
                      "incidents list", out)

    def test_ratified_and_every_page_must_name_the_same_folder(self):
        # Policy 4 is unassigned, so its name lands in the Excluded table INSIDE the
        # markers. A row there reading '| Ratified from |' must never be taken for the
        # approval header.
        for date in ("2026-09-25", "2026-12-01"):
            self.tree.add_folder(date, dump=stub_dump(renames={"4": "Ratified from"}))
            self.generate(date)
        self.ratify("2026-09-25")
        self.assertIn("| Ratified from | `configurationPolicies` |",
                      self.tree.page("hardening-standard-windows-endpoints.md"))
        out, _ = self.ok(self.tree.run("status"))
        self.assertRegex(out, r"page\s+hardening-standard-windows-endpoints\.md\s+"
                              r"ratified from 2026-09-25")
        (self.tree.dumps / rcc.RATIFIED).write_text("2026-12-01\n")
        out, _ = self.ok(self.tree.run("status"), code=1)
        self.assertIn("PROBLEM         RATIFIED names 2026-12-01, but "
                      "hardening-standard-windows-endpoints.md is Ratified from "
                      "dumps/2026-09-25", out)
        # diff and pack refuse to default to a RATIFIED the pages contradict...
        _, err = self.ok(self.tree.run("diff", "--current", "2026-09-25"), code=2)
        self.assertIn("RATIFIED and the standard pages disagree", err)
        self.assertEqual(list((self.tree.dumps / "2026-09-25").glob("diff-vs-*")), [])
        _, err = self.ok(self.tree.run("pack", "2026-09-25"), code=2)
        self.assertIn("RATIFIED and the standard pages disagree", err)
        # ...but an explicit baseline is the operator's own choice.
        self.ok(self.tree.run("diff", "--baseline", "2026-09-25", "--current", "2026-12-01"))


# --------------------------------------------------------------------------- generate

class Generate(CycleTestCase):

    def snapshot(self, date):
        folder = self.tree.dumps / date
        return {n: (folder / n).read_bytes() for n in (rcc.ROWS, rcc.README)} | {
            rcc.ID_MAP: (self.tree.dumps / rcc.ID_MAP).read_bytes()}

    def test_rerun_is_byte_identical(self):
        self.tree.add_folder("2026-09-25")
        self.generate("2026-09-25")
        first = self.snapshot("2026-09-25")
        out, _ = self.generate("2026-09-25")
        self.assertEqual(first, self.snapshot("2026-09-25"))
        self.assertIn("(unchanged)", out)

    def test_generated_at_comes_from_manifest_then_midnight(self):
        self.tree.add_folder("2026-09-25", collected_at="2026-09-25T04:05:06Z")
        out, _ = self.generate("2026-09-25")
        self.assertIn("collected_at_utc", out)
        self.assertEqual(self.tree.rows("2026-09-25")["meta"]["generated_at"],
                         "2026-09-25T04:05:06Z")
        self.tree.add_folder("2026-12-20", manifest=False)
        self.generate("2026-12-20")
        self.assertEqual(self.tree.rows("2026-12-20")["meta"]["generated_at"],
                         "2026-12-20T00:00:00Z")

    def test_refuses_a_raw_file_that_no_longer_matches_its_manifest(self):
        folder = self.tree.add_folder("2026-09-25")
        (folder / rcc.RAW_DUMP).write_bytes((folder / rcc.RAW_DUMP).read_bytes() + b" ")
        _, err = self.ok(self.tree.run("generate", "2026-09-25"), code=2)
        self.assertIn("no longer matches the files it records", err)
        self.assertFalse((folder / rcc.ROWS).exists())

    def test_passes_definitions_only_when_present(self):
        folder = self.tree.add_folder("2026-09-25", definitions=False)
        out, _ = self.generate("2026-09-25")
        self.assertNotIn("--definitions", out)
        self.assertIn("definitions=False", out)
        (folder / rcc.DEFINITIONS).write_text('{"_unresolved": []}\n')
        out, _ = self.generate("2026-09-25")
        self.assertIn("--definitions", out)
        self.assertIn("definitions=True", out)

    def test_generator_without_readme_flag_warns_rather_than_crashes(self):
        self.tree.add_folder("2026-09-25")
        out, _ = self.generate("2026-09-25", extra={"STUB_NO_README": "1"})
        self.assertNotIn("--readme", out)
        self.assertIn("wrote no README.md", out)

    def test_generator_failure_is_exit_2(self):
        self.tree.add_folder("2026-09-25")
        (self.tree.dumps / rcc.ID_MAP).write_text('{"row": "BP-WIN-0001"}\n')  # v1 map
        _, err = self.ok(self.tree.run("generate", "2026-09-25"), code=2)
        self.assertIn("failed (exit 1)", err)


# ------------------------------------------------------------------------------- diff

class Diff(CycleTestCase):

    def cycle(self, date, **dump_kw):
        self.tree.add_folder(date, dump=stub_dump(**dump_kw))
        self.generate(date)

    def test_defaults_to_ratified_against_newest_folder(self):
        self.cycle("2026-06-24")
        self.ratify("2026-06-24")
        self.cycle("2026-09-25", value="setting_two_0")
        self.cycle("2026-12-20", renames={"2": "Mac FileVault (renamed)"})
        out, _ = self.ok(self.tree.run("diff"), code=1)
        self.assertIn("baseline        2026-06-24   (RATIFIED)", out)
        self.assertIn("current         2026-12-20   (newest folder)", out)
        self.assertIn("SUMMARY differences=1 added=0 removed=0 changed=0 renamed=1", out)
        md = (self.tree.dumps / "2026-12-20" / "diff-vs-2026-06-24.md").read_text()
        self.assertTrue(md.startswith("---\ntype: Record\ntitle: Baseline diff\n"), md[:200])
        self.assertIn("\ndoc_type: record\n", md)
        self.assertIn("RENAMED Mac FileVault -> Mac FileVault (renamed)", md)
        js = json.loads((self.tree.dumps / "2026-12-20" / "diff-vs-2026-06-24.json").read_text())
        self.assertEqual(js["renamed"], [["Mac FileVault", "Mac FileVault (renamed)"]])

    def test_no_change_is_exit_0_and_still_prints_counts(self):
        self.cycle("2026-06-24")
        self.ratify("2026-06-24")
        self.cycle("2026-09-25")
        out, _ = self.ok(self.tree.run("diff"), code=0)
        self.assertIn("SUMMARY differences=0", out)

    def test_explicit_baseline_and_current(self):
        for date in ("2026-06-24", "2026-09-25", "2026-12-20"):
            self.cycle(date, value="v-" + date)
        out, _ = self.ok(self.tree.run("diff", "--baseline", "2026-06-24",
                                       "--current", "2026-09-25"), code=1)
        self.assertIn("changed=1", out)
        self.assertTrue((self.tree.dumps / "2026-09-25" / "diff-vs-2026-06-24.md").is_file())

    def test_refuses_baseline_equal_to_current(self):
        self.cycle("2026-09-25")
        self.ratify("2026-09-25")
        _, err = self.ok(self.tree.run("diff"), code=2)
        self.assertIn("baseline and current are both 2026-09-25", err)

    def test_refuses_without_ratified_or_baseline(self):
        self.cycle("2026-09-25")
        _, err = self.ok(self.tree.run("diff"), code=2)
        self.assertIn("no RATIFIED file", err)

    def test_refuses_rows_that_do_not_describe_their_dump(self):
        self.cycle("2026-06-24")
        self.ratify("2026-06-24")
        self.cycle("2026-09-25")
        raw = self.tree.dumps / "2026-09-25" / rcc.RAW_DUMP
        raw.write_bytes(raw.read_bytes() + b"\n")
        _, err = self.ok(self.tree.run("diff"), code=2)
        self.assertIn("current folder 2026-09-25: rows record source_sha256", err)
        self.assertFalse((self.tree.dumps / "2026-09-25" / "diff-vs-2026-06-24.md").exists())

    def crash_setup(self):
        """A ratified cycle, a current one, and last quarter's diff records already in the
        current folder -- the files a crash must never let pass for this run's."""
        self.cycle("2026-06-24")
        self.ratify("2026-06-24")
        self.cycle("2026-09-25", value="setting_two_0")
        folder = self.tree.dumps / "2026-09-25"
        (folder / "diff-vs-2026-06-24.md").write_text("STALE REPORT FROM LAST QUARTER\n")
        (folder / "diff-vs-2026-06-24.json").write_text('{"stale": true}\n')
        return folder, {n: (folder / n).read_bytes()
                        for n in ("diff-vs-2026-06-24.md", "diff-vs-2026-06-24.json")}

    def crash_run(self, *flags):
        extra = {"CONFIG_CYCLE_DIFFER": str(self.tree.stubs / "crash-diff.py")}
        extra.update({flag: "1" for flag in flags})
        return self.ok(self.tree.run("diff", extra=extra), code=2)

    def assert_nothing_recorded(self, folder, stale, out, err):
        self.assertIn("RuntimeError: differ crashed before its own exit-2 handler", err)
        self.assertIn("crash-diff.py crashed (exit 1, traceback above)", err)
        self.assertIn("from an earlier run, NOT from this one", err)
        self.assertNotIn("wrote           ", out)
        # The stale report is byte-for-byte what it was: no fresh frontmatter, no new
        # last_reviewed, nothing that would make it read as this cycle's evidence.
        self.assertEqual(stale, {n: (folder / n).read_bytes() for n in stale})
        self.assertEqual([p.name for p in folder.iterdir() if rcc.PARTIAL in p.name], [])

    def test_crashing_differ_never_passes_off_an_earlier_record(self):
        folder, stale = self.crash_setup()
        out, err = self.crash_run()
        self.assertIn("--markdown-out", out)
        self.assert_nothing_recorded(folder, stale, out, err)

    def test_crash_after_the_records_were_written_still_records_nothing(self):
        folder, stale = self.crash_setup()
        out, err = self.crash_run("STUB_WRITE_THEN_CRASH")
        self.assert_nothing_recorded(folder, stale, out, err)

    def test_crash_of_an_older_differ_records_nothing(self):
        folder, stale = self.crash_setup()
        out, err = self.crash_run("STUB_NO_RECORD_FLAGS")
        self.assertNotIn("--markdown-out", out)
        self.assert_nothing_recorded(folder, stale, out, err)


# ----------------------------------------------------------------------------- ratify

class Ratify(CycleTestCase):

    def setUp(self):
        super().setUp()
        self.tree.add_folder("2026-09-25")
        self.generate("2026-09-25")

    def test_injects_between_markers_and_nothing_else(self):
        before = {name: self.tree.page(name) for _p, name, _s in PAGE_FILES}
        out, _ = self.ratify("2026-09-25")
        self.assertIn("done", out)
        doc = self.tree.rows("2026-09-25")
        raw_sha = doc["meta"]["source_sha256"]
        for platform, name, _sid in PAGE_FILES:
            after = self.tree.page(name)
            changed = self.assert_outside_unchanged(before[name], after)
            new_lines = {n.rstrip("\n") for _o, n in changed}
            # APPROVED_ON is a date no page copy starts with, so all seven owned lines
            # must actually have been rewritten -- not merely left matching.
            self.assertEqual(len(changed), 7, sorted(new_lines))
            frontmatter = after.split("\n---\n", 1)[0].splitlines()
            self.assertIn("status: active", frontmatter)
            self.assertIn("last_reviewed: %s" % APPROVED_ON, frontmatter)
            self.assertIn("| Version | 1.0 |", new_lines)
            self.assertIn("| Approved by | Eric Sharp |", new_lines)
            self.assertIn("| Approved on | %s |" % APPROVED_ON, new_lines)
            self.assertIn("| Effective from | %s |" % APPROVED_ON, new_lines)
            self.assertIn("| Ratified from | dumps/2026-09-25 (sha256 %s) |" % raw_sha[:16],
                          new_lines)
            block = "".join(split_page(after)[1])
            rows = [r for r in doc["rows"] if r["platform"] == platform]
            self.assertEqual(block.count("\n| BP-"), len(rows), name)
            for row in rows:
                self.assertIn("| %s |" % row["id"], block)
            self.assertIn("bitpool:ratified 2026-09-25", block)
        self.assertEqual(self.tree.ratified(), b"2026-09-25\n")

    def test_name_row_is_first_with_mode_identity(self):
        self.ratify("2026-09-25")
        block = split_page(self.tree.page("hardening-standard-windows-endpoints.md"))[1]
        idx = next(i for i, line in enumerate(block) if line.startswith("### Win Defender"))
        first_row = next(line for line in block[idx:] if line.startswith("| BP-"))
        cells = [c.strip() for c in table_cells(first_row)]
        self.assertEqual(cells[1:3], ["Policy name", "Win Defender"])
        self.assertEqual(cells[4], "identity")
        self.assertEqual(cells[7], "`@displayName = Win Defender`")
        self.assertIn("AAAAAAAA-0000-0000-0000-000000000001", "".join(block[idx:idx + 3]))
        excluded = "".join(block)
        self.assertIn("| TROUBLESHOOTING Disable all firewalls | `configurationPolicies` | "
                      "`AAAAAAAA-0000-0000-0000-000000000004` | unassigned |", excluded)

    def test_default_approval_date_is_the_gmt_plus_10_day(self):
        """User decision, 2026-09-28: with no --approved-on, an approval is dated by
        Bitpool's calendar day in GMT+10, not by UTC. The wrapper's clock is pinned to
        2026-09-28T15:00Z, which is already 2026-09-29 in GMT+10, so a UTC default cannot
        pass whatever time of day the suite runs."""
        self.assertEqual(rcc.APPROVAL_TZ.utcoffset(None), dt.timedelta(hours=10))
        pin = self.tree.root / "pinned-clock"
        pin.mkdir()
        (pin / "sitecustomize.py").write_text(PINNED_CLOCK, encoding="utf-8")
        self.ok(self.tree.run("ratify", "2026-09-25", "--approved-by", "Eric Sharp",
                              extra={"PYTHONPATH": str(pin)}))
        for _p, name, _sid in PAGE_FILES:
            page = self.tree.page(name)
            self.assertIn("| Approved on | 2026-09-29 |", page, name)
            self.assertIn("| Effective from | 2026-09-29 |", page)
            self.assertIn("last_reviewed: 2026-09-29", page)
            self.assertNotIn("last_reviewed: %s" % UNRATIFIED_REVIEWED, page)

    def test_idempotent_for_the_same_date(self):
        # No --approved-on: the recorded approval date must be kept, not replaced by today.
        run = lambda: self.ok(self.tree.run("ratify", "2026-09-25", "--approved-by",
                                            "Eric Sharp"))
        run()
        first_pages, first_ratified = self.tree.pages(), self.tree.ratified()
        out, _ = run()
        self.assertEqual(first_pages, self.tree.pages())
        self.assertEqual(first_ratified, self.tree.ratified())
        self.assertEqual(out.count("unchanged"), 3, out)

    def test_refuses_hash_mismatch_and_writes_nothing(self):
        before = self.tree.pages()
        raw = self.tree.dumps / "2026-09-25" / rcc.RAW_DUMP
        raw.write_bytes(raw.read_bytes().replace(b"Win Defender", b"Win Defendxr"))
        _, err = self.ratify("2026-09-25", code=2)
        self.assertIn("hash mismatch", err)
        self.assertEqual(before, self.tree.pages())
        self.assertIsNone(self.tree.ratified())

    def test_refuses_missing_markers_and_writes_no_page(self):
        before = self.tree.pages()
        mac = self.tree.hardening / "hardening-standard-macos-endpoints.md"
        mac.write_bytes(mac.read_bytes().replace(rcc.MARK_END.encode(), b""))
        before[mac.name] = mac.read_bytes()
        _, err = self.ratify("2026-09-25", code=2)
        self.assertIn("hardening-standard-macos-endpoints.md: needs exactly one", err)
        # Windows is validated first and was fine -- it must still be untouched.
        self.assertEqual(before, self.tree.pages())
        self.assertIsNone(self.tree.ratified())

    def test_refuses_missing_approval_row(self):
        ios = self.tree.hardening / "hardening-standard-ios-endpoints.md"
        ios.write_bytes(re.sub(rb"\| Ratified from \|[^\n]*\n", b"", ios.read_bytes()))
        _, err = self.ratify("2026-09-25", code=2)
        self.assertIn("'| Ratified from |' row, found 0", err)

    def test_refuses_page_for_the_wrong_platform(self):
        win = self.tree.hardening / "hardening-standard-windows-endpoints.md"
        win.write_bytes(win.read_bytes().replace(b"| Standard ID | BP-WIN |",
                                                 b"| Standard ID | BP-MAC |"))
        _, err = self.ratify("2026-09-25", code=2)
        self.assertIn("declares Standard ID 'BP-MAC', expected 'BP-WIN'", err)

    def test_refuses_rows_whose_ids_the_map_does_not_hold(self):
        id_map = self.tree.dumps / rcc.ID_MAP
        data = json.loads(id_map.read_text())
        key = sorted(data["ids"])[0]
        data["ids"][key] = "BP-WIN-9999"
        id_map.write_text(json.dumps(data))
        _, err = self.ratify("2026-09-25", code=2)
        self.assertIn("carry an id that id-map.json does not", err)

    def test_version_bumps_on_a_later_date_and_holds_on_rerun(self):
        self.ratify("2026-09-25")
        self.tree.add_folder("2026-12-20", dump=stub_dump(value="later"))
        self.generate("2026-12-20")
        self.ratify("2026-12-20")
        page = self.tree.page("hardening-standard-windows-endpoints.md")
        self.assertIn("| Version | 1.1 |", page)
        self.assertIn("| Ratified from | dumps/2026-12-20 (sha256 ", page)
        self.assertIn("bitpool:ratified 2026-12-20", page)
        self.ratify("2026-12-20")
        self.assertIn("| Version | 1.1 |", self.tree.page("hardening-standard-windows-endpoints.md"))
        self.assertEqual(self.tree.ratified(), b"2026-12-20\n")

    def test_refuses_to_backdate_without_the_flag(self):
        self.tree.add_folder("2026-06-24")
        self.generate("2026-06-24")
        self.ratify("2026-09-25")
        _, err = self.ratify("2026-06-24", code=2)
        self.assertIn("rolls the standard back", err)
        self.ratify("2026-06-24", "--allow-backdate")
        self.assertEqual(self.tree.ratified(), b"2026-06-24\n")

    def test_dry_run_writes_nothing(self):
        before = self.tree.pages()
        out, _ = self.ratify("2026-09-25", "--dry-run")
        self.assertIn("dry run         nothing written", out)
        self.assertRegex(out, r"Version: '[^']*' -> '1\.0'")
        self.assertIn("Approved by: '—' -> 'Eric Sharp'", out)
        self.assertEqual(before, self.tree.pages())
        self.assertIsNone(self.tree.ratified())

    def test_untrusted_names_and_values_cannot_break_the_page(self):
        self.tree.add_folder("2026-12-20", dump=stub_dump(hostile=True))
        self.generate("2026-12-20")
        self.ratify("2026-12-20")
        page = self.tree.page("hardening-standard-windows-endpoints.md")
        head, block, tail = split_page(page)  # asserts exactly one marker pair
        self.assertEqual(sum(1 for line in page.splitlines() if line.strip() == rcc.MARK_END), 1)
        rows = [line for line in block if line.startswith("| BP-")]
        self.assertEqual(len(rows), len([r for r in self.tree.rows("2026-12-20")["rows"]
                                         if r["platform"] == "windows10"]))
        for line in rows:
            cells = table_cells(line)
            self.assertEqual(len(cells), 8, line)
            for cell in cells[:7]:
                self.assertNotIn("<", cell.replace("<br>", ""), line)
            self.assertRegex(cells[7].strip(), r"^(`+).*\1$", line)
        headings = [line for line in block if line.startswith("### ")]
        for heading in headings:
            self.assertNotIn("<", heading.replace("<br>", ""))
        self.assertIn("### &lt;script>alert(1)&lt;/script>\n", headings)
        self.assertIn("### trailing \\#\\#\\#\n", headings)
        self.assertIn("### line<br>break\n", headings)
        self.assertIn("| Evil \\| pipe |", "".join(block))
        # An entity-shaped value must render as typed, not as '<' and '>'. A bare '&'
        # and a '>' mid-cell are literal already, so they stay readable in the source.
        self.assertIn("| &amp;lt;looks-like-an-entity&amp;gt; & plain |", "".join(block))
        self.assertIn("| Intune > configurationPolicies > Win Defender |", "".join(block))

    # -- the same date again: a re-run, or a new approval ---------------------------

    def run_ratify(self, date, approver, approved_on, *extra, code=0):
        return self.ok(self.tree.run("ratify", date, "--approved-by", approver,
                                     "--approved-on", approved_on, *extra), code)

    def win_page(self):
        return self.tree.page("hardening-standard-windows-endpoints.md")

    def test_same_date_with_changed_rows_is_refused_without_re_ratify(self):
        self.ratify("2026-09-25")
        # The rows change under the ratified folder, as when setting-definitions.json is
        # added and generate re-run. Here every setting is relabelled.
        out, _ = self.generate("2026-09-25", extra={"STUB_LABEL_SUFFIX": " (relabelled)"})
        self.assertIn("ratify 2026-09-25 --re-ratify --dry-run", out)
        pages, ratified = self.tree.pages(), self.tree.ratified()
        _, err = self.ratify("2026-09-25", code=2)
        self.assertIn("is already ratified from dumps/2026-09-25 as version 1.0", err)
        self.assertIn("baseline-rows.json changed since it was ratified", err)
        self.assertIn("pass --re-ratify to record it as version 1.1", err)
        self.assertEqual(pages, self.tree.pages())
        self.assertEqual(ratified, self.tree.ratified())
        out, _ = self.run_ratify("2026-09-25", "Eric Sharp", "2026-10-01", "--re-ratify")
        self.assertIn("re-ratified (--re-ratify) because", out)
        page = self.win_page()
        for cell in ("| Version | 1.1 |", "| Approved on | 2026-10-01 |",
                     "| Effective from | 2026-10-01 |", "(relabelled)"):
            self.assertIn(cell, page)
        # The same again, nothing changed: a true re-run, so nothing moves.
        pages = self.tree.pages()
        out, _ = self.run_ratify("2026-09-25", "Eric Sharp", "2026-10-01", "--re-ratify")
        self.assertIn("--re-ratify has no effect", out)
        self.assertEqual(pages, self.tree.pages())

    def test_same_date_with_another_approver_or_date_is_refused(self):
        self.ratify("2026-09-25")
        pages = self.tree.pages()
        _, err = self.run_ratify("2026-09-25", "Someone Else", APPROVED_ON, code=2)
        self.assertIn("Approved by 'Eric Sharp' -> 'Someone Else'", err)
        _, err = self.run_ratify("2026-09-25", "Eric Sharp", "2026-10-02", code=2)
        self.assertIn("Approved on '%s' -> '2026-10-02'" % APPROVED_ON, err)
        self.assertEqual(pages, self.tree.pages())
        self.run_ratify("2026-09-25", "Someone Else", "2026-10-02", "--re-ratify")
        page = self.win_page()
        for cell in ("| Version | 1.1 |", "| Approved by | Someone Else |",
                     "| Approved on | 2026-10-02 |"):
            self.assertIn(cell, page)

    # -- provenance a standard must not be built on without saying so ---------------

    def test_refuses_a_folder_with_no_manifest_unless_allowed(self):
        self.tree.add_folder("2026-12-20", manifest=False)
        self.generate("2026-12-20")
        _, err = self.ratify("2026-12-20", code=2)
        self.assertIn("2026-12-20 has no collection-manifest.json", err)
        self.assertIn("--allow-missing-manifest", err)
        self.assertIsNone(self.tree.ratified())
        out, _ = self.ratify("2026-12-20", "--allow-missing-manifest", "--dry-run")
        self.assertIn("WARNING         2026-12-20 has no collection-manifest.json: this "
                      "baseline is undated and unattributed", out)

    def test_refuses_raw_labels_unless_allowed(self):
        self.tree.add_folder("2026-12-20", definitions=False)
        self.generate("2026-12-20")
        _, err = self.ratify("2026-12-20", code=2)
        self.assertIn("generated with display resolution 'none'", err)
        self.assertIn("The folder has no setting-definitions.json", err)
        out, _ = self.ratify("2026-12-20", "--allow-raw-labels", "--dry-run")
        self.assertIn("WARNING         display resolution 'none'", out)
        # Definitions that arrived after generate: the refusal says to regenerate.
        (self.tree.dumps / "2026-12-20" / rcc.DEFINITIONS).write_text('{"_unresolved": []}\n')
        _, err = self.ratify("2026-12-20", code=2)
        self.assertIn("run generate 2026-12-20 first", err)

    def test_refuses_an_incomplete_dump_unless_accepted(self):
        incident = "Settings Catalog policies: assignments UNAVAILABLE for 2 object(s)"
        self.tree.add_folder("2026-12-20", incidents=[incident])
        self.generate("2026-12-20")
        _, err = self.ratify("2026-12-20", code=2)
        self.assertIn("2026-12-20 was placed INCOMPLETE: collection-manifest.json records "
                      "1 incident(s)", err)
        self.assertIn("- " + incident, err)
        self.assertIsNone(self.tree.ratified())
        out, _ = self.ratify("2026-12-20", "--accept-incomplete-baseline", "--dry-run")
        lines = out.splitlines()
        i = lines.index("approved by     Eric Sharp")
        self.assertEqual(lines[i + 1], "INCOMPLETE      1 incident(s), accepted by Eric Sharp "
                                       "with --accept-incomplete-baseline:")
        self.assertEqual(lines[i + 2].strip(), "- " + incident)

    def test_accepted_incomplete_dump_is_written_with_every_incident_listed(self):
        incidents = ["deviceConfigurations: list TRUNCATED after 1 page(s) (HTTP 503)",
                     "Settings Catalog policies: assignments UNAVAILABLE for 2 object(s)"]
        self.tree.add_folder("2026-12-20", incidents=incidents)
        self.generate("2026-12-20")
        pages = self.tree.pages()
        _, err = self.ratify("2026-12-20", code=2)  # a real run, not only --dry-run
        self.assertIn("records 2 incident(s)", err)
        self.assertEqual(pages, self.tree.pages())
        self.assertIsNone(self.tree.ratified())
        out, _ = self.ratify("2026-12-20", "--accept-incomplete-baseline")
        self.assertIn("INCOMPLETE      2 incident(s), accepted by Eric Sharp with "
                      "--accept-incomplete-baseline:", out)
        for incident in incidents:
            self.assertIn("                  - " + incident, out)
        self.assertNotEqual(pages, self.tree.pages())
        self.assertEqual(self.tree.ratified(), b"2026-12-20\n")

    def test_malformed_incidents_list_is_refused_even_with_the_override(self):
        folder = self.tree.add_folder("2026-12-20")
        set_manifest_incidents(folder, {"deviceConfigurations": "TRUNCATED"})
        self.generate("2026-12-20")
        _, err = self.ratify("2026-12-20", "--accept-incomplete-baseline", "--dry-run",
                             code=2)
        self.assertIn("'incidents' is not a list of strings", err)
        self.assertIn("Refusing to ratify a dump whose completeness cannot be read", err)

    # -- 'catalog' is not 'every label resolved' ------------------------------------

    UNRESOLVED = {"STUB_MISSING_DEFINITIONS": "device_vendor_msft_defender_allowrealtime",
                  "STUB_MISSING_OPTIONS": "com.apple.mcx.filevault2_enable"}

    def unresolved_folder(self, date="2026-12-20", env=None, **folder_kw):
        self.tree.add_folder(date, **folder_kw)
        self.generate(date, extra=env or self.UNRESOLVED)
        ids = {r["setting_id"]: r["id"] for r in self.tree.rows(date)["rows"]}
        self.assertEqual(self.tree.rows(date)["meta"]["display_resolution"]["mode"],
                         "catalog")
        return ids

    def assert_lists_unresolved(self, text, ids):
        self.assertIn("2 unresolved row(s) in display resolution 'catalog' (2 resolved)", text)
        self.assertIn("                  - %s  device_vendor_msft_defender_allowrealtime  "
                      "(no setting definition)"
                      % ids["device_vendor_msft_defender_allowrealtime"], text)
        self.assertIn("                  - %s  com.apple.mcx.filevault2_enable = "
                      "com.apple.mcx.filevault2_enable_0  (no option label for "
                      "com.apple.mcx.filevault2_enable_0)"
                      % ids["com.apple.mcx.filevault2_enable"], text)
        self.assertIn("                  - the exporter recorded 1 setting definition(s) it "
                      "could not fetch: device_vendor_msft_defender_allowrealtime", text)
        # The rows that did resolve are not listed as raw.
        self.assertNotIn(ids["setting_two"], text)

    def test_unresolved_catalog_labels_are_refused_unless_allowed(self):
        ids = self.unresolved_folder()
        pages = self.tree.pages()
        # Before the fix a 'catalog' folder ratified on a note, whatever it left raw.
        _, err = self.ratify("2026-12-20", code=2)
        self.assert_lists_unresolved(err, ids)
        self.assertIn("or pass --allow-raw-labels to ratify these rows with raw labels "
                      "knowingly", err)
        self.assertEqual(pages, self.tree.pages())
        self.assertIsNone(self.tree.ratified())
        # --dry-run is not a way round it, and it shows the same list.
        _, err = self.ratify("2026-12-20", "--dry-run", code=2)
        self.assert_lists_unresolved(err, ids)
        # With the flag, the dry run lists every raw row beside the approver...
        out, _ = self.ratify("2026-12-20", "--allow-raw-labels", "--dry-run")
        self.assertIn("RAW LABELS      2 unresolved row(s)", out)
        self.assertIn("Accepted by Eric Sharp with --allow-raw-labels:", out)
        self.assert_lists_unresolved(out, ids)
        self.assertIn("dry run         nothing written", out)
        self.assertEqual(pages, self.tree.pages())
        # ...and so does the real run, which then writes.
        out, _ = self.ratify("2026-12-20", "--allow-raw-labels")
        self.assert_lists_unresolved(out, ids)
        self.assertNotEqual(pages, self.tree.pages())
        self.assertEqual(self.tree.ratified(), b"2026-12-20\n")

    def test_an_unknown_or_untied_unresolved_count_is_refused_and_still_shown(self):
        env = {"STUB_RESOLUTION": json.dumps({"mode": "catalog", "resolved": 4})}
        self.unresolved_folder(env=env)
        _, err = self.ratify("2026-12-20", "--dry-run", code=2)
        self.assertIn("an unknown number of unresolved row(s) in display resolution "
                      "'catalog' (4 resolved)", err)
        # A count the recorded misses only partly explain: every part is still shown.
        env = {"STUB_RESOLUTION": json.dumps({
            "mode": "catalog", "resolved": 1, "unresolved": 3,
            "missing_definitions": ["setting_two", "not_in_any_row"]})}
        ids = self.unresolved_folder("2027-03-20", env=env)
        _, err = self.ratify("2027-03-20", "--dry-run", code=2)
        out, _ = self.ratify("2027-03-20", "--allow-raw-labels", "--dry-run")
        for text in (err, out):
            self.assertIn("3 unresolved row(s) in display resolution 'catalog' (1 resolved)",
                          text)
            self.assertIn("- %s  setting_two  (no setting definition)" % ids["setting_two"],
                          text)
            self.assertIn("- setting not_in_any_row  (recorded unresolved; no row matched it)",
                          text)
            self.assertIn("- 2 more unresolved row(s) that the rows file does not name", text)

    def test_every_refusal_is_reported_at_once(self):
        incident = "deviceConfigurations: list TRUNCATED after 1 page(s) (HTTP 503)"
        ids = self.unresolved_folder(incidents=[incident])
        _, err = self.ratify("2026-12-20", "--dry-run", code=2)
        self.assertIn("2 reasons to refuse, all shown so one --dry-run lists them", err)
        self.assertIn("1. 2026-12-20 was placed INCOMPLETE", err)
        self.assertIn("- " + incident, err)
        self.assertIn("2. 2026-12-20/baseline-rows.json: 2 unresolved row(s)", err)
        self.assert_lists_unresolved(err, ids)
        # Each override answers only its own refusal.
        _, err = self.ratify("2026-12-20", "--accept-incomplete-baseline", "--dry-run", code=2)
        self.assertNotIn("reasons to refuse", err)
        self.assertNotIn("INCOMPLETE", err)
        self.assert_lists_unresolved(err, ids)
        _, err = self.ratify("2026-12-20", "--allow-raw-labels", "--dry-run", code=2)
        self.assertIn("was placed INCOMPLETE", err)
        self.assertNotIn("unresolved row(s)", err)
        out, _ = self.ratify("2026-12-20", "--accept-incomplete-baseline",
                             "--allow-raw-labels", "--dry-run")
        self.assertIn("INCOMPLETE      1 incident(s)", out)
        self.assertIn("RAW LABELS      2 unresolved row(s)", out)

    def test_dirty_exporter_is_warned(self):
        self.tree.add_folder("2026-12-20", git_dirty=True)
        self.generate("2026-12-20")
        out, _ = self.ratify("2026-12-20", "--dry-run")
        self.assertIn("had uncommitted changes (tool.git_dirty true", out)

    # -- the Deviation cell, the one human-written cell between the markers ---------

    def windows_row(self, setting_id):
        block = split_page(self.win_page())[1]
        return next(line for line in block
                    if line.startswith("| BP-") and "`%s = " % setting_id in line)

    def set_deviation(self, setting_id, value):
        """Put an EXM- reference in one row's Deviation cell, as a human would."""
        page = self.tree.hardening / "hardening-standard-windows-endpoints.md"
        row = self.windows_row(setting_id)
        cells = table_cells(row)
        self.assertEqual(cells[6].strip(), "none")
        edited = row.replace("| none |", "| %s |" % value, 1)
        page.write_bytes(page.read_bytes().replace(row.encode(), edited.encode(), 1))
        return cells[0].strip()

    def test_deviation_survives_a_rerun_and_a_later_ratify(self):
        self.ratify("2026-09-25")
        rid = self.set_deviation("setting_two", "EXM-007")
        edited = self.tree.pages()
        out, _ = self.ratify("2026-09-25")
        self.assertIn("Deviation carried forward: %s EXM-007" % rid, out)
        self.assertEqual(edited, self.tree.pages(), "a same-date re-run moved something")
        self.tree.add_folder("2026-12-20", dump=stub_dump(value="later"))
        self.generate("2026-12-20")
        self.ratify("2026-12-20")
        cells = [c.strip() for c in table_cells(self.windows_row("setting_two"))]
        self.assertEqual((cells[0], cells[6]), (rid, "EXM-007"))
        self.assertIn("setting_two = later", cells[7])
        self.assertEqual(self.win_page().count("EXM-007"), 1)

    def test_deviation_on_a_vanished_row_is_warned_not_silently_dropped(self):
        self.ratify("2026-09-25")
        rid = self.set_deviation("setting_two", "EXM-009")
        self.tree.add_folder("2026-12-20", dump=stub_dump(drop=("setting_two",)))
        self.generate("2026-12-20")
        out, _ = self.ratify("2026-12-20", "--dry-run")
        self.assertIn("WARNING         hardening-standard-windows-endpoints.md: %s Deviation "
                      "EXM-009: the row is not in dumps/2026-12-20/baseline-rows.json" % rid,
                      out)
        self.assertIn("update the exemption register entry", out)

    def test_deviation_is_not_pinned_on_a_setting_its_id_no_longer_names(self):
        self.ratify("2026-09-25")
        rid = self.set_deviation("setting_two", "EXM-011")
        # Rebuild the id map the forbidden way: two ids swapped.
        id_map = self.tree.dumps / rcc.ID_MAP
        data = json.loads(id_map.read_text())
        prefix = "configurationPolicies|aaaaaaaa-0000-0000-0000-000000000001|"
        a, b = prefix + "setting_two", prefix + "device_vendor_msft_defender_allowrealtime"
        data["ids"][a], data["ids"][b] = data["ids"][b], data["ids"][a]
        id_map.write_text(json.dumps(data))
        self.tree.add_folder("2026-12-20")
        self.generate("2026-12-20")
        out, _ = self.ratify("2026-12-20")
        self.assertIn("%s Deviation EXM-011: the id now names "
                      "device_vendor_msft_defender_allowrealtime" % rid, out)
        self.assertNotIn("EXM-011", self.win_page())


class LabelResolution(unittest.TestCase):
    """Which rows a recorded miss names. A missing option names a row only when that row's
    value is, or holds, the option: listing every row of the setting would bury the one
    the approver has to look at."""

    def row(self, rid, setting_id, value):
        return {"id": rid, "row_key": rid.lower(), "setting_id": setting_id,
                "required_value": value}

    def test_rows_are_tied_by_definition_and_by_option_value(self):
        doc = {"meta": {"display_resolution": {
            "mode": "catalog", "resolved": 2, "unresolved": 4,
            "missing_definitions": ["Vendor_Def_A"],
            "missing_options": ["vendor_choice = vendor_choice_2",
                                "vendor_multi = vendor_multi_9"]}},
            "rows": [self.row("BP-WIN-0001", rcc.NAME_SETTING, "vendor_def_a"),
                     self.row("BP-WIN-0002", "vendor_def_a", "x"),
                     self.row("BP-WIN-0003", "vendor_def_a#2", "y"),
                     self.row("BP-WIN-0004", "vendor_choice", "vendor_choice_1"),
                     self.row("BP-WIN-0005", "vendor_choice", "vendor_choice_2"),
                     self.row("BP-WIN-0006", "vendor_multi",
                              '["vendor_multi_1","vendor_multi_9"]')]}
        labels = rcc.label_resolution(doc)
        self.assertEqual([r[0] for r in labels["rows"]],
                         ["BP-WIN-0002", "BP-WIN-0003", "BP-WIN-0005", "BP-WIN-0006"])
        self.assertEqual(labels["rows"][3][2], "no option label for vendor_multi_9")
        self.assertEqual(labels["unmatched"], [])
        self.assertEqual(labels["count"], 4)

    def test_a_count_that_is_not_a_non_negative_integer_is_unknown(self):
        for value in (None, True, -1, "2", 1.5):
            doc = {"meta": {"display_resolution": {"mode": "catalog", "unresolved": value}},
                   "rows": []}
            self.assertIsNone(rcc.label_resolution(doc)["count"], value)
        doc = {"meta": {"display_resolution": {"mode": "catalog", "unresolved": 0}},
               "rows": []}
        self.assertEqual(rcc.label_resolution(doc)["count"], 0)


# ------------------------------------------------------------------------------- pack

class Pack(CycleTestCase):

    def pack_args(self, date):
        html = (self.tree.dumps / date / rcc.PACK).read_text()
        return json.loads(re.search(r"<pre>(.*)</pre>", html).group(1))

    def test_baseline_defaults_to_ratified(self):
        self.tree.add_folder("2026-09-25")
        self.generate("2026-09-25")
        self.ratify("2026-09-25")
        self.tree.add_folder("2026-12-20")
        self.generate("2026-12-20")
        out, _ = self.ok(self.tree.run("pack", "2026-12-20"))
        self.assertIn("baseline        2026-09-25   (RATIFIED)", out)
        self.assertEqual(self.pack_args("2026-12-20"),
                         {"folder": "2026-12-20", "baseline": "2026-09-25",
                          "standards": str(self.tree.hardening)})

    def test_ratified_folder_packs_without_a_baseline(self):
        self.tree.add_folder("2026-09-25")
        self.generate("2026-09-25")
        self.ratify("2026-09-25")
        self.ok(self.tree.run("pack", "2026-09-25"))
        self.assertEqual(self.pack_args("2026-09-25"),
                         {"folder": "2026-09-25", "baseline": None,
                          "standards": str(self.tree.hardening)})

    def test_the_resolved_standards_dir_reaches_the_pack(self):
        """The pack shows each page's approval, so it must read the pages ratify wrote,
        wherever CONFIG_CYCLE_STANDARDS_DIR put them -- not a default beside the dumps."""
        elsewhere = self.tree.root / "standards-elsewhere"
        shutil.copytree(str(self.tree.hardening), str(elsewhere),
                        ignore=shutil.ignore_patterns("dumps"))
        self.tree.add_folder("2026-09-25")
        extra = {"CONFIG_CYCLE_STANDARDS_DIR": str(elsewhere)}
        self.ok(self.tree.run("generate", "2026-09-25", extra=extra))
        self.ok(self.tree.run("pack", "2026-09-25", extra=extra))
        self.assertEqual(self.pack_args("2026-09-25")["standards"], str(elsewhere))

    def test_no_resolvable_standards_dir_leaves_the_fallback_to_the_builder(self):
        """With no standards folder resolvable -- the wrapper copied where no
        security-documentation-restricted sits above it, and only --dumps-dir given --
        pack must not refuse. The builder falls back to the parent of the dumps directory,
        as pack did before --standards-dir existed."""
        self.tree.add_folder("2026-09-25")
        self.generate("2026-09-25")
        iso = Path(tempfile.mkdtemp(prefix="run-config-cycle-isolated-"))
        self.addCleanup(shutil.rmtree, str(iso), True)
        shutil.copy(str(WRAPPER), str(iso / WRAPPER.name))
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("CONFIG_CYCLE_", "STUB_")) and k != "STANDARDS_REPO"}
        env["CONFIG_CYCLE_PACK_BUILDER"] = str(self.tree.stubs / "pack.py")
        proc = subprocess.run([sys.executable, str(iso / WRAPPER.name), "pack", "2026-09-25",
                               "--no-baseline", "--dumps-dir", str(self.tree.dumps)],
                              capture_output=True, env=env, cwd=str(iso))
        self.assertEqual(proc.returncode, 0, proc.stderr.decode("utf-8"))
        self.assertIsNone(self.pack_args("2026-09-25")["standards"])

    def test_explicit_and_no_baseline(self):
        for date in ("2026-06-24", "2026-09-25"):
            self.tree.add_folder(date)
        self.ok(self.tree.run("pack", "2026-09-25", "--baseline", "2026-06-24"))
        self.assertEqual(self.pack_args("2026-09-25")["baseline"], "2026-06-24")
        self.ok(self.tree.run("pack", "2026-09-25", "--no-baseline"))
        self.assertIsNone(self.pack_args("2026-09-25")["baseline"])
        _, err = self.ok(self.tree.run("pack", "2026-09-25", "--baseline", "2026-09-25"),
                         code=2)
        self.assertIn("is the folder being packed", err)


# ------------------------------------------------- the real differ and pack builder

def differ_is_v2():
    differ = HERE / "diff_baseline.py"
    return differ.is_file() and rcc.NAME_SETTING in differ.read_text(encoding="utf-8")


@unittest.skipUnless(differ_is_v2(), "diff_baseline.py is not v2 yet")
class RealDifferAndPack(CycleTestCase):
    """The REAL differ and pack builder behind the wrapper, fed by the stub generator so
    this layer runs whatever state the real generator is in."""

    STUB_ONLY_GENERATOR = ("generator",)

    def setUp(self):
        super().setUp()
        self.tree.add_folder("2026-09-25")
        self.generate("2026-09-25", stubs=self.STUB_ONLY_GENERATOR)
        self.ratify("2026-09-25", stubs=self.STUB_ONLY_GENERATOR)

    def next_cycle(self, **dump_kw):
        self.tree.add_folder("2026-12-20", raw=json.dumps(stub_dump(**dump_kw),
                                                          indent=1).encode())
        self.generate("2026-12-20", stubs=self.STUB_ONLY_GENERATOR)

    def test_one_differ_run_writes_both_records_and_reports_the_rename_once(self):
        self.next_cycle(renames={"2": "Mac FileVault (renamed)"}, value="setting_two_0")
        out, _ = self.ok(self.tree.run("diff", stubs=self.STUB_ONLY_GENERATOR), code=1)
        self.assertEqual(out.count("run             diff_baseline.py"), 1, out)
        self.assertEqual(sorted(p.name for p in (self.tree.dumps / "2026-12-20").iterdir()
                                if rcc.PARTIAL in p.name), [], "a partial record was left")
        self.assertRegex(out, r"SUMMARY\s+renamed=1 reassigned=0")
        self.assertRegex(out, r"changed=1 removed=0 added=0")
        folder = self.tree.dumps / "2026-12-20"
        md = (folder / "diff-vs-2026-09-25.md").read_text(encoding="utf-8")
        self.assertTrue(md.startswith("---\ntype: Record\n"), md[:120])
        self.assertIn("\ndoc_type: record\n", md.split("\n---\n", 1)[0] + "\n")
        self.assertIn("Mac FileVault (renamed)", md)
        json.loads((folder / "diff-vs-2026-09-25.json").read_text(encoding="utf-8"))

    def test_no_change_is_exit_0_with_full_counts(self):
        self.next_cycle()
        out, _ = self.ok(self.tree.run("diff", stubs=self.STUB_ONLY_GENERATOR), code=0)
        self.assertIn("total differences: 0", out)
        self.assertIn("rows 7 -> 7", out)

    def test_pack_is_offline_and_reproducible(self):
        self.next_cycle(renames={"2": "Mac FileVault (renamed)"})
        out, _ = self.ok(self.tree.run("pack", "2026-12-20", stubs=self.STUB_ONLY_GENERATOR))
        self.assertIn("baseline        2026-09-25   (RATIFIED)", out)
        self.assertIn("--differ %s" % (HERE / "diff_baseline.py"), out)
        pack = self.tree.dumps / "2026-12-20" / rcc.PACK
        first = pack.read_bytes()
        self.ok(self.tree.run("pack", "2026-12-20", stubs=self.STUB_ONLY_GENERATOR))
        self.assertEqual(first, pack.read_bytes(), "the same inputs gave a different pack")
        html = first.decode("utf-8")
        self.assertEqual(network_references(html), [])
        # The stub tenant holds no URL-valued setting, so here the contract's literal rule
        # holds too: the only 'http' is the SVG namespace.
        hits = set(re.findall(r"https?://[^\s\"'<>)]*", html))
        self.assertTrue(hits <= {"http://www.w3.org/2000/svg"}, hits)

    def test_missing_manifest_refused_unless_passed_through(self):
        self.tree.add_folder("2026-12-20", manifest=False)
        self.generate("2026-12-20", stubs=self.STUB_ONLY_GENERATOR)
        self.ok(self.tree.run("pack", "2026-12-20", stubs=self.STUB_ONLY_GENERATOR), code=2)
        self.assertFalse((self.tree.dumps / "2026-12-20" / rcc.PACK).exists())
        out, _ = self.ok(self.tree.run("pack", "2026-12-20", "--allow-missing-manifest",
                                       stubs=self.STUB_ONLY_GENERATOR))
        self.assertIn("--allow-missing-manifest", out)
        self.assertTrue((self.tree.dumps / "2026-12-20" / rcc.PACK).is_file())

    def test_ratifying_a_later_dump_without_its_diff_warns(self):
        self.next_cycle(value="setting_two_0")
        out, _ = self.ratify("2026-12-20", "--dry-run", stubs=self.STUB_ONLY_GENERATOR)
        self.assertIn("holds no diff-vs-2026-09-25 record", out)
        self.ok(self.tree.run("diff", stubs=self.STUB_ONLY_GENERATOR), code=1)
        out, _ = self.ratify("2026-12-20", stubs=self.STUB_ONLY_GENERATOR)
        self.assertNotIn("holds no diff-vs", out)
        self.assertIn("| Version | 1.1 |",
                      self.tree.page("hardening-standard-windows-endpoints.md"))


# ------------------------------------------------------------------ the real scripts

def real_skip_reason():
    if not (REAL_DUMP and REAL_DUMP.is_file()):
        return "the real 2026-09-27 dump is not readable from here"
    generator = HERE / "generate_baseline.py"
    if not generator.is_file() or not rcc.supports(generator, "--definitions"):
        return "generate_baseline.py is not v2 yet (no --definitions flag)"
    differ = HERE / "diff_baseline.py"
    if not differ.is_file() or rcc.NAME_SETTING not in differ.read_text(encoding="utf-8"):
        return "diff_baseline.py is not v2 yet (no @displayName handling)"
    return None


REAL_SKIP = real_skip_reason()


@unittest.skipIf(REAL_SKIP, REAL_SKIP or "")
class RealScripts(CycleTestCase):
    """The wrapper against the real generator, differ and pack builder, on a copy of the
    real dump. Nothing here is stubbed except the second cycle, which is the real dump
    with one policy renamed."""

    def setUp(self):
        super().setUp()
        self.raw = REAL_DUMP.read_bytes()
        # Deliberately WITHOUT setting-definitions.json, so the rows carry raw labels
        # and ratify needs --allow-raw-labels. That exercises the override end to end.
        self.tree.add_folder("2026-09-24", raw=self.raw, definitions=False,
                             collected_at="2026-09-24T05:14:15Z")

    def run_real(self, *args, code=0):
        return self.ok(self.tree.run(*args, real=True), code)

    def test_generate_is_byte_identical_on_rerun(self):
        self.run_real("generate", "2026-09-24")
        folder = self.tree.dumps / "2026-09-24"
        names = [n for n in (rcc.ROWS, rcc.README) if (folder / n).is_file()]
        first = {n: (folder / n).read_bytes() for n in names}
        first_map = (self.tree.dumps / rcc.ID_MAP).read_bytes()
        self.run_real("generate", "2026-09-24")
        self.assertEqual(first, {n: (folder / n).read_bytes() for n in names})
        self.assertEqual(first_map, (self.tree.dumps / rcc.ID_MAP).read_bytes())
        doc = self.tree.rows("2026-09-24")
        self.assertEqual(doc["meta"]["generated_at"], "2026-09-24T05:14:15Z")
        self.assertEqual(doc["meta"]["source_sha256"], sha(self.raw))
        self.assertEqual(doc["meta"]["generator_version"].split(".")[0], "2")

    def test_ratify_diff_and_pack_end_to_end(self):
        self.run_real("generate", "2026-09-24")
        before = {name: self.tree.page(name) for _p, name, _s in PAGE_FILES}
        _, err = self.ok(self.tree.run("ratify", "2026-09-24", "--approved-by", "Eric Sharp",
                                       "--approved-on", APPROVED_ON, real=True), code=2)
        self.assertIn("display resolution 'none'", err)
        self.ok(self.tree.run("ratify", "2026-09-24", "--approved-by", "Eric Sharp",
                              "--approved-on", APPROVED_ON, "--allow-raw-labels", real=True))
        doc = self.tree.rows("2026-09-24")
        for platform, name, _sid in PAGE_FILES:
            after = self.tree.page(name)
            self.assert_outside_unchanged(before[name], after)
            block = split_page(after)[1]
            rows = [line for line in block if line.startswith("| BP-")]
            self.assertEqual(len(rows), sum(1 for r in doc["rows"]
                                            if r["platform"] == platform), name)
            for line in rows:
                self.assertEqual(len(table_cells(line)), 8, line)
        pages = self.tree.pages()
        self.ok(self.tree.run("ratify", "2026-09-24", "--approved-by", "Eric Sharp",
                              "--approved-on", APPROVED_ON, "--allow-raw-labels", real=True))
        self.assertEqual(pages, self.tree.pages(), "re-ratify was not idempotent")

        old_name, new_name = self.next_cycle_with_rename()
        out, _ = self.run_real("diff", code=1)
        self.assertIn("baseline        2026-09-24   (RATIFIED)", out)
        self.assertIn("current         2026-12-20   (newest folder)", out)
        md = (self.tree.dumps / "2026-12-20" / "diff-vs-2026-09-24.md").read_text()
        self.assertTrue(md.startswith("---\n"), md[:200])
        self.assertIn("type: Record", md.split("\n---\n", 1)[0])
        self.assertIn(old_name, md)
        self.assertIn(new_name, md)
        self.assertRegex(md.lower(), r"renam")
        json.loads((self.tree.dumps / "2026-12-20" / "diff-vs-2026-09-24.json").read_text())
        self.ok(self.tree.run("status", real=True))

    def next_cycle_with_rename(self):
        """A second cycle: the same tenant with one assigned policy renamed."""
        dump = json.loads(self.raw)
        policy = next(p for p in dump["configurationPolicies"] if p.get("isAssigned"))
        old_name, policy["name"] = policy["name"], policy["name"] + " (renamed)"
        self.tree.add_folder("2026-12-20", raw=json.dumps(dump, indent=2).encode(),
                             definitions=False)
        self.run_real("generate", "2026-12-20")
        return old_name, policy["name"]

    @unittest.skipUnless((HERE / "build_evidence_pack.py").is_file(),
                         "build_evidence_pack.py does not exist yet")
    def test_pack_against_ratified_has_no_network_references(self):
        self.run_real("generate", "2026-09-24")
        self.ok(self.tree.run("ratify", "2026-09-24", "--approved-by", "Eric Sharp",
                              "--approved-on", APPROVED_ON, "--allow-raw-labels", real=True))
        self.next_cycle_with_rename()
        out, _ = self.run_real("pack", "2026-12-20")
        self.assertIn("baseline        2026-09-24   (RATIFIED)", out)
        pack = self.tree.dumps / "2026-12-20" / rcc.PACK
        first = pack.read_bytes()
        self.assertEqual(network_references(first.decode("utf-8")), [])
        # The approval ratify wrote reaches the pack: wrapper -> builder -> the pages.
        text = first.decode("utf-8")
        self.assertEqual(text.count("matches RATIFIED"), 3)
        self.assertIn("Approved by <strong>Eric Sharp</strong> on <strong>%s</strong>"
                      % APPROVED_ON, text)
        self.assertIn("approval: BP-WIN version 1.0, approved by Eric Sharp on %s"
                      % APPROVED_ON, out)
        self.run_real("pack", "2026-12-20")
        self.assertEqual(first, pack.read_bytes(), "the same inputs gave a different pack")


if __name__ == "__main__":
    if REAL_SKIP:
        sys.stderr.write("note: real-script tests skipped -- %s\n" % REAL_SKIP)
    unittest.main(verbosity=2)
