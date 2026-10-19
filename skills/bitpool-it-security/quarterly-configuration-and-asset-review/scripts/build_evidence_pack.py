#!/usr/bin/env python3
"""Build the quarterly Intune hardening evidence pack: one self-contained HTML page.

This is the auditor-facing artefact for the configuration stream of the quarterly review.
It attaches in Drata against DCF-12 (System Security Configuration and Hardening Standards)
and DCF-171 (Documented Operating Procedures). It deliberately follows the evidence
contract of /network-segmentation-evidence, so the two packs read as one system:

  1. DATED AT COLLECTION   the timestamp comes from collection-manifest.json, written by
                           the exporter when the run STARTED. Never file mtime, never now().
  2. ATTRIBUTED            the collector identity comes from the same manifest, decoded by
                           the exporter from the access token's claims.
  3. HASHED                every input file's SHA-256 is printed in the page header, and
                           checked against the hash the exporter recorded at collection.
  4. REPRODUCIBLE          same inputs, byte-identical page. Nothing here reads the clock,
                           the hostname or an absolute path, and every list is sorted or
                           taken in the generator's deterministic row order.
  5. APPROVED              who approved the standard, when, at which version and from which
                           dump, read from the approval table of each hardening-standard page
                           (--standards-dir, default the parent of the dumps directory) and
                           shown in the header. RATIFIED alone is a pointer, not an approval:
                           each page must record an approval of the dump RATIFIED names, citing
                           that dump's raw sha256. The pages are hashed with the other inputs,
                           so the pack is bound to the exact approval text it shows.

Plus the two hard rules:

  * FINDINGS ARE COMPUTED from the data on this run. No sentence in a finding or a verdict
    card asserts a fact about the estate unless it is derived from the inputs. A resolved
    problem disappears on the next run without anyone remembering to delete a paragraph.
  * ZERO NETWORK REQUESTS. No webfont, no CDN, no script, no external stylesheet. The only
    `http` string permitted in the output is the SVG namespace declaration. The IBM Plex
    families are named first in every font stack and fall back to system faces, exactly as
    the network pack does. The CSS tokens and class names are copied from
    network-segmentation-evidence/scripts/style.py -- keep the two in step. URL-shaped
    configuration VALUES (real ones exist in the tenant) are written, in TEXT nodes only,
    with a character reference for their leading `h`, so the literal grep stays an audit:
    see e(). Attributes never get that treatment (see attr()), because a browser decodes a
    character reference inside an attribute and would fetch what the grep cannot see.
    The grep is not the only guard: before anything is written, audit_offline() parses the
    rendered page and refuses it if any tag, attribute or stylesheet could make a request.

Everything rendered is HTML-escaped. Policy names and setting values come from Intune, where
any administrator can type anything, so they are untrusted text -- a policy named
`<script>` must print as text, never run. The same holds for the manifest's incident
messages, which quote Graph error bodies.

COMPLETENESS is part of provenance. The exporter records every incident that made an export
incomplete (a list it could not drain, an assignments request that failed) in the manifest's
`incidents` list, and placement refuses a non-empty list unless --accept-incomplete is given.
So a dump that reaches this builder with incidents was placed incomplete on purpose, and the
pack says so in its header, in section 01 and as a high-severity finding -- a failed
assignments request looks exactly like an unassigned policy, and without this the exclusion
would read as a fact about Intune. `tool.git_dirty` is shown beside the commit it qualifies.

What refuses (exit 2) rather than rendering a convincing wrong answer:

  * no baseline-rows.json, or one whose generator_version major is not 2
  * baseline-rows.json whose source_sha256 is not the SHA-256 of the dump beside it --
    the tables would then describe a different dump from the one the header hashes
  * no collection-manifest.json, unless --allow-missing-manifest. With the flag the pack
    builds, but every provenance field reads NOT RECORDED, a high-severity finding says so,
    and a warning goes to stderr. Provenance is never inferred from a folder name or mtime
  * an unreadable or malformed manifest (a corrupt record is a defect to fix, not to skip)
  * --baseline naming the same folder as --folder (a self-diff always reads clean)
  * the differ exiting 2, or emitting anything that is not a JSON object
  * a rendered page that audit_offline() finds could make a network request (a builder
    bug: nothing is written)

Severity logic, stated so it can be tested rather than remembered:

  high    provenance or integrity is broken (no manifest, a raw file differing from its
          collection hash, a truncated export, incidents recorded by the exporter or an
          unreadable incidents record, an id-map defect), a ratified setting is no
          longer enforced (the differ reports a removal), or RATIFIED names a dump that a
          standard page does not record approving (page missing or unreadable, no approver,
          date or version, another folder or another sha256 cited, a wrong Standard ID)
  medium  a required value changed, an object crossed the assigned boundary, the standard
          is unratified, a page records an approval although there is no RATIFIED, or the
          comparison was not made against the ratified baseline, the
          baseline's own collection recorded incidents, or a provenance field is missing
          (including no incidents list at all, and a tool version that is not pinned:
          git_dirty true, or the commit or git_dirty not recorded)
  low     display-only gaps (labels that fell back to raw ids), additions not yet
          ratified, renames (identity held, so the name change is the whole event)

Exit codes: 0 pack written; 2 refused or failed. Findings never change the exit code --
the pack records them, it does not gate on them.

The comparison is produced by diff_baseline.py, invoked through its CLI with
`--format json`. This script never imports the differ or the generator, so either can be
rewritten without this one noticing, as long as the row and report contracts hold.

Pure stdlib. Run through WSL:

    python3 build_evidence_pack.py --folder dumps/2026-09-24 --out /tmp/evidence-pack.html
    python3 build_evidence_pack.py --folder dumps/2026-12-24 --baseline dumps/2026-09-24 \\
            --out dumps/2026-12-24/evidence-pack.html
"""

import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
import os
import re
import subprocess
import sys

PACK_VERSION = "1.0"
SUPPORTED_ROWS_MAJOR = "2"

RAW_EXPORT = "intune-config-export.json"
RAW_READABLE = "intune-config-export-readable.json"
DEFINITIONS = "setting-definitions.json"
MANIFEST = "collection-manifest.json"
ROWS = "baseline-rows.json"
RATIFIED = "RATIFIED"

BASELINE_COLLECTIONS = ("configurationPolicies", "deviceConfigurations",
                        "deviceCompliancePolicies")
COLLECTION_CLASS = {"configurationPolicies": "g-cp", "deviceConfigurations": "g-dc",
                    "deviceCompliancePolicies": "g-comp"}
COLLECTION_TOKEN = {"g-cp": "private", "g-dc": "isolated", "g-comp": "vendor"}
PLATFORM_ORDER = ("windows10", "macOS", "iOS")
PLATFORM_LABEL = {"windows10": "Windows", "macOS": "macOS", "iOS": "iOS"}
MODE_PILL = {"enforced": "p-ok", "compliance": "p-private", "identity": "p-vendor"}
NAME_SETTING = "@displayName"
ID_RE = re.compile(r"^BP-(WIN|MAC|IOS|GEN)-\d{4}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")
# A file name the manifest may attest: a plain name inside the dated folder, no path.
SAFE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

# Graph surfaces that references/configuration-baseline.md names as blind spots of the
# export. Each is reported as "not in this export" only when its key is absent from the
# dump on this run -- so the day the exporter learns one, it drops off the list by itself.
UNEXPORTED_SURFACES = (
    ("compliancePolicies", "Settings Catalog-format compliance policies"),
    ("intents", "Endpoint Security profiles (intents)"),
    ("templates", "Endpoint Security templates"),
    ("assignmentFilters", "assignment filters"),
    ("windowsDriverUpdateProfiles", "Windows driver update profiles"),
    ("windowsFeatureUpdateProfiles", "Windows feature update profiles"),
    ("windowsQualityUpdateProfiles", "Windows quality update profiles"),
    ("reusablePolicySettings", "reusable policy settings"),
)

# The differ's event classes, in the order an auditor should meet them. The differ's own
# `summary` decides which classes it counted; this table only supplies order and labels.
# (`mode_changed` was a v1 class. The v2 differ reports mode drift as a warning instead.)
DIFF_CLASSES = (
    ("integrity", "Id-map integrity defects"),
    ("object_removed", "Objects removed"),
    ("removed", "Settings removed"),
    ("changed", "Required values changed"),
    ("mode_changed", "Modes changed"),
    ("reassigned", "Objects reassigned"),
    ("renamed", "Objects renamed"),
    ("object_added", "Objects added"),
    ("added", "Settings added"),
)
DIFF_KNOWN = {k for k, _ in DIFF_CLASSES} | {"warnings"}
# Visible in the differ's report but deliberately NOT counted as drift: relabels with an
# unchanged raw value, and never-assigned objects coming and going.
NOT_COUNTED = (
    ("display_only", "Labels changed, raw value unchanged"),
    ("excluded_added", "Unassigned objects that appeared"),
    ("excluded_removed", "Unassigned objects that disappeared"),
)
# Classes that mean the running configuration no longer matches the standard, as opposed
# to classes that only add to it or rename within it.
DIFF_HARD = ("integrity", "removed", "object_removed", "changed", "mode_changed", "reassigned")

SEV_ORDER = {"high": 0, "medium": 1, "low": 2}
CTL = "DCF-12 · DCF-171"
NOT_RECORDED = "NOT RECORDED"

# The three standard pages ratify writes: platform, file, the Standard ID the page declares.
# The same list as run_config_cycle.PAGES, copied rather than imported, because this builder
# imports no sibling.
PAGES = (("windows10", "hardening-standard-windows-endpoints.md", "BP-WIN"),
         ("macOS", "hardening-standard-macos-endpoints.md", "BP-MAC"),
         ("iOS", "hardening-standard-ios-endpoints.md", "BP-IOS"))
# The approval-table rows the pack shows, in the order the pages carry them.
APPROVAL_LABELS = ("Standard ID", "Version", "Approved by", "Approved on", "Effective from",
                   "Ratified from")
MARK_START = "<!-- GENERATED:START -->"
UNSET = ("", "—", "-")
VERSION_RE = re.compile(r"^\d+\.\d+$")
MARK_END = "<!-- GENERATED:END -->"
# Exactly the Ratified from cell ratify writes. Matched whole, so a cell that merely CONTAINS
# a valid citation ("REVOKED, was dumps/...") is never read as one.
RATIFIED_FROM_RE = re.compile(r"dumps/(\d{4}-\d{2}-\d{2}) \(sha256 ([0-9a-f]{16})\)")
# The rows citation ratify writes at the top of every generated block.
ROWS_CITED_RE = re.compile(r"dumps/(\d{4}-\d{2}-\d{2})/baseline-rows\.json "
                           r"\(sha256 ([0-9a-f]{16})\)")


class Refusal(Exception):
    """Producing a pack here would produce a convincing wrong answer. Exit 2."""


# --------------------------------------------------------------------------------------
# Escaping and small helpers
# --------------------------------------------------------------------------------------

HTTP_RE = re.compile(r"(h)(ttp)", re.IGNORECASE)


def _escaped(x):
    """HTML-escape any value. None renders empty. Non-strings go through json.dumps so a
    boolean reads `true` as it does in the dump, not Python's `True`. quote=True escapes
    both quote characters."""
    if x is None:
        return ""
    if not isinstance(x, str):
        x = json.dumps(x, sort_keys=True, ensure_ascii=False)
    return html.escape(x, quote=True)


def e(x):
    """Escape a value for an HTML TEXT node. Never use it inside an attribute: use attr().

    The leading `h` of every `http` is written as a character reference. Real tenant
    values carry URLs -- the 2026-09-24 dump holds an SSO extension's
    `https://login.microsoftonline.com` list -- and in a text node they are text, not
    references, so they make no request. But the evidence contract's audit is a byte grep
    for `http` that may hit only the SVG namespace, and a grep that has to be interpreted
    is not an audit. The browser renders the value identically and html.unescape()
    recovers it exactly.

    That reasoning holds for text nodes ONLY. A browser decodes character references
    inside an attribute too, so `src="&#x68;ttps://..."` fetches exactly as `https://`
    would -- defanging there would hide a real reference from the grep. So attributes go
    through attr(), which does not defang, and audit_offline() decodes every attribute
    before judging it.
    """
    return HTTP_RE.sub(lambda mo: "&#x%x;%s" % (ord(mo.group(1)), mo.group(2)), _escaped(x))


def attr(x):
    """Escape a value for a double-quoted attribute. No `http` defang, deliberately: a URL
    that reaches an attribute must stay visible to the grep, and audit_offline() refuses
    the page. Every attribute value this builder writes today is a constant; this is the
    helper for the day one is not."""
    return _escaped(x)


def v(x):
    """Escape a configuration VALUE. Unlike e(), None is shown as `null`, not hidden."""
    if x is None:
        return "null"
    return e(x)


def nr(x):
    """A provenance field: escaped, or NOT RECORDED. Never guessed."""
    return e(x) if x not in (None, "") else NOT_RECORDED


def plural(n, one, many=None):
    return "%d %s" % (n, one if n == 1 else (many or one + "s"))


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def read_bytes(path):
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError as x:
        raise Refusal("cannot read %s: %s" % (path, x))


def parse_json(raw, path):
    try:
        return json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, ValueError) as x:
        raise Refusal("%s is not valid JSON: %s" % (path, x))


def platform_key(p):
    return (PLATFORM_ORDER.index(p) if p in PLATFORM_ORDER else len(PLATFORM_ORDER), str(p or ""))


def collection_key(c):
    return (BASELINE_COLLECTIONS.index(c) if c in BASELINE_COLLECTIONS
            else len(BASELINE_COLLECTIONS), str(c or ""))


def platform_label(p):
    return PLATFORM_LABEL.get(p, p or "other")


def json_kind(x):
    """What a JSON value is, in JSON's words, for a message about a malformed field."""
    if isinstance(x, bool):
        return "a boolean"
    if isinstance(x, (int, float)):
        return "a number"
    return {str: "a string", dict: "an object", list: "a list"}.get(type(x), "null")


def incidents_of(man):
    """The manifest's record of what made the export incomplete: (state, [text, ...]).

    state is `no-manifest`; `not-recorded` (no incidents key, or null -- an exporter that
    predates the record, or a hand-written manifest); `malformed` (not a list); or
    `recorded` (a list, possibly empty). An absent record is NOT a clean one. The exporter
    writes strings; anything else is kept, as sorted-key JSON, rather than dropped."""
    if man is None:
        return "no-manifest", []
    x = man.get("incidents")
    if x is None:
        return "not-recorded", []
    if not isinstance(x, list):
        return "malformed", []
    return "recorded", [i if isinstance(i, str)
                        else json.dumps(i, sort_keys=True, ensure_ascii=False) for i in x]


# --------------------------------------------------------------------------------------
# Reading one dated folder
# --------------------------------------------------------------------------------------

def recorded_status(name, sha, nbytes, manifest):
    """How a file compares with what the exporter recorded for it at collection."""
    if manifest is None:
        return "none"
    files = manifest.get("files") if isinstance(manifest.get("files"), dict) else {}
    rec = files.get(name)
    if not isinstance(rec, dict):
        return "unattested"
    rsha = str(rec.get("sha256") or "").lower()
    rbytes = rec.get("bytes")
    if rsha == sha and (rbytes is None or rbytes == nbytes):
        return "match"
    return "altered"


def read_cycle(folder, dumps_root, current, allow_missing_manifest):
    """Load a dated folder. The current folder is read in full; a baseline, only as far
    as the comparison and its integrity checks need."""
    name = os.path.basename(os.path.normpath(folder))
    if not os.path.isdir(folder):
        raise Refusal("%s is not a directory" % folder)
    c = {"name": name, "dir": folder, "files": [], "manifest": None,
         "manifest_present": False}

    def rel(fname):
        return os.path.relpath(os.path.join(folder, fname), dumps_root).replace(os.sep, "/")

    def present(fname, role, raw, status):
        c["files"].append({"name": fname, "rel": rel(fname), "present": True,
                           "sha256": sha256_bytes(raw), "bytes": len(raw), "role": role,
                           "status": status})
        return c["files"][-1]["sha256"]

    def absent(fname, role):
        c["files"].append({"name": fname, "rel": rel(fname), "present": False,
                           "role": role, "status": "absent"})

    # --- manifest first: every other file's status is judged against it -------------
    mpath = os.path.join(folder, MANIFEST)
    if os.path.isfile(mpath):
        mraw = read_bytes(mpath)
        man = parse_json(mraw, mpath)
        if not isinstance(man, dict):
            raise Refusal("%s is not a JSON object -- a corrupt provenance record must be "
                          "fixed or re-collected, not skipped" % mpath)
        c["manifest"], c["manifest_present"] = man, True
        present(MANIFEST, "collection manifest", mraw, "self")
    elif current and not allow_missing_manifest:
        raise Refusal(
            "%s has no %s.\n"
            "       Without it this pack is neither dated at collection nor attributed, which\n"
            "       are two of the four properties that make it evidence. Re-collect with the\n"
            "       current exporter, which writes the manifest. For a dump collected before\n"
            "       the manifest existed, pass --allow-missing-manifest: the pack then states\n"
            "       NOT RECORDED wherever provenance belongs, and raises it as a finding."
            % (folder, MANIFEST))
    else:
        absent(MANIFEST, "collection manifest")
    c["incidents_state"], c["incidents"] = incidents_of(c["manifest"])

    # --- the raw export ---------------------------------------------------------------
    rpath = os.path.join(folder, RAW_EXPORT)
    if os.path.isfile(rpath):
        raw = read_bytes(rpath)
        sha = sha256_bytes(raw)
        c["raw_sha256"] = present(RAW_EXPORT, "raw Graph export", raw,
                                  recorded_status(RAW_EXPORT, sha, len(raw), c["manifest"]))
        if current:
            c["raw_nextlinks"] = raw.count(b"@odata.nextLink")
            c["raw"] = parse_json(raw, rpath)
            if not isinstance(c["raw"], dict):
                raise Refusal("%s is not a JSON object" % rpath)
    elif current:
        raise Refusal("%s has no %s -- there is nothing to evidence" % (folder, RAW_EXPORT))
    else:
        c["raw_sha256"] = None
        absent(RAW_EXPORT, "raw Graph export")

    # --- the other raw files (current folder only) -------------------------------------
    if current:
        for fname, role in ((RAW_READABLE, "raw Graph export, readable"),
                            (DEFINITIONS, "raw setting definitions")):
            p = os.path.join(folder, fname)
            if not os.path.isfile(p):
                absent(fname, role)
                continue
            b = read_bytes(p)
            sha = present(fname, role, b,
                          recorded_status(fname, sha256_bytes(b), len(b), c["manifest"]))
            if fname == DEFINITIONS:
                c["definitions"] = parse_json(b, p)
                c["definitions_sha256"] = sha

    # --- anything else the manifest attests, so a file the exporter learns to write
    # later is hashed here without this script having to learn its name first ----------
    c["bad_manifest_names"] = []
    if current and c["manifest"] is not None:
        mfiles = c["manifest"].get("files") if isinstance(c["manifest"].get("files"), dict) else {}
        known = {f["name"] for f in c["files"]} | {ROWS}
        for fname in sorted(mfiles):
            if fname in known:
                continue
            if not SAFE_NAME_RE.match(fname):
                c["bad_manifest_names"].append(fname)   # never opened: untrusted path
                continue
            p = os.path.join(folder, fname)
            if os.path.isfile(p):
                b = read_bytes(p)
                present(fname, "raw, attested by the manifest", b,
                        recorded_status(fname, sha256_bytes(b), len(b), c["manifest"]))

    # --- the generated rows -------------------------------------------------------------
    ypath = os.path.join(folder, ROWS)
    if not os.path.isfile(ypath):
        raise Refusal("%s has no %s. Generate it first (run_config_cycle.py generate %s)."
                      % (folder, ROWS, name))
    yraw = read_bytes(ypath)
    doc = parse_json(yraw, ypath)
    if (not isinstance(doc, dict) or not isinstance(doc.get("meta"), dict)
            or not isinstance(doc.get("rows"), list)):
        raise Refusal("%s is not a baseline (needs a 'meta' object and a 'rows' list)" % ypath)
    ver = str(doc["meta"].get("generator_version") or "")
    if ver.split(".")[0] != SUPPORTED_ROWS_MAJOR:
        raise Refusal("%s is generator_version %r; this pack reads %s.x only. Regenerate it "
                      "(run_config_cycle.py generate %s)."
                      % (ypath, ver or "missing", SUPPORTED_ROWS_MAJOR, name))
    if not all(isinstance(r, dict) for r in doc["rows"]):
        raise Refusal("%s holds a row that is not a JSON object" % ypath)
    c["rows_doc"], c["rows_path"] = doc, ypath
    present(ROWS, "generated baseline rows" + ("" if current else ", compared"), yraw,
            "generated")

    src = str(doc["meta"].get("source_sha256") or "").lower()
    if current and src != c["raw_sha256"]:
        raise Refusal(
            "%s says it was generated from a dump with sha256 %s, but %s beside it hashes\n"
            "       to %s. The tables would describe a different dump from the one this pack\n"
            "       hashes. Regenerate it (run_config_cycle.py generate %s)."
            % (ROWS, src or "(none)", RAW_EXPORT, c["raw_sha256"], name))
    c["rows_source_matches"] = c.get("raw_sha256") is not None and src == c["raw_sha256"]
    c["files"].sort(key=lambda f: f["rel"])
    return c


def read_ratified(dumps_root):
    """The RATIFIED pointer: (date or None, problem or None)."""
    p = os.path.join(dumps_root, RATIFIED)
    if not os.path.isfile(p):
        return None, None
    try:
        with open(p, "r", encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError) as x:
        return None, "cannot be read (%s)" % x
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if len(lines) != 1 or not DATE_RE.match(lines[0]):
        return None, "does not hold exactly one YYYY-MM-DD line"
    if not os.path.isdir(os.path.join(dumps_root, lines[0])):
        return lines[0], "names %s, which is not a folder beside it" % lines[0]
    return lines[0], None


def md_cell(s):
    """A table cell ratify wrote, as the plain text it was written from: the exact inverse
    of run_config_cycle.md_text, which escapes an entity-like '&' as '&amp;', then '<' as
    '&lt;', then markdown punctuation with a backslash. Undone in reverse order."""
    s = re.sub(r"\\(.)", r"\1", s.strip())
    return s.replace("&lt;", "<").replace("&amp;", "&")


def read_standard_pages(standards_dir, dumps_root):
    """Each standard page's approval table, and the rows citation in its generated block.
    Read, never written, and never raises: a page that is absent, unreadable or not shaped
    the way ratify requires is recorded with its problem, and the findings decide what that
    means. The layout rule is ratify's own: frontmatter first, exactly one pair of generated
    markers, and the approval table anywhere outside the frontmatter and the markers."""
    pages = []
    for platform, fname, std_id in PAGES:
        path = os.path.join(standards_dir, fname)
        pg = {"platform": platform, "name": fname, "std_id": std_id, "present": False,
              "rel": os.path.relpath(path, dumps_root).replace(os.sep, "/"),
              "cells": {}, "rows_cited": None, "problem": None}
        pages.append(pg)
        if not os.path.isfile(path):
            pg["problem"] = "is not in the standards folder"
            continue
        try:
            raw = read_bytes(path)
        except Refusal:
            # No path in the text: it would put the checkout location into the page.
            pg["problem"] = "cannot be read"
            continue
        pg.update(present=True, sha256=sha256_bytes(raw), bytes=len(raw))
        try:
            lines = raw.decode("utf-8").splitlines()
        except UnicodeDecodeError:
            pg["problem"] = "is not UTF-8"
            continue
        pg["problem"] = read_approval_table(lines, pg)
    return pages


def read_approval_table(lines, pg):
    """Fill pg["cells"] and pg["rows_cited"] from a page's lines. Returns the problem, or
    None when the page is shaped the way ratify writes it."""
    if not lines or lines[0].strip() != "---":
        return "has no frontmatter block"
    fm_end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if fm_end is None:
        return "has a frontmatter block that is never closed"
    starts = [i for i, ln in enumerate(lines) if ln.strip() == MARK_START]
    ends = [i for i, ln in enumerate(lines) if ln.strip() == MARK_END]
    if len(starts) != 1 or len(ends) != 1 or not fm_end < starts[0] < ends[0]:
        return "does not have exactly one pair of generated markers after the frontmatter"
    start, end = starts[0], ends[0]

    def outside(i):
        return fm_end < i < start or i > end

    anchor = [i for i in range(len(lines))
              if outside(i) and re.match(r"^\|[ \t]*Standard ID[ \t]*\|", lines[i])]
    if len(anchor) != 1:
        return ("has %d approval tables (a '| Standard ID |' row outside the generated "
                "block), not one" % len(anchor))
    top = bottom = anchor[0]
    while top - 1 > fm_end and lines[top - 1].lstrip().startswith("|"):
        top -= 1
    while bottom + 1 < len(lines) and lines[bottom + 1].lstrip().startswith("|"):
        bottom += 1
    if not all(outside(i) for i in range(top, bottom + 1)):
        return "has an approval table that runs into the generated markers"
    table = lines[top:bottom + 1]
    for label in APPROVAL_LABELS:
        row = re.compile(r"^\|[ \t]*%s[ \t]*\|((?:[^|\\]|\\.)*)\|[ \t]*$" % re.escape(label))
        hits = [row.match(ln) for ln in table
                if re.match(r"^\|[ \t]*%s[ \t]*\|" % re.escape(label), ln)]
        if len(hits) != 1 or not hits[0]:
            return "has no single two-column '| %s |' row in its approval table" % label
        pg["cells"][label] = md_cell(hits[0].group(1))
    cited = [m for m in (ROWS_CITED_RE.search(ln) for ln in lines[start + 1:end]) if m]
    if len(cited) == 1:
        pg["rows_cited"] = (cited[0].group(1), cited[0].group(2))
    return None


def page_approval(pg, rat, rat_sha, rat_rows_sha):
    """Why this page does not evidence the standard RATIFIED names: a list of reasons,
    empty only when every check was made and held. rat_sha and rat_rows_sha are the
    sha256 of the ratified folder's raw export and rows, or None when they cannot be read --
    and a check that cannot be made is a reason, never a pass."""
    if not pg["present"] or pg["problem"]:
        return ["%s %s" % (pg["name"], pg["problem"])]
    c, why = pg["cells"], []
    if c["Standard ID"] != pg["std_id"]:
        why.append("%s declares Standard ID %s, not %s"
                   % (pg["name"], c["Standard ID"] or "nothing", pg["std_id"]))
    unset = [k for k in ("Version", "Approved by", "Approved on", "Effective from")
             if c[k] in UNSET]
    if unset:
        why.append("%s records no %s" % (pg["name"], ", ".join(unset)))
    if c["Version"] not in UNSET and not VERSION_RE.match(c["Version"]):
        why.append("%s's Version is %s, not MAJOR.MINOR" % (pg["name"], c["Version"]))
    for k in ("Approved on", "Effective from"):
        if c[k] not in UNSET and not DATE_RE.match(c[k]):
            why.append("%s's %s is %s, not a YYYY-MM-DD date" % (pg["name"], k, c[k]))
    rf = RATIFIED_FROM_RE.fullmatch(c["Ratified from"])
    if not rf:
        why.append("%s's Ratified from is not exactly dumps/YYYY-MM-DD (sha256 ...)"
                   % pg["name"])
    elif rf.group(1) != rat:
        why.append("%s was ratified from dumps/%s, but RATIFIED names %s"
                   % (pg["name"], rf.group(1), rat))
    elif not rat_sha:
        why.append("dumps/%s/%s cannot be read, so the sha256 %s cites (%s) cannot be "
                   "verified" % (rat, RAW_EXPORT, pg["name"], rf.group(2)))
    elif rf.group(2) != rat_sha[:16]:
        why.append("%s cites sha256 %s for dumps/%s, whose raw export hashes to %s"
                   % (pg["name"], rf.group(2), rat, rat_sha[:16]))
    rc = pg["rows_cited"]
    if not rc:
        why.append("%s's generated block names no dumps/YYYY-MM-DD/%s (sha256 ...) it was "
                   "rendered from" % (pg["name"], ROWS))
    elif rc[0] != rat:
        why.append("%s's settings were rendered from dumps/%s/%s, but RATIFIED names %s"
                   % (pg["name"], rc[0], ROWS, rat))
    elif not rat_rows_sha:
        why.append("dumps/%s/%s cannot be read, so the rows %s was approved with cannot be "
                   "verified" % (rat, ROWS, pg["name"]))
    elif rc[1] != rat_rows_sha[:16]:
        why.append("%s was approved with %s sha256 %s, but dumps/%s/%s now hashes to %s: the "
                   "rows changed after approval" % (pg["name"], ROWS, rc[1], rat, ROWS,
                                                    rat_rows_sha[:16]))
    return why


def approval_problems(m, pg):
    return page_approval(pg, m["ratified"], m["ratified_sha"], m["ratified_rows_sha"])


# --------------------------------------------------------------------------------------
# The comparison -- through the differ's CLI, never its internals
# --------------------------------------------------------------------------------------

def run_differ(differ, base_rows, cur_rows):
    cmd = [sys.executable, differ, "--baseline", base_rows, "--current", cur_rows,
           "--format", "json"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    except OSError as x:
        raise Refusal("cannot run the differ %s: %s" % (differ, x))
    if p.returncode not in (0, 1):
        detail = (p.stderr or p.stdout or "").strip()
        raise Refusal("the differ refused the comparison (exit %d):\n%s"
                      % (p.returncode, detail))
    try:
        doc = json.loads(p.stdout)
    except ValueError:
        raise Refusal("the differ exited %d but did not emit JSON on stdout" % p.returncode)
    if not isinstance(doc, dict):
        raise Refusal("the differ's JSON report is not an object")
    return {"doc": doc, "exit": p.returncode}


def diff_events(doc, key):
    x = doc.get(key)
    return [ev for ev in x if isinstance(ev, dict)] if isinstance(x, list) else []


def diff_count(doc, key):
    if isinstance(doc.get(key), list):
        return len(doc[key])
    s = doc.get("summary")
    if isinstance(s, dict) and isinstance(s.get(key), int):
        return s[key]
    return 0


def pick(ev, *keys):
    """First non-None of `keys`, looked up on the event and then on its nested row."""
    srcs = [ev] + [ev[k] for k in ("row", "current_row", "baseline_row")
                   if isinstance(ev.get(k), dict)]
    for s in srcs:
        for k in keys:
            if s.get(k) is not None:
                return s[k]
    return None


# --------------------------------------------------------------------------------------
# Model: everything the page shows, computed once
# --------------------------------------------------------------------------------------

def walk_definition_ids(node, out):
    if isinstance(node, dict):
        for k, x in node.items():
            if k == "settingDefinitionId" and isinstance(x, str):
                out.add(x)
            else:
                walk_definition_ids(x, out)
    elif isinstance(node, list):
        for x in node:
            walk_definition_ids(x, out)


def build_model(cur, base, ratified, ratified_problem, diff, pages=(), ratified_sha=None,
                ratified_rows_sha=None, standards_override=None):
    rows = cur["rows_doc"]["rows"]
    meta = cur["rows_doc"]["meta"]
    raw = cur["raw"]

    # objects, in the generator's deterministic row order
    objects, index = [], {}
    for r in rows:
        k = (r.get("collection"), str(r.get("object_id") or "").lower())
        if k not in index:
            index[k] = len(objects)
            objects.append({"platform": r.get("platform"), "collection": r.get("collection"),
                            "object_id": r.get("object_id"),
                            "object_name": r.get("object_name"), "rows": []})
        objects[index[k]]["rows"].append(r)
    by_platform = {}
    for o in objects:
        by_platform.setdefault(o["platform"], []).append(o)
    platforms = sorted(by_platform, key=platform_key)

    counts = {}
    for o in objects:
        slot = counts.setdefault(o["platform"], {}).setdefault(
            o["collection"], {"objects": 0, "rows": 0})
        slot["objects"] += 1
        slot["rows"] += len(o["rows"])

    # the acceptance test on the raw export, per references/configuration-baseline.md
    cps = [p for p in (raw.get("configurationPolicies") or []) if isinstance(p, dict)]
    truncated = [p for p in cps if isinstance(p.get("settingCount"), int)
                 and p["settingCount"] != len(p.get("settings") or [])]
    no_count = [p for p in cps if not isinstance(p.get("settingCount"), int)]
    no_assigned = [p for p in cps if "isAssigned" not in p]
    missing_collections = [c for c in BASELINE_COLLECTIONS if c not in raw]

    # every definition id in any settings tree is either fetched or listed unresolved
    defs = cur.get("definitions")
    def_check = None
    if isinstance(defs, dict):
        ids = set()
        for p in cps:
            walk_definition_ids(p.get("settings"), ids)
        unresolved = defs.get("_unresolved")
        unresolved = sorted(str(x) for x in unresolved) if isinstance(unresolved, list) else []
        have = {k for k in defs if k != "_unresolved"}
        def_check = {"ids": len(ids), "fetched": len(ids & have), "unresolved": unresolved,
                     "dropped": sorted(ids - have - set(unresolved))}

    other_collections = sorted((k, len(x) if isinstance(x, list) else None)
                               for k, x in raw.items() if k not in BASELINE_COLLECTIONS)
    unexported = [(k, label) for k, label in UNEXPORTED_SURFACES if k not in raw]

    # A standard page is an input like any other: hashing it binds the pack to the exact
    # approval text it shows.
    page_files = [{"name": pg["name"], "rel": pg["rel"], "present": True,
                   "sha256": pg["sha256"], "bytes": pg["bytes"],
                   "role": "standard page, approval written by ratify", "status": "standard"}
                  for pg in pages if pg["present"]]
    files = sorted(list(cur["files"]) + (list(base["files"]) if base else []) + page_files,
                   key=lambda f: f["rel"])
    present = [f for f in files if f["present"]]
    # Exactly the bytes `sha256sum <files in this order>` prints, so it can be recomputed
    # by an auditor with no access to this tool.
    digest = sha256_bytes("".join("%s  %s\n" % (f["sha256"], f["rel"])
                                  for f in present).encode("utf-8"))

    return {"cur": cur, "base": base, "meta": meta, "rows": rows, "objects": objects,
            "by_platform": by_platform, "platforms": platforms, "counts": counts,
            "cps": cps, "truncated": truncated, "no_count": no_count,
            "no_assigned": no_assigned, "missing_collections": missing_collections,
            "def_check": def_check, "other_collections": other_collections,
            "unexported": unexported, "files": files, "present": present,
            "digest": digest, "ratified": ratified, "ratified_problem": ratified_problem,
            "diff": diff, "pages": list(pages), "ratified_sha": ratified_sha,
            "ratified_rows_sha": ratified_rows_sha, "standards_override": standards_override}


# --------------------------------------------------------------------------------------
# Findings -- every one computed from the model on this run
# --------------------------------------------------------------------------------------

DISPOSE = ("Every difference from the ratified standard needs exactly one disposition before "
           "the cycle closes: a recorded rationale, a risk with a treatment plan, or a gap "
           "with a ticket.")


def compute_findings(m):
    f = []

    def add(sev, cat, title, body, test):
        f.append({"sev": sev, "cat": cat, "ctl": CTL, "title": title, "body": body,
                  "test": test})

    cur, meta, man = m["cur"], m["meta"], m["cur"]["manifest"]

    # --- provenance ---------------------------------------------------------------------
    if man is None:
        add("high", "provenance",
            "No collection manifest: this pack is not dated at collection or attributed",
            "%s has no %s. The collection time and the collector are therefore not recorded "
            "anywhere, and this page does not infer them from the folder name or a file date. "
            "The raw files are hashed in the header, but nothing binds those hashes to the "
            "moment and the identity that produced them." % (cur["name"], MANIFEST),
            "Evidence is dated at collection and attributed to whoever collected it. A dump "
            "without a manifest shows what a configuration was, but not when or by whom it "
            "was read, so on its own it cannot evidence a review on a given date.")
    else:
        # completeness first: it changes the meaning of everything else on the page
        inc_state, incs = cur["incidents_state"], cur["incidents"]
        if inc_state == "recorded" and incs:
            add("high", "integrity",
                "The export recorded %s: this collection is incomplete"
                % plural(len(incs), "incident"),
                "The exporter logged, while reading Graph: %s. Placement refuses a dump whose "
                "manifest records incidents unless --accept-incomplete is given, so this dump "
                "was placed incomplete on purpose (the manifest does not record the flag "
                "itself; a folder placed by hand would read the same). Against a complete "
                "baseline, missing data reads as settings removed, and a failed assignments "
                "request reads exactly like an unassigned policy, so any removal, "
                "reassignment or exclusion in this pack may describe the collection rather "
                "than Intune." % "; ".join(incs),
                "An export known to be incomplete evidences what could be read, not the "
                "configuration. Re-collect, or record why this dump is accepted as it is.")
        elif inc_state == "malformed":
            add("high", "integrity", "The manifest's incidents record is unreadable",
                "incidents is %s, not a list, so whether this export was complete cannot be "
                "read from the record the exporter wrote." % json_kind(man.get("incidents")),
                "Completeness is read from the collector's own record. A record that cannot "
                "be read proves nothing either way.")
        elif inc_state == "not-recorded":
            add("medium", "provenance",
                "The manifest does not record whether the export was complete",
                "%s carries no incidents list. The current exporter writes one on every run, "
                "empty when nothing went wrong, so its absence means an older exporter or a "
                "hand-written manifest. Completeness is therefore NOT RECORDED, which is not "
                "the same as clean." % MANIFEST,
                "Completeness is recorded by the collector, not inferred from silence.")

        when = man.get("collected_at_utc")
        if not (isinstance(when, str) and UTC_RE.match(when)):
            add("high", "provenance", "The manifest carries no valid collection time",
                "collected_at_utc is %s. Every date this page would print derives from it."
                % ("missing" if when is None else "%r, not an ISO 8601 UTC timestamp" % when),
                "Evidence is dated when the collection started, not when a file was saved.")
        who = man.get("collector") if isinstance(man.get("collector"), dict) else {}
        if not who.get("upn"):
            add("medium", "provenance", "The collector's identity was not recorded",
                "The manifest's collector.upn is empty%s. The exporter records null rather "
                "than guess when the access token carries no usable claim."
                % ("; object id %s is recorded" % who.get("object_id")
                   if who.get("object_id") else ", and so is the object id"),
                "A reviewer must be able to answer who produced this artefact.")
        cd = man.get("collection_date")
        if cd and cd != cur["name"]:
            add("medium", "provenance", "The folder name disagrees with the collection date",
                "The folder is %s but the manifest records collection_date %s."
                % (cur["name"], cd),
                "Cycle folders are named for the day of collection, so the name is a claim "
                "the manifest must support.")
        tool = man.get("tool") if isinstance(man.get("tool"), dict) else {}
        commit, dirty = tool.get("git_commit"), tool.get("git_dirty")
        tname = tool.get("name") or "the exporter"
        pinned = ("A commit id identifies the code that produced the evidence only when the "
                  "script that ran was that commit, unmodified.")
        if dirty is True:
            add("medium", "provenance",
                "The exporter that ran differed from its recorded git commit",
                "The manifest records git commit %s with git_dirty true: %s had uncommitted "
                "changes when it ran, so that commit does not identify the code that "
                "produced this dump." % (commit or "(none)", tname), pinned)
        elif not commit:
            add("medium", "provenance", "The exporter's git commit was not recorded",
                "tool.git_commit is %s, so which version of %s produced this dump is not "
                "recorded." % (json.dumps(commit), tname), pinned)
        elif dirty is not False:
            add("medium", "provenance",
                "Whether the exporter matched its recorded commit was not recorded",
                "tool.git_commit is %s but tool.git_dirty is %s rather than true or false, so "
                "it is not recorded whether the script that ran was that commit or a local "
                "modification of it." % (commit, json.dumps(dirty)), pinned)
        if man.get("schema") != 1:
            add("medium", "provenance", "Unrecognised manifest schema",
                "The manifest declares schema %s; this pack reads schema 1."
                % json.dumps(man.get("schema")),
                "Provenance fields are only meaningful under the schema that defines them.")
        mfiles = man.get("files") if isinstance(man.get("files"), dict) else {}
        if not mfiles:
            add("high", "provenance", "The manifest records no file hashes",
                "%s has no files map, so no raw file can be shown to be the one collected."
                % MANIFEST,
                "Hashing proves integrity only against a hash recorded at collection.")
        altered = [x["name"] for x in cur["files"] if x["status"] == "altered"]
        if altered:
            add("high", "provenance",
                "%s differ%s from the hash recorded at collection"
                % (plural(len(altered), "raw file"), "s" if len(altered) == 1 else ""),
                "Altered since collection: %s. The exporter recorded each file's hash when it "
                "saved it; a mismatch means the file on disk is not the one Graph returned."
                % ", ".join(altered),
                "Raw files are retained byte-for-byte unaltered; that is what makes a later "
                "comparison trustworthy.")
        if cur["bad_manifest_names"]:
            add("high", "provenance", "The manifest names files outside the dated folder",
                "Not plain file names, so not opened: %s." % ", ".join(cur["bad_manifest_names"]),
                "A manifest attests the files beside it; a path in it is a defect in the record.")
        on_disk = {x["name"] for x in cur["files"] if x["present"]}
        gone = sorted(n for n in mfiles if n not in on_disk and n not in cur["bad_manifest_names"])
        if gone:
            add("high", "provenance",
                "%s recorded at collection %s missing"
                % (plural(len(gone), "file"), "is" if len(gone) == 1 else "are"),
                "Listed in the manifest but absent from %s: %s." % (cur["name"], ", ".join(gone)),
                "A retained record that has lost part of itself cannot be reproduced.")
        unatt = [x["name"] for x in cur["files"] if x["status"] == "unattested"]
        if unatt:
            add("medium", "provenance",
                "%s not attested by the manifest" % plural(len(unatt), "raw file"),
                "Present in the folder but carrying no collection hash: %s." % ", ".join(unatt),
                "Every raw file should be bound to the collection that produced it.")

    # --- export completeness: the acceptance test ---------------------------------------
    def names(ps):
        return "; ".join(str(p.get("name")) for p in ps)

    if m["truncated"]:
        add("high", "integrity",
            "%s returned fewer settings than declared"
            % plural(len(m["truncated"]), "Settings Catalog policy", "Settings Catalog policies"),
            "settingCount does not equal the settings fetched: %s."
            % "; ".join("%s (%d of %d)" % (p.get("name"), len(p.get("settings") or []),
                                          p["settingCount"]) for p in m["truncated"]),
            "A truncated export produces a comparison that reports no change. The acceptance "
            "test is that every policy's settingCount equals its fetched settings.")
    if m["no_count"]:
        add("medium", "integrity",
            "%s carry no settingCount" % plural(len(m["no_count"]), "Settings Catalog policy",
                                                "Settings Catalog policies"),
            "Their completeness cannot be counted: %s." % names(m["no_count"]),
            "Completeness is shown by counting, not assumed.")
    if m["no_assigned"]:
        add("medium", "integrity",
            "%s carry no isAssigned flag" % plural(len(m["no_assigned"]),
                                                   "Settings Catalog policy",
                                                   "Settings Catalog policies"),
            "Scope is decided by assignment, so these cannot be placed in or out of it "
            "reliably: %s." % names(m["no_assigned"]),
            "The baseline covers assigned objects only.")
    if cur.get("raw_nextlinks"):
        add("high", "integrity", "The export still contains unfollowed page links",
            "%d occurrence(s) of @odata.nextLink remain in %s, so at least one collection or "
            "settings list was not read to its end." % (cur["raw_nextlinks"], RAW_EXPORT),
            "A page link left in the export is a page of configuration nobody compared.")
    if m["missing_collections"]:
        add("high", "integrity", "A baselined collection is absent from the export",
            "Not present in %s: %s." % (RAW_EXPORT, ", ".join(m["missing_collections"])),
            "An absent collection reads as an empty one, and a comparison over it is clean "
            "by construction.")
    dis = (meta.get("scope") or {}).get("assignment_disagreements") or []
    if dis:
        add("medium", "integrity",
            "isAssigned disagrees with the assignments array on %s" % plural(len(dis), "object"),
            "The generator reports %s where the flag and the assignment list disagree; the "
            "object's place in scope is uncertain until one is corrected."
            % plural(len(dis), "case"),
            "The acceptance test cross-checks isAssigned against assignments[]; a "
            "disagreement is a finding, not a formatting quirk.")

    # --- the rows themselves ------------------------------------------------------------
    rows = m["rows"]
    if meta.get("row_count") != len(rows):
        add("high", "integrity", "row_count does not match the rows present",
            "meta.row_count is %s but %s holds %d rows."
            % (json.dumps(meta.get("row_count")), ROWS, len(rows)),
            "A file that disagrees with its own header has been edited or truncated.")
    seen_k, seen_i, dup_k, dup_i, bad_i = set(), set(), set(), set(), 0
    for r in rows:
        k, i = r.get("row_key"), r.get("id")
        if k in seen_k:
            dup_k.add(k)
        seen_k.add(k)
        if not (isinstance(i, str) and ID_RE.match(i)):
            bad_i += 1
        elif i in seen_i:
            dup_i.add(i)
        else:
            seen_i.add(i)
    if dup_k or dup_i or bad_i:
        parts = []
        if dup_k:
            parts.append("%s shared by more than one row" % plural(len(dup_k), "row_key"))
        if dup_i:
            parts.append("%s on more than one row" % plural(len(dup_i), "BP- id"))
        if bad_i:
            parts.append("%s with no valid BP- id" % plural(bad_i, "row"))
        add("high", "integrity", "Row identity is not unique", "; ".join(parts) + ".",
            "Each setting has one permanent identity and one permanent id. A shared or "
            "missing one silently drops a row from every comparison.")
    bad_name = [o for o in m["objects"]
                if sum(1 for r in o["rows"] if r.get("setting_id") == NAME_SETTING) != 1]
    if bad_name:
        add("medium", "integrity",
            "%s lack exactly one policy-name row" % plural(len(bad_name), "object"),
            "Affected: %s." % "; ".join(str(o["object_name"]) for o in bad_name),
            "The name is diffed as a setting of its own, so a rename is one visible change. "
            "Without that row a rename goes unreported.")
    odd_mode = sorted({str(r.get("mode")) for r in rows if r.get("mode") not in MODE_PILL})
    if odd_mode:
        add("medium", "integrity", "Rows carry an unrecognised mode",
            "Modes outside enforced, compliance and identity: %s." % ", ".join(odd_mode),
            "An advisory row reading as enforced is false assurance.")
    mc = meta.get("counts")
    if isinstance(mc, dict):
        counted = sum(n for pc in mc.values() if isinstance(pc, dict)
                      for n in pc.values() if isinstance(n, int))
        if counted != len(rows):
            add("medium", "integrity", "meta.counts does not add up to the rows present",
                "The per-platform counts sum to %d; the file holds %d rows."
                % (counted, len(rows)),
                "A header that disagrees with its body cannot be quoted as scope.")

    # --- display resolution (labels only; never the compared value) ---------------------
    dres = meta.get("display_resolution") if isinstance(meta.get("display_resolution"),
                                                        dict) else {}
    dsha = meta.get("definitions_sha256")
    if dsha and not cur.get("definitions_sha256"):
        add("medium", "display", "Labels were resolved from a definitions file that is not here",
            "%s records definitions_sha256 %s, but %s is absent from %s."
            % (ROWS, str(dsha)[:16], DEFINITIONS, cur["name"]),
            "Every input a pack depends on is retained beside it.")
    elif dsha and dsha != cur.get("definitions_sha256"):
        add("medium", "display", "Labels were resolved from a different definitions file",
            "%s records definitions_sha256 %s; the file here hashes to %s."
            % (ROWS, str(dsha)[:16], str(cur.get("definitions_sha256"))[:16]),
            "Human-readable labels must come from the definitions retained with the dump.")
    if dres.get("mode") != "catalog":
        add("low", "display", "Settings Catalog labels are raw setting ids",
            "No setting definitions were used for this generation (display_resolution mode "
            "%s), so Setting and Required value show raw Graph identifiers. The compared "
            "value is unaffected: it is always the raw value."
            % json.dumps(dres.get("mode")),
            "Labels are for the reader. Every row is still verifiable, only more slowly.")
    elif isinstance(dres.get("unresolved"), int) and dres["unresolved"] > 0:
        add("low", "display", "%s fell back to raw values" % plural(dres["unresolved"], "label"),
            "%d label(s) resolved from the Settings Catalog definitions and %d did not, so "
            "those show the raw value instead." % (dres.get("resolved") or 0, dres["unresolved"]),
            "Labels are display only; the compared value is always the raw value.")
    dc = m["def_check"]
    if dc and dc["dropped"]:
        add("medium", "display",
            "%s neither fetched nor listed unresolved"
            % plural(len(dc["dropped"]), "setting definition"),
            "Present in the settings trees but absent from %s and from its _unresolved list: "
            "%s." % (DEFINITIONS, ", ".join(dc["dropped"])),
            "The exporter records every definition it could not fetch; a silent drop hides "
            "which labels are missing and why.")
    if dc and dc["unresolved"]:
        add("low", "display",
            "%s could not be fetched from Graph"
            % plural(len(dc["unresolved"]), "setting definition"),
            "Listed in %s _unresolved: %s." % (DEFINITIONS, ", ".join(dc["unresolved"])),
            "Recorded rather than dropped, so the gap is visible and bounded.")

    # --- the standard: is there a ratified baseline, and was this compared with it -------
    rat, base = m["ratified"], m["base"]
    if m["ratified_problem"]:
        add("medium", "standard", "The RATIFIED pointer is unusable",
            "dumps/%s %s." % (RATIFIED, m["ratified_problem"]),
            "Which dump the standard was ratified from must be unambiguous.")
    elif rat is None:
        add("medium", "standard", "No baseline has been ratified",
            "There is no dumps/%s file, so no dated folder has been approved as the hardening "
            "standard. Until one is, this configuration is recorded but not measured against "
            "anything." % RATIFIED,
            "A standard is normative: it states what configuration ought to be, and it "
            "changes only by a deliberate, approved act.")
    else:
        if base and base["name"] != rat:
            add("medium", "standard", "Compared against a baseline that is not the ratified one",
                "The comparison baseline is %s; the ratified standard is %s."
                % (base["name"], rat),
                "Drift is measured from the ratified standard, not from whichever earlier "
                "dump is to hand.")
        if not base and cur["name"] != rat:
            add("medium", "standard", "This cycle was not compared with the ratified baseline",
                "The ratified standard is %s and no baseline was supplied, so this pack "
                "records the configuration without showing whether it drifted." % rat,
                "The quarterly review exists to compare running configuration with the "
                "approved standard.")
        for pg in m["pages"]:
            why = approval_problems(m, pg)
            if why:
                add("high", "standard",
                    "The %s standard does not record the approval RATIFIED names"
                    % platform_label(pg["platform"]),
                    "%s." % "; ".join(why),
                    "The standard is approved only if its page names who approved it, when, "
                    "at which version, and from which dump. RATIFIED alone is a pointer, not "
                    "an approval.")
    if m["standards_override"]:
        add("low", "provenance", "The standard pages were read from outside the default layout",
            "--standards-dir named %s, relative to the dumps directory, not its parent. The "
            "page paths in the input digest are relative to the dumps directory, so moving "
            "either folder changes the digest." % m["standards_override"],
            "The digest is reproducible without this tool only while the layout it names holds.")
    if rat is None and not m["ratified_problem"]:
        claims = [pg["name"] for pg in m["pages"] if pg["present"] and not pg["problem"]
                  and RATIFIED_FROM_RE.fullmatch(pg["cells"]["Ratified from"])]
        if claims:
            add("medium", "standard", "A standard page records an approval that RATIFIED does not",
                "%s %s ratified from a dump, but there is no dumps/%s file."
                % (", ".join(claims), "says it was" if len(claims) == 1 else "say they were",
                   RATIFIED),
                "Which dump the standard was ratified from must be unambiguous.")

    # --- the comparison -----------------------------------------------------------------
    if base:
        bmeta = base["rows_doc"]["meta"]
        if not base["rows_source_matches"]:
            if base.get("raw_sha256"):
                add("high", "integrity", "The baseline's rows do not match its raw dump",
                    "%s/%s hashes to %s, but the baseline rows record source_sha256 %s."
                    % (base["name"], RAW_EXPORT, base["raw_sha256"][:16],
                       str(bmeta.get("source_sha256"))[:16]),
                    "A baseline is only as trustworthy as its tie to the dump it came from.")
            else:
                add("low", "integrity", "The baseline's raw dump is not retained beside it",
                    "%s/%s is absent, so the baseline rows cannot be re-derived from a "
                    "retained dump." % (base["name"], RAW_EXPORT),
                    "A baseline is only as trustworthy as its tie to the dump it came from.")
        b_altered = [x["name"] for x in base["files"] if x["status"] == "altered"]
        if b_altered:
            add("high", "provenance",
                "The baseline's raw dump differs from the hash recorded at its collection",
                "Altered since %s was collected: %s. The standard is measured from this "
                "dump, so the comparison inherits whatever changed in it."
                % (base["name"], ", ".join(b_altered)),
                "Raw files are retained byte-for-byte unaltered on both sides of a comparison.")
        if base["incidents_state"] == "recorded" and base["incidents"]:
            add("medium", "integrity",
                "The baseline's own collection recorded %s"
                % plural(len(base["incidents"]), "incident"),
                "%s was placed incomplete, with: %s. Whatever it could not read is absent from "
                "the baseline, so the same data read in full now surfaces in this comparison "
                "as additions rather than as drift."
                % (base["name"], "; ".join(base["incidents"])),
                "A comparison is only as complete as the less complete of its two sides.")
        elif base["incidents_state"] == "malformed":
            add("medium", "integrity", "The baseline's incidents record is unreadable",
                "%s's manifest holds incidents as %s, not a list, so whether the baseline "
                "was complete cannot be read." % (base["name"],
                                                  json_kind(base["manifest"].get("incidents"))),
                "A comparison is only as complete as the less complete of its two sides.")
        if not base["manifest_present"]:
            add("low", "provenance", "The baseline has no collection manifest",
                "%s carries no %s, so its collection time and collector are not recorded. Its "
                "rows are still bound to its raw dump by sha256." % (base["name"], MANIFEST),
                "Provenance on the reference side is stated rather than assumed.")
        doc = m["diff"]["doc"]
        for w in (doc.get("warnings") or []):
            add("medium", "drift", "The differ raised a warning", str(w),
                "A comparison caveat belongs in the evidence, not only on a console.")
        n_int = diff_count(doc, "integrity")
        if n_int:
            add("high", "integrity", "%s in the id map" % plural(n_int, "integrity defect"),
                "Between %s and %s the same setting carries a different BP- id, or one id "
                "sits on two settings." % (base["name"], cur["name"]),
                "Ids are permanent. A renumbered standard silently invalidates every prior "
                "sign-off that cited an id.")
        n_rm, n_orm = diff_count(doc, "removed"), diff_count(doc, "object_removed")
        if n_rm or n_orm:
            add("high", "drift", "Settings in the baseline are no longer enforced",
                "The differ reports %s and %s: present in %s, absent from %s. Each is listed "
                "in section 04." % (plural(n_rm, "setting removal"),
                                    plural(n_orm, "whole-object removal"),
                                    base["name"], cur["name"]),
                DISPOSE)
        for key, sev, title, gist in (
                ("changed", "medium", "Required values changed",
                 "the same setting now holds a different raw value"),
                ("mode_changed", "medium", "Enforcement modes changed",
                 "the value held but the way it is enforced did not"),
                ("reassigned", "medium", "Objects crossed the assigned boundary",
                 "an object moved into or out of scope by assignment"),
                ("object_added", "low", "Objects added and not yet ratified",
                 "a whole new object entered scope"),
                ("added", "low", "Settings added and not yet ratified",
                 "a setting exists that the standard does not state"),
                ("renamed", "low", "Objects renamed",
                 "the object id held and only the display name changed")):
            n = diff_count(doc, key)
            if n:
                add(sev, "drift", "%s: %d" % (title, n),
                    "Between %s and %s, %s in %s. Each is listed in section 04."
                    % (base["name"], cur["name"], gist, plural(n, "case")),
                    DISPOSE if key != "renamed" else
                    "Identity is the object id, so a rename is one event and moves no other "
                    "row's identity. It still needs a disposition.")

    f.sort(key=lambda x: SEV_ORDER[x["sev"]])  # stable: insertion order within a severity
    return f


# --------------------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------------------

CSS = """
<style>
:root{
  --paper:#F4F7F9; --surface:#FFFFFF; --surface-2:#EDF1F4;
  --ink:#0F1720; --ink-soft:#48565F; --ink-faint:#74838D;
  --rule:#D9E1E6; --rule-soft:#E7ECEF;
  --public:#A2661F; --private:#2F5B87; --isolated:#186354;
  --public-bg:#F7EEE1; --private-bg:#E7EFF7; --isolated-bg:#E1F0EB;
  --flag:#A2352A; --flag-bg:#F8E9E6; --vendor:#63548A; --vendor-bg:#EDEAF4;
  --warn:#8A6412; --edge:#7A8992;
  --shadow:0 1px 2px rgba(15,23,32,.06),0 8px 24px -12px rgba(15,23,32,.16);
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --paper:#0B1116; --surface:#131B22; --surface-2:#18222B;
    --ink:#E3EAEF; --ink-soft:#9DACB6; --ink-faint:#74848E;
    --rule:#26323B; --rule-soft:#1E2830;
    --public:#D9A05C; --private:#7FB0DD; --isolated:#5DBCA6;
    --public-bg:#2A2015; --private-bg:#152431; --isolated-bg:#122924;
    --flag:#E2867A; --flag-bg:#2E1A18; --vendor:#A899CE; --vendor-bg:#211D2E;
    --warn:#D6AC5A; --edge:#63737D;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px -12px rgba(0,0,0,.6);
  }
}
:root[data-theme="dark"]{
  --paper:#0B1116; --surface:#131B22; --surface-2:#18222B;
  --ink:#E3EAEF; --ink-soft:#9DACB6; --ink-faint:#74848E;
  --rule:#26323B; --rule-soft:#1E2830;
  --public:#D9A05C; --private:#7FB0DD; --isolated:#5DBCA6;
  --public-bg:#2A2015; --private-bg:#152431; --isolated-bg:#122924;
  --flag:#E2867A; --flag-bg:#2E1A18; --vendor:#A899CE; --vendor-bg:#211D2E;
  --warn:#D6AC5A; --edge:#63737D;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px -12px rgba(0,0,0,.6);
}
*{box-sizing:border-box}
body{background:var(--paper);color:var(--ink);
  font-family:"IBM Plex Sans",ui-sans-serif,system-ui,sans-serif;
  font-size:16px;line-height:1.6;margin:0;-webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto;padding:0 28px 96px}
code,.mono{font-family:"IBM Plex Mono",ui-monospace,monospace;font-variant-ligatures:none}
.rail{background:var(--surface);border-bottom:1px solid var(--rule);position:sticky;top:0;z-index:20}
.rail-in{max-width:1180px;margin:0 auto;padding:9px 28px;display:flex;flex-wrap:wrap;
  gap:7px 26px;align-items:baseline}
.rail .grp{white-space:nowrap}
.rail dt{font-size:9.5px;letter-spacing:.11em;text-transform:uppercase;color:var(--ink-faint);
  font-weight:600;margin:0 6px 0 0;display:inline}
.rail dd{margin:0;display:inline;font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--ink-soft)}
.rail dd.flag{color:var(--flag);font-weight:600}
header.hero{padding:52px 0 30px;border-bottom:1px solid var(--rule)}
.eyebrow{font-size:11px;letter-spacing:.15em;text-transform:uppercase;color:var(--private);
  font-weight:600;margin:0 0 14px}
h1{font-size:clamp(30px,4.4vw,46px);line-height:1.08;letter-spacing:-.021em;margin:0 0 16px;
  font-weight:600;text-wrap:balance}
.standfirst{font-family:"IBM Plex Serif",Georgia,serif;font-size:19px;line-height:1.58;
  color:var(--ink-soft);margin:0;max-width:64ch}
h2{font-size:23px;letter-spacing:-.012em;margin:0 0 6px;font-weight:600;text-wrap:balance}
h3{font-size:15px;margin:0 0 8px;font-weight:600}
h4{font-size:14.5px;margin:0;font-weight:600;color:var(--ink)}
section{padding-top:52px}
.sec-head{display:flex;gap:14px;align-items:baseline;border-bottom:1px solid var(--rule-soft);
  padding-bottom:12px;margin-bottom:22px;flex-wrap:wrap}
.sec-n{font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--ink-faint);
  font-weight:500;padding-top:5px}
.lede{font-family:"IBM Plex Serif",Georgia,serif;font-size:16.5px;color:var(--ink-soft);
  margin:0 0 22px;max-width:66ch;line-height:1.62}
p{margin:0 0 15px}
.verdict{display:grid;grid-template-columns:repeat(auto-fit,minmax(258px,1fr));gap:14px;margin:26px 0 4px}
.vcard{background:var(--surface);border:1px solid var(--rule);border-radius:9px;padding:17px 18px;
  box-shadow:var(--shadow)}
.vcard .k{font-size:10px;letter-spacing:.11em;text-transform:uppercase;font-weight:600;margin:0 0 9px}
.vcard.yes .k{color:var(--isolated)}
.vcard.no .k{color:var(--flag)}
.vcard.part .k{color:var(--warn)}
.vcard p{margin:0;font-size:14px;color:var(--ink-soft);line-height:1.55}
.vcard strong{color:var(--ink);font-weight:600}
.inputs{margin-top:30px}
.scroller{overflow-x:auto;background:var(--surface);border:1px solid var(--rule);
  border-radius:10px;padding:18px;box-shadow:var(--shadow)}
.scroller svg{display:block;min-width:640px;width:100%;height:auto}
figcaption{font-size:12.5px;color:var(--ink-faint);margin-top:11px;max-width:74ch}
figcaption b{color:var(--ink-soft);font-weight:600}
.key{display:flex;flex-wrap:wrap;gap:8px 20px;margin:16px 0 0;font-size:12px;color:var(--ink-soft)}
.key i{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:7px;
  vertical-align:-1px;font-style:normal}
.g-cp{fill:var(--private)} .g-dc{fill:var(--isolated)} .g-comp{fill:var(--vendor)}
.g-other{fill:var(--edge)}
.g-lab{font:600 12.5px "IBM Plex Sans",sans-serif;fill:var(--ink)}
.g-num{font:500 12px "IBM Plex Mono",monospace;fill:var(--ink-soft)}
table{border-collapse:collapse;width:100%;font-size:13.5px;font-variant-numeric:tabular-nums}
th{text-align:left;font-size:9.5px;letter-spacing:.11em;text-transform:uppercase;color:var(--ink-faint);
  font-weight:600;padding:0 14px 9px 0;border-bottom:1px solid var(--rule);white-space:nowrap}
td{padding:9px 14px 9px 0;border-bottom:1px solid var(--rule-soft);vertical-align:top;color:var(--ink-soft)}
td.k{color:var(--ink);font-weight:500}
td.n{text-align:right}
td.hash,td.val{word-break:break-all}
td.val{max-width:46ch}
td .path{display:block;font-size:11px;color:var(--ink-faint);margin-top:3px}
tr:last-child td{border-bottom:none}
.pill{display:inline-block;font-size:10px;font-weight:600;letter-spacing:.05em;padding:2.5px 8px;
  border-radius:999px;white-space:nowrap;text-transform:uppercase}
.p-private{background:var(--private-bg);color:var(--private)}
.p-flag{background:var(--flag-bg);color:var(--flag)}
.p-ok{background:var(--isolated-bg);color:var(--isolated)}
.p-vendor{background:var(--vendor-bg);color:var(--vendor)}
.p-warn{background:var(--public-bg);color:var(--warn)}
.p-none{background:var(--surface-2);color:var(--ink-faint)}
.finding{background:var(--surface);border:1px solid var(--rule);border-left-width:4px;
  border-radius:8px;padding:17px 20px;margin-bottom:12px;box-shadow:var(--shadow)}
.finding.high{border-left-color:var(--flag)}
.finding.medium{border-left-color:var(--warn)}
.finding.low{border-left-color:var(--edge)}
.f-top{display:flex;gap:12px;align-items:baseline;flex-wrap:wrap;margin-bottom:7px}
.f-sev{font-size:9.5px;letter-spacing:.11em;text-transform:uppercase;font-weight:700}
.high .f-sev{color:var(--flag)}
.medium .f-sev{color:var(--warn)}
.low .f-sev{color:var(--ink-faint)}
.f-ctl{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--ink-faint)}
.f-title{font-size:16px;font-weight:600;margin:0 0 7px;color:var(--ink);width:100%}
.finding p{font-size:14px;margin:0 0 10px;color:var(--ink-soft)}
.f-test{font-family:"IBM Plex Serif",Georgia,serif;font-style:italic;font-size:14px;
  color:var(--ink-soft);border-top:1px solid var(--rule-soft);padding-top:10px;margin:0}
pre{background:var(--surface);border:1px solid var(--rule);border-radius:9px;padding:16px 18px;
  overflow-x:auto;font-family:"IBM Plex Mono",monospace;font-size:12.5px;line-height:1.62;
  color:var(--ink-soft);margin:0 0 14px;box-shadow:var(--shadow)}
pre b{color:var(--private);font-weight:600}
pre i{color:var(--ink-faint);font-style:normal}
.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(212px,1fr));gap:12px;margin:22px 0}
.step{background:var(--surface);border:1px solid var(--rule);border-radius:9px;padding:15px 16px}
.step .n{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--private);font-weight:600;
  display:block;margin-bottom:7px}
.step h3{margin:0 0 6px;font-size:14px}
.step p{font-size:13px;margin:0;color:var(--ink-soft);line-height:1.5}
.note{background:var(--surface-2);border:1px solid var(--rule);border-radius:9px;padding:16px 18px;
  font-size:14px;color:var(--ink-soft);margin:20px 0}
.note strong{color:var(--ink)}
.note.flag{background:var(--flag-bg);border-color:var(--flag);color:var(--ink)}
.plat{margin-top:34px}
.obj{margin:0 0 22px}
.obj-head{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:baseline;margin:0 0 9px}
.obj-head .mono{font-size:11.5px;color:var(--ink-faint)}
.obj-head .cnt{font-size:12px;color:var(--ink-faint)}
footer{margin-top:64px;padding-top:22px;border-top:1px solid var(--rule);font-size:12px;
  color:var(--ink-faint);display:flex;justify-content:space-between;gap:18px;flex-wrap:wrap}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
@media (max-width:640px){.wrap{padding:0 18px 64px}.rail-in{padding:9px 18px}}
</style>
"""

STATUS_PILL = {
    "match": ("p-ok", "matches collection"),
    "altered": ("p-flag", "differs from collection"),
    "unattested": ("p-warn", "not in manifest"),
    "none": ("p-flag", "no manifest"),
    "self": ("p-none", "the record itself"),
    "generated": ("p-private", "generated after collection"),
    "standard": ("p-vendor", "written by ratify"),
    "absent": ("p-none", "absent"),
}


def prov(m):
    """Provenance fields as displayed. Missing stays None and renders NOT RECORDED."""
    man, cur = m["cur"]["manifest"], m["cur"]
    inc = {"inc_state": cur["incidents_state"], "incs": cur["incidents"]}
    if man is None:
        return dict(dict.fromkeys(("when", "date", "who", "oid", "src", "tenant", "client",
                                   "tool", "commit", "dirty")), **inc)
    who = man.get("collector") if isinstance(man.get("collector"), dict) else {}
    tool = man.get("tool") if isinstance(man.get("tool"), dict) else {}
    when = man.get("collected_at_utc")
    dirty = tool.get("git_dirty")
    return dict({"when": when if isinstance(when, str) and UTC_RE.match(when) else None,
                 "date": man.get("collection_date"),
                 "who": who.get("upn"), "oid": who.get("object_id"), "src": who.get("source"),
                 "tenant": man.get("tenant_id"), "client": man.get("client_id"),
                 "tool": tool.get("name"), "commit": tool.get("git_commit"),
                 "dirty": dirty if isinstance(dirty, bool) else None}, **inc)


def completeness_label(P):
    """The export's completeness as the rail and section 01 state it: (text, flagged)."""
    if P["inc_state"] == "recorded":
        if not P["incs"]:
            return "complete, no incidents recorded", False
        return "INCOMPLETE, %s" % plural(len(P["incs"]), "incident"), True
    if P["inc_state"] == "malformed":
        return "UNREADABLE incidents record", True
    return None, True


def rail(m, P):
    base = m["base"]
    export_state, export_flag = completeness_label(P)
    items = [("collected", P["when"], False), ("by", P["who"], False),
             ("export", export_state, export_flag),
             ("input digest", m["digest"][:16], False), ("rows", str(len(m["rows"])), False),
             ("objects", str(len(m["objects"])), False),
             ("baseline", base["name"] if base else "not compared", False),
             ("generator", "build_evidence_pack %s" % PACK_VERSION, False)]
    out = []
    for k, x, flag in items:
        cls = ' class="flag"' if flag or x in (None, "") else ""
        out.append('<div class="grp"><dt>%s</dt><dd%s>%s</dd></div>' % (k, cls, nr(x)))
    return '<div class="rail"><dl class="rail-in">%s</dl></div>' % "".join(out)


def verdict(m, fs, P):
    """The three cards an auditor reads first. EVERY CLAUSE HERE IS COMPUTED."""
    rows, objs, base, rat, cur = m["rows"], m["objects"], m["base"], m["ratified"], m["cur"]["name"]
    plats = ", ".join("%s %d" % (platform_label(p), sum(len(o["rows"]) for o in m["by_platform"][p]))
                      for p in m["platforms"])

    # card 1 -- is there a standard, and is this it
    if m["ratified_problem"]:
        c1, t1 = "part", "The RATIFIED pointer is unusable, so which dump is the standard is unclear."
    elif rat == cur:
        c1, t1 = "yes", "<strong>This dump is the ratified standard</strong> (dumps/%s)." % e(rat)
    elif rat:
        c1, t1 = "yes", "The ratified standard is <strong>dumps/%s</strong>." % e(rat)
    else:
        c1, t1 = "part", "<strong>No dump has been ratified yet</strong>, so the standard is still a draft."
    if rat and not m["ratified_problem"]:
        if any(approval_problems(m, pg) for pg in m["pages"]):
            c1 = "part"
            t1 += (" <strong>Its approval record is incomplete</strong>: read section 03.")
        else:
            who = sorted({(pg["cells"]["Approved by"], pg["cells"]["Approved on"])
                          for pg in m["pages"]})
            versions = ", ".join("%s %s" % (pg["std_id"], pg["cells"]["Version"])
                                 for pg in m["pages"])
            t1 += (" Approved by %s: %s."
                   % ("; ".join("<strong>%s</strong> on <strong>%s</strong>" % (e(a), e(d))
                                for a, d in who), e(versions)))
    card1 =('<div class="vcard %s"><p class="k">The standard is defined</p><p><strong>%s</strong> '
             'across %s on assigned objects (%s). %s</p></div>'
             % (c1, plural(len(rows), "row"), plural(len(objs), "object"), e(plats), t1))

    # card 2 -- does running configuration still match it
    if base:
        doc, ex = m["diff"]["doc"], m["diff"]["exit"]
        n = doc.get("difference_count")
        n = n if isinstance(n, int) else sum(diff_count(doc, k) for k, _ in DIFF_CLASSES)
        if ex == 0:
            c2 = "yes"
            t2 = ("<strong>No differences</strong> from dumps/%s. Both were read in full: %d rows "
                  "then, %d now." % (e(base["name"]), len(base["rows_doc"]["rows"]), len(rows)))
        else:
            hard = sum(diff_count(doc, k) for k in DIFF_HARD)
            c2 = "no" if hard else "part"
            parts = ["%d %s" % (diff_count(doc, k), lbl.lower()) for k, lbl in DIFF_CLASSES
                     if diff_count(doc, k)]
            t2 = ("<strong>%s</strong> from dumps/%s: %s. Each needs a disposition."
                  % (plural(n, "difference"), e(base["name"]), e("; ".join(parts))))
    elif rat == cur:
        c2, t2 = "part", ("<strong>Not compared.</strong> This dump is the ratified standard "
                          "itself, so drift is measured from the next cycle on.")
    else:
        c2, t2 = "part", ("<strong>Not compared.</strong> No baseline was supplied, so this pack "
                          "records the configuration but does not show whether it drifted.")
    if P["inc_state"] == "recorded" and P["incs"]:
        c2 = "part" if c2 == "yes" else c2
        t2 += (" <strong>The export recorded %s</strong>, so it is an incomplete collection: "
               "what it could not read is not shown, and cannot be shown to match."
               % plural(len(P["incs"]), "incident"))
    card2 =('<div class="vcard %s"><p class="k">Running configuration matches it</p><p>%s</p></div>'
             % (c2, t2))

    # card 3 -- does the evidence itself hold
    bad = [x for x in fs if x["sev"] == "high" and x["cat"] in ("provenance", "integrity")]
    matched = sum(1 for f in m["cur"]["files"] if f["status"] == "match")
    raw_files = sum(1 for f in m["cur"]["files"]
                    if f["present"] and f["status"] not in ("self", "generated"))
    if bad:
        c3 = "no"
        t3 = ("<strong>%s</strong> against provenance or integrity. Read section 03 before "
              "relying on anything below." % plural(len(bad), "high-severity finding"))
    else:
        c3 = "yes"
        t3 = ("<strong>%d of %d raw files</strong> match the SHA-256 recorded at collection. "
              "Collected %s by %s." % (matched, raw_files, nr(P["when"]), nr(P["who"])))
    card3 = ('<div class="vcard %s"><p class="k">The evidence holds</p><p>%s %s hashed in the '
             'header.</p></div>' % (c3, t3, plural(len(m["present"]), "input file")))
    return '<div class="verdict">%s%s%s</div>' % (card1, card2, card3)


def approval_block(m):
    """Who approved the standard, when, and from which dump -- as each page records it."""
    rat = None if m["ratified_problem"] else m["ratified"]
    trs = []
    for pg in m["pages"]:
        c = pg["cells"]
        if not pg["present"] or pg["problem"]:
            cells = "<td>&mdash;</td>" * 5
            state = ("p-flag" if rat else "p-none",
                     "page missing" if not pg["present"] else "unreadable")
        else:
            cells = "".join('<td class="%s">%s</td>' % (cls, e(c[k]))
                            for k, cls in (("Version", "mono"), ("Approved by", ""),
                                           ("Approved on", "mono"), ("Effective from", "mono"),
                                           ("Ratified from", "mono")))
            if not rat:
                state = ("p-none", "not ratified")
            elif approval_problems(m, pg):
                state = ("p-flag", "does not match RATIFIED")
            else:
                state = ("p-ok", "matches RATIFIED")
        trs.append('<tr><td class="k mono">%s</td><td>%s</td>%s'
                   '<td><span class="pill %s">%s</span></td></tr>'
                   % (e(pg["std_id"]), e(platform_label(pg["platform"])), cells,
                      state[0], state[1]))
    return """
  <div class="inputs">
  <h3>Approval of the standard</h3>
  <div class="scroller"><table><thead><tr><th>Standard</th><th>Platform</th><th>Version</th>
    <th>Approved by</th><th>Approved on</th><th>Effective from</th><th>Ratified from</th>
    <th>Against RATIFIED</th></tr></thead><tbody>%s</tbody></table></div>
  <figcaption>Read, never written, from the approval table of each standard page. Ratify writes
    those cells with a named approver; <span class="mono">dumps/RATIFIED</span> %s. Each page
    is hashed below, so this pack is bound to the exact approval text it shows.</figcaption>
  </div>""" % ("".join(trs),
               'reads <span class="mono">%s</span>' % e(m["ratified"]) if m["ratified"]
               else "does not exist")


def inputs_table(m):
    trs = []
    for f in m["files"]:
        cls, lbl = STATUS_PILL[f["status"]]
        trs.append('<tr><td class="k mono">%s</td><td>%s</td><td class="n mono">%s</td>'
                   '<td class="mono hash">%s</td><td><span class="pill %s">%s</span></td></tr>'
                   % (e(f["rel"]), e(f["role"]), e(f["bytes"]) if f["present"] else "&mdash;",
                      e(f["sha256"]) if f["present"] else "&mdash;", cls, lbl))
    return """
  <div class="inputs">
  <h3>Inputs, hashed</h3>
  <div class="scroller"><table><thead><tr><th>File</th><th>Role</th><th style="text-align:right">Bytes</th>
    <th>SHA-256</th><th>At collection</th></tr></thead><tbody>%s</tbody></table></div>
  <figcaption>Input digest <span class="mono">%s</span> is the SHA-256 of the lines
    <span class="mono">&lt;sha256&gt;&nbsp;&nbsp;&lt;file&gt;</span> for every present file above, in this
    order &mdash; exactly what <span class="mono">sha256sum</span> prints, so it can be recomputed without
    this tool (section 06). <b>Paths are relative to the dumps directory</b>, so the digest does not
    depend on where the repository is checked out.</figcaption>
  </div>""" % ("".join(trs), e(m["digest"]))


def provenance_section(m, P):
    man = m["cur"]["manifest"]
    if man is None:
        body = ('<div class="note flag"><strong>No collection manifest.</strong> '
                '<span class="mono">%s</span> is absent from <span class="mono">%s</span>, so the '
                'collection time, the collector, the tenant and the tool version are '
                '<strong>not recorded</strong>. This page does not infer any of them from the '
                'folder name or from file dates: a folder name is a label someone chose, not a '
                'record of when Graph was read.</div>' % (MANIFEST, e(m["cur"]["name"])))
    else:
        dirty = {True: "true: the script that ran differed from this commit",
                 False: "false: the script that ran was this commit, unmodified"}.get(P["dirty"])
        export_state, _ = completeness_label(P)
        kv = [("Collected at (UTC)", P["when"]), ("Collection date", P["date"]),
              ("Collector", P["who"]), ("Collector object id", P["oid"]),
              ("Identity taken from", P["src"]), ("Tenant", P["tenant"]),
              ("App (client) id", P["client"]), ("Tool", P["tool"]),
              ("Tool git commit", P["commit"]), ("Tool git dirty", dirty),
              ("Export completeness", export_state), ("Manifest schema", man.get("schema"))]
        body = ('<div class="scroller"><table><tbody>%s</tbody></table></div>'
                '<figcaption>Read from <span class="mono">%s</span>, written by the exporter. The '
                'collection time is taken <b>once, when the run starts</b>; the collector is '
                'decoded from the access token&#x27;s own claims rather than typed in. '
                '<b>Tool git dirty</b> qualifies the commit beside it: a commit id alone would '
                'vouch for code that may not be what ran.</figcaption>'
                % ("".join('<tr><td class="k">%s</td><td class="mono">%s</td></tr>' % (k, nr(x))
                           for k, x in kv), MANIFEST))
        if P["inc_state"] == "recorded" and P["incs"]:
            body += ("""<div class="note flag"><strong>This export is incomplete.</strong> The exporter
    recorded %s while reading Graph, and placement refuses such a dump unless
    <span class="mono">--accept-incomplete</span> is given, so it was placed knowing this. Anything it
    could not read is missing from every table below: a failed assignments request makes an assigned
    policy look unassigned, and against a complete baseline a missing list reads as settings removed.</div>
  <div class="scroller"><table><thead><tr><th>#</th><th>Incident, as the exporter recorded it</th></tr></thead>
    <tbody>%s</tbody></table></div>"""
                     % (plural(len(P["incs"]), "incident"),
                        "".join('<tr><td class="n mono">%d</td><td class="val mono">%s</td></tr>'
                                % (i, e(t)) for i, t in enumerate(P["incs"], 1))))

    cps, dc = m["cps"], m["def_check"]
    dis = (m["meta"].get("scope") or {}).get("assignment_disagreements") or []

    def ok(b):
        return ('<span class="pill p-ok">pass</span>' if b
                else '<span class="pill p-flag">fail</span>')

    inc_state, incs = m["cur"]["incidents_state"], m["cur"]["incidents"]
    if inc_state == "recorded":
        inc_check = (ok(not incs), plural(len(incs), "incident") + " recorded")
    elif inc_state == "malformed":
        inc_check = (ok(False), "incidents record unreadable")
    else:
        inc_check = ('<span class="pill p-none">not recorded</span>',
                     "no manifest" if inc_state == "no-manifest" else "no incidents list")
    checks = [
        ("The exporter recorded no incidents while reading Graph",) + inc_check,
        ("Every Settings Catalog policy returned as many settings as its settingCount declares",
         ok(not m["truncated"] and not m["no_count"]),
         "%d of %d" % (len(cps) - len(m["truncated"]) - len(m["no_count"]), len(cps))),
        ("isAssigned is present on every Settings Catalog policy", ok(not m["no_assigned"]),
         "%d of %d" % (len(cps) - len(m["no_assigned"]), len(cps))),
        ("isAssigned agrees with the assignments array", ok(not dis),
         plural(len(dis), "disagreement")),
        ("No unfollowed @odata.nextLink remains in the export",
         ok(not m["cur"].get("raw_nextlinks")), "%d found" % (m["cur"].get("raw_nextlinks") or 0)),
        ("All three baselined collections are present in the export",
         ok(not m["missing_collections"]),
         "%d of %d" % (len(BASELINE_COLLECTIONS) - len(m["missing_collections"]),
                       len(BASELINE_COLLECTIONS))),
        ("Every setting definition id was fetched or listed as unresolved",
         ok(not dc["dropped"]) if dc else '<span class="pill p-none">not checked</span>',
         ("%d of %d fetched, %d unresolved, %d dropped"
          % (dc["fetched"], dc["ids"], len(dc["unresolved"]), len(dc["dropped"])))
         if dc else "no %s" % DEFINITIONS),
        ("%s was generated from exactly this dump" % ROWS, ok(True),
         "sha256 %s" % m["cur"]["raw_sha256"][:16]),
    ]
    trs = "".join('<tr><td>%s</td><td>%s</td><td class="mono">%s</td></tr>' % (e(a), b, e(c))
                  for a, b, c in checks)
    return """
<section id="provenance">
  <div class="sec-head"><span class="sec-n">01</span><div><h2>Where this came from</h2></div></div>
  <p class="lede">An auditor asking what the configuration was on a given day cannot be answered by a
    live query, which only ever shows today. This is a retained, read-only export, and the record of
    who took it and when is written at the moment it is taken.</p>
  %s
  <h3 style="margin-top:30px">Acceptance test on the raw export</h3>
  <div class="scroller"><table><thead><tr><th>Check</th><th>Result</th><th>Count</th></tr></thead>
    <tbody>%s</tbody></table></div>
  <figcaption><b>A truncated export produces a comparison that reports no change</b>, so completeness
    is counted on every run rather than assumed. A clean result is still stated, with its count.</figcaption>
</section>""" % (body, trs)


def scope_svg(m):
    plats = m["platforms"]
    colls = sorted({c for p in plats for c in m["counts"][p]}, key=collection_key)
    totals = {p: sum(s["rows"] for s in m["counts"][p].values()) for p in plats}
    mx = max(totals.values()) if totals else 1
    W, left, barw, rowh, top = 840, 110, 620, 34, 8
    h = top * 2 + rowh * max(len(plats), 1)
    out = ['<svg viewBox="0 0 %d %d" role="img" aria-label="Rows by platform and collection" '
           'xmlns="http://www.w3.org/2000/svg">' % (W, h)]
    for i, p in enumerate(plats):
        y = top + i * rowh
        out.append('<text x="0" y="%d" class="g-lab">%s</text>' % (y + 18, e(platform_label(p))))
        x = left
        for c in colls:
            n = (m["counts"][p].get(c) or {}).get("rows", 0)
            w = max((barw * n) // mx, 2) if n else 0
            if w:
                out.append('<rect x="%d" y="%d" width="%d" height="20" rx="3" class="%s">'
                           '<title>%s: %d</title></rect>'
                           % (x, y + 4, w, COLLECTION_CLASS.get(c, "g-other"), e(c), n))
            x += w
        out.append('<text x="%d" y="%d" class="g-num">%d</text>' % (x + 8, y + 18, totals[p]))
    out.append("</svg>")
    return "".join(out)


def scope_section(m):
    colls = sorted({c for p in m["platforms"] for c in m["counts"][p]}, key=collection_key)
    trs = []
    for p in m["platforms"]:
        for c in sorted(m["counts"][p], key=collection_key):
            s = m["counts"][p][c]
            trs.append('<tr><td class="k">%s</td><td class="mono">%s</td><td class="n">%d</td>'
                       '<td class="n">%d</td></tr>'
                       % (e(platform_label(p)), e(c), s["objects"], s["rows"]))
    excl = (m["meta"].get("scope") or {}).get("excluded_objects") or []
    excl = sorted((x for x in excl if isinstance(x, dict)),
                  key=lambda x: (platform_key(x.get("platform")), collection_key(x.get("collection")),
                                 str(x.get("name") or "").casefold(), str(x.get("object_id") or "")))
    etrs = "".join('<tr><td class="k">%s</td><td class="mono">%s</td><td>%s</td>'
                   '<td class="mono">%s</td><td><span class="pill p-warn">%s</span></td></tr>'
                   % (e(x.get("name")), e(x.get("collection")), e(platform_label(x.get("platform"))),
                      e(x.get("object_id")), e(x.get("reason"))) for x in excl)
    excl_block = ("<p>No object in the three baselined collections was excluded.</p>" if not excl
                  else """<div class="scroller"><table><thead><tr><th>Object</th><th>Collection</th>
    <th>Platform</th><th>Object id</th><th>Reason</th></tr></thead><tbody>%s</tbody></table></div>
  <figcaption><b>An unassigned object enforces nothing</b>, so it is not part of the baseline and a
    change to one is not drift. Listing each with its reason is what separates a deliberate exclusion
    from an object nobody looked at.</figcaption>""" % etrs)

    other = "".join('<tr><td class="mono">%s</td><td class="n">%s</td></tr>'
                    % (e(k), e(n) if n is not None else "&mdash;") for k, n in m["other_collections"])
    unexp = "".join('<tr><td class="mono">%s</td><td>%s</td></tr>' % (e(k), e(lbl))
                    for k, lbl in m["unexported"])
    limits = []
    if other:
        limits.append("""<h3 style="margin-top:28px">Exported, but not part of the baseline</h3>
  <div class="scroller"><table><thead><tr><th>Collection in the export</th>
    <th style="text-align:right">Objects</th></tr></thead><tbody>%s</tbody></table></div>
  <figcaption>Retained in the raw export and hashed with it, but carrying no rows here.</figcaption>""" % other)
    if unexp:
        limits.append("""<h3 style="margin-top:28px">Not in this export at all</h3>
  <div class="scroller"><table><thead><tr><th>Graph surface</th><th>Holds</th></tr></thead>
    <tbody>%s</tbody></table></div>
  <figcaption><b>Each is a candidate gap, not a confirmed absence.</b> A policy authored on one of these
    surfaces is invisible to this pack, and the collections above cannot report it.</figcaption>""" % unexp)
    key = "".join('<span><i style="background:var(--%s)"></i>%s</span>'
                  % (COLLECTION_TOKEN.get(COLLECTION_CLASS.get(c, ""), "edge"), e(c)) for c in colls)
    return """
<section id="scope">
  <div class="sec-head"><span class="sec-n">02</span><div><h2>What is in scope</h2></div></div>
  <p class="lede">Scope is decided by assignment: an object is in the baseline because it is assigned
    to devices, and every object left out is listed with its reason. Rows are counted per platform and
    per collection straight from the rows in section 05.</p>
  <figure style="margin:0 0 22px"><div class="scroller">%s</div><div class="key">%s</div></figure>
  <div class="scroller"><table><thead><tr><th>Platform</th><th>Collection</th>
    <th style="text-align:right">Objects</th><th style="text-align:right">Rows</th></tr></thead>
    <tbody>%s</tbody></table></div>
  <h3 style="margin-top:28px">Excluded, and why &mdash; %d</h3>
  %s
  %s
  <div class="note"><strong>What this pack does not cover.</strong> It reads the Intune configuration
    surfaces named above and nothing else. It says nothing about a device that is not Intune-managed,
    and nothing about the AWS plane.</div>
</section>""" % (scope_svg(m), key, "".join(trs), len(excl), excl_block, "".join(limits))


def findings_section(fs):
    if not fs:
        body = ('<div class="note"><strong>No findings on this run.</strong> Every check in section '
                '01 passed and the comparison, where one was made, found nothing to dispose of.</div>')
    else:
        body = "".join("""<div class="finding %s">
  <div class="f-top"><span class="f-sev">%s</span><span class="f-ctl">%s</span></div>
  <p class="f-title">%s</p><p>%s</p>
  <p class="f-test">%s</p></div>""" % (x["sev"], x["sev"], e(x["ctl"]), e(x["title"]),
                                       e(x["body"]), e(x["test"])) for x in fs)
    return """
<section id="findings">
  <div class="sec-head"><span class="sec-n">03</span><div><h2>What the data says</h2></div></div>
  <p class="lede">Each finding is derived by the builder from the inputs &mdash; comparisons in code, not
    judgement typed into a document. Re-run it after a fix and a resolved finding disappears on its
    own.</p>
  %s
</section>""" % body


def labelled(label, raw):
    """A human label with the raw value beneath it -- or just the raw value when the two
    are the same. The raw value is always shown: it is what was compared."""
    rv = '<span class="mono">%s</span>' % v(raw)
    if label is None or label == raw:
        return rv
    return '%s<span class="path">%s</span>' % (v(label), rv)


def event_columns(key):
    """(header, cell) pairs per differ class, for the v2 report shape. Cells read through
    pick(), so a field nested under `row` (the v1 shape) is found either way, and a field
    the differ does not supply renders empty rather than failing the pack."""
    def mono(x):
        return '<span class="mono">%s</span>' % x

    oid = ("Object id", lambda ev: mono(e(pick(ev, "object_id"))))
    obj = ("Object", lambda ev: e(pick(ev, "object_name", "name")))
    rid = ("ID", lambda ev: mono(e(pick(ev, "id"))))
    sid = ("Setting", lambda ev: labelled(pick(ev, "setting_name"), pick(ev, "setting_id")))
    col = ("Collection", lambda ev: mono(e(pick(ev, "collection"))))
    nrows = ("Rows", lambda ev: e(pick(ev, "row_count")))
    ids = ("Row ids", lambda ev: mono(e(", ".join(str(i) for i in (pick(ev, "ids") or [])))))
    frm = ("From", lambda ev: labelled(pick(ev, "from_display"),
                                       pick(ev, "from", "baseline_value", "old_value")))
    to = ("To", lambda ev: labelled(pick(ev, "to_display"),
                                    pick(ev, "to", "current_value", "new_value")))
    value = ("Value", lambda ev: labelled(pick(ev, "display_value"), pick(ev, "required_value")))

    def unaffected(ev):
        u, t = pick(ev, "unaffected_settings", "unaffected"), pick(ev, "total_settings")
        return e(u) if t is None else "%s of %s" % (e(u), e(t))

    if key == "renamed":
        return [oid, col,
                ("Old name", lambda ev: e(pick(ev, "from", "old_name"))),
                ("New name", lambda ev: e(pick(ev, "to", "new_name"))),
                ("Settings unaffected", unaffected)]
    if key == "reassigned":
        return [obj, oid, col, ("Direction", lambda ev: e(pick(ev, "direction"))),
                ("Reason", lambda ev: e(pick(ev, "reason"))), nrows, ids]
    if key in ("object_added", "object_removed"):
        return [obj, oid, col, ("Platform", lambda ev: e(pick(ev, "platform"))), nrows, ids]
    if key in ("added", "removed"):
        return [rid, obj, sid, value]
    if key in ("changed", "mode_changed"):
        return [rid, obj, sid, frm, to]
    if key == "integrity":
        return [("Kind", lambda ev: e(pick(ev, "kind"))),
                ("row_key", lambda ev: mono(e(pick(ev, "row_key")))),
                ("Baseline id", lambda ev: mono(e(pick(ev, "baseline_id")))),
                ("Current id", lambda ev: mono(e(pick(ev, "current_id")))),
                ("Detail", lambda ev: e(pick(ev, "detail")))]
    if key == "display_only":
        return [rid, obj, ("Setting id", lambda ev: mono(e(pick(ev, "setting_id")))),
                ("Label then", lambda ev: v(pick(ev, "from_display"))),
                ("Label now", lambda ev: v(pick(ev, "to_display"))),
                ("Raw value, both", lambda ev: mono(v(pick(ev, "required_value"))))]
    if key in ("excluded_added", "excluded_removed"):
        return [obj, oid, col, ("Platform", lambda ev: e(pick(ev, "platform"))),
                ("Reason", lambda ev: e(pick(ev, "reason")))]
    return [("Event", lambda ev: mono(e(ev)))]


def event_table(title, evs, key):
    cols = event_columns(key)
    head = "".join("<th>%s</th>" % e(h) for h, _ in cols)
    body = "".join("<tr>%s</tr>" % "".join('<td class="val">%s</td>' % fn(ev) for _, fn in cols)
                   for ev in evs)
    return ('<h3 style="margin-top:26px">%s &mdash; %d</h3><div class="scroller"><table>'
            '<thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
            % (e(title), len(evs), head, body))


def counted_classes(doc):
    """The classes the differ itself counted, in DIFF_CLASSES order, then any it added."""
    s = doc.get("summary")
    if not isinstance(s, dict):
        return list(DIFF_CLASSES)
    label = dict(DIFF_CLASSES)
    known = [(k, lbl) for k, lbl in DIFF_CLASSES if k in s]
    return known + [(k, k) for k in sorted(s) if k not in label]


def diff_section(m):
    base = m["base"]
    if not base:
        return """
<section id="comparison">
  <div class="sec-head"><span class="sec-n">04</span><div><h2>What changed since the baseline</h2></div></div>
  <div class="note"><strong>No comparison was made.</strong> This pack was built without a baseline, so it
    records the configuration in %s and says nothing about how it differs from any earlier cycle.</div>
</section>""" % e(m["cur"]["name"])
    doc, ex = m["diff"]["doc"], m["diff"]["exit"]
    bn = doc.get("baseline") if isinstance(doc.get("baseline"), dict) else {}
    cn = doc.get("current") if isinstance(doc.get("current"), dict) else {}
    brc = bn["row_count"] if isinstance(bn.get("row_count"), int) else len(base["rows_doc"]["rows"])
    crc = cn["row_count"] if isinstance(cn.get("row_count"), int) else len(m["rows"])
    classes = counted_classes(doc)
    srows = [(lbl, diff_count(doc, k)) for k, lbl in classes]
    if isinstance(doc.get("unchanged_rows"), int):
        srows.append(("Rows unchanged", doc["unchanged_rows"]))
    summary = "".join('<tr><td class="k">%s</td><td class="n mono">%d</td></tr>' % (e(lbl), n)
                      for lbl, n in srows)
    blocks = []
    listed = {k for k, _ in classes}
    extra = sorted(k for k, x in doc.items()
                   if isinstance(x, list) and k not in DIFF_KNOWN and k not in listed)
    for k, lbl in classes + [(k, k) for k in extra]:
        evs = diff_events(doc, k)
        if evs:
            blocks.append(event_table(lbl, evs, k))
    if not blocks:
        blocks.append('<div class="note"><strong>No differences.</strong> Both baselines were read and '
                      'compared in full; the counts above are the evidence the comparison ran.</div>')
    nc = doc.get("not_counted") if isinstance(doc.get("not_counted"), dict) else {}
    nc_blocks = [event_table(lbl, diff_events(nc, k), k) for k, lbl in NOT_COUNTED
                 if diff_events(nc, k)]
    if nc:
        blocks.append("""<h3 style="margin-top:34px">Visible, but not counted as drift</h3>
  <p>%s. <b>None of these changes a compared value</b>: a relabel leaves the raw value where it was,
    and an object that was never assigned was never part of the standard.</p>%s"""
                      % (e("; ".join("%s: %d" % (lbl, len(diff_events(nc, k)))
                                     for k, lbl in NOT_COUNTED)), "".join(nc_blocks)))
    return """
<section id="comparison">
  <div class="sec-head"><span class="sec-n">04</span><div><h2>What changed since the baseline</h2></div></div>
  <p class="lede">Rows are joined on their permanent identity &mdash; collection, object id and setting
    id &mdash; and only the raw required value is compared. A Microsoft relabel, a new display label or
    a policy rename cannot pose as a configuration change.</p>
  <div class="scroller"><table><thead><tr><th></th><th>Folder</th><th style="text-align:right">Rows</th>
    <th>Source dump sha256</th></tr></thead><tbody>
    <tr><td class="k">Baseline</td><td class="mono">%s</td><td class="n mono">%d</td><td class="mono hash">%s</td></tr>
    <tr><td class="k">Current</td><td class="mono">%s</td><td class="n mono">%d</td><td class="mono hash">%s</td></tr>
  </tbody></table></div>
  <h3 style="margin-top:26px">Counts by class &mdash; differ exit %d</h3>
  <div class="scroller"><table><thead><tr><th>Class</th><th style="text-align:right">Count</th></tr></thead>
    <tbody>%s</tbody></table></div>
  <figcaption>Produced by <span class="mono">diff_baseline.py --format json</span>%s, run by this
    builder rather than pasted in. Exit 0 means no differences, 1 means differences; <b>a no-change
    result still prints every count</b>, because &ldquo;no change&rdquo; without them is
    indistinguishable from nobody having looked.</figcaption>
  %s
</section>""" % (e(base["name"]), brc, e(base["rows_doc"]["meta"].get("source_sha256")),
                 e(m["cur"]["name"]), crc, e(m["meta"].get("source_sha256")), ex, summary,
                 (" (report %s, row contract %s)" % (e(doc.get("diff_version")),
                                                      e(doc.get("row_contract")))
                  if doc.get("diff_version") is not None else ""),
                 "".join(blocks))


def rows_section(m):
    parts = []
    for p in m["platforms"]:
        objs = m["by_platform"][p]
        blocks = []
        for o in objs:
            trs = "".join(
                '<tr><td class="k mono">%s</td><td>%s</td><td class="val">%s</td>'
                '<td><span class="pill %s">%s</span></td>'
                '<td class="val mono">%s = %s<span class="path">%s</span></td></tr>'
                % (e(r.get("id")), e(r.get("setting_name")), v(r.get("display_value")),
                   MODE_PILL.get(r.get("mode"), "p-flag"), e(r.get("mode")),
                   e(r.get("setting_id")), v(r.get("required_value")), e(r.get("verify")))
                for r in o["rows"])
            nset = sum(1 for r in o["rows"] if r.get("setting_id") != NAME_SETTING)
            blocks.append("""<div class="obj"><div class="obj-head"><h4>%s</h4>
  <span class="mono">%s</span><span class="pill p-private">%s</span><span class="cnt">%s</span></div>
  <div class="scroller"><table><thead><tr><th>ID</th><th>Setting</th><th>Required value</th><th>Mode</th>
    <th>Raw value in the dump</th></tr></thead><tbody>%s</tbody></table></div></div>"""
                          % (e(o["object_name"]), e(o["object_id"]), e(o["collection"]),
                             plural(nset, "setting"), trs))
        parts.append('<div class="plat"><h3>%s &mdash; %s, %s</h3>%s</div>'
                     % (e(platform_label(p)), plural(len(objs), "object"),
                        plural(sum(len(o["rows"]) for o in objs), "row"), "".join(blocks)))
    return """
<section id="configuration">
  <div class="sec-head"><span class="sec-n">05</span><div><h2>The configuration, setting by setting</h2></div></div>
  <p class="lede">Every row of <span class="mono">%s</span>, grouped by platform and object. Required value
    is the human-readable label; the raw value beside it is what is compared between cycles, and what an
    auditor checks against the dump at the path shown. Each object&#x27;s first row is its name, diffed
    like any other setting, so a rename is one visible change.</p>
  %s
</section>""" % (ROWS, "".join(parts))


def pipeline_section(m):
    base = m["base"]
    files = " \\\n    ".join(e(f["rel"]) for f in m["present"])
    cmd = ("python3 build_evidence_pack.py --folder dumps/%s%s%s%s --out evidence-pack.html"
           % (e(m["cur"]["name"]), (" --baseline dumps/%s" % e(base["name"])) if base else "",
              " --allow-missing-manifest" if m["cur"]["manifest"] is None else "",
              (" --standards-dir dumps/%s" % e(m["standards_override"]))
              if m["standards_override"] else ""))
    return """
<section id="pipeline">
  <div class="sec-head"><span class="sec-n">06</span><div><h2>How this page was made &mdash; and how it
    stays true</h2></div></div>
  <p class="lede">Nothing here was typed by hand. The page is a pure function of the dated, hashed files
    listed in its header: build it twice from the same inputs and the two files are byte-identical.</p>
  <div class="steps">
    <div class="step"><span class="n">01</span><h3>Collect</h3><p>A read-only Microsoft Graph export. The
      exporter records the start time, the collector&#x27;s token claims and every file&#x27;s SHA-256 in
      the manifest.</p></div>
    <div class="step"><span class="n">02</span><h3>Generate</h3><p>Assigned objects become rows keyed by
      object id and setting id, never by name. Row ids are permanent and never reused.</p></div>
    <div class="step"><span class="n">03</span><h3>Compare</h3><p>The differ joins two cycles on that
      identity and compares only the raw value, so a relabel cannot pose as drift.</p></div>
    <div class="step"><span class="n">04</span><h3>Render</h3><p>This page: findings computed from the
      inputs, every value escaped, no network request of any kind.</p></div>
  </div>
  <pre><i># rebuild this page -- byte-identical output for identical inputs</i>
<b>%s</b>

<i># recompute the input digest without this tool, from the dumps directory</i>
<b>sha256sum %s \\
    | sha256sum</b>
<i># expect %s</i></pre>
</section>""" % (cmd, files, e(m["digest"]))


def render(m, fs):
    P = prov(m)
    h1 = ("The Intune hardening baseline, as collected on %s" % e(P["date"]) if P["date"] else
          "The Intune hardening baseline in %s &mdash; collection date not recorded"
          % e(m["cur"]["name"]))
    banner = ""
    if P["inc_state"] == "recorded" and P["incs"]:
        banner = ('<div class="note flag"><strong>Incomplete collection.</strong> The exporter '
                  'recorded %s while reading Graph, and this dump was placed anyway. Nothing '
                  'below shows the whole configuration: read section 01 and the findings in '
                  'section 03 first.</div>' % plural(len(P["incs"]), "incident"))
    elif P["inc_state"] == "malformed":
        banner = ('<div class="note flag"><strong>Completeness unreadable.</strong> The '
                  'manifest&#x27;s incidents record is not a list, so whether this export is '
                  'complete cannot be read. See section 03.</div>')
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Intune Hardening Evidence</title>
%s
</head>
<body>
%s
<div class="wrap">
<header class="hero">
  <p class="eyebrow">Evidence pack &middot; A.8.9 configuration management &middot; DCF-12 &middot; DCF-171</p>
  <h1>%s</h1>
  <p class="standfirst">Generated from a read-only Microsoft Graph export of the Intune tenant. Every row is
    a setting on an assigned policy, identified by the policy&#x27;s object id rather than its name, and
    compared on its raw value. It answers the question DCF-12 turns on &mdash; is there an approved
    hardening standard, and does running configuration still match it &mdash; from the export itself
    rather than from intent.</p>
  %s
  %s
  %s
  %s
</header>
%s
%s
%s
%s
%s
%s
<footer>
  <span>build_evidence_pack %s &middot; collected %s &middot; input digest %s</span>
  <span>Read-only. Nothing in Intune was modified.</span>
</footer>
</div>
</body>
</html>
""" % (CSS, rail(m, P), h1, banner, verdict(m, fs, P), approval_block(m), inputs_table(m),
       provenance_section(m, P),
       scope_section(m), findings_section(fs), diff_section(m), rows_section(m),
       pipeline_section(m), PACK_VERSION, nr(P["when"]), e(m["digest"]))


# --------------------------------------------------------------------------------------
# The offline audit -- a parse of the rendered page, not a grep of its bytes
# --------------------------------------------------------------------------------------

SVG_NS = "http://www.w3.org/2000/svg"
# Elements that load, embed, navigate or submit. None is ever emitted by this builder.
FETCHING_TAGS = frozenset((
    "a", "applet", "audio", "base", "button", "embed", "feimage", "form", "frame",
    "frameset", "iframe", "image", "img", "input", "link", "object", "picture", "portal",
    "script", "source", "track", "use", "video"))
# Attributes that take a URL. None is ever emitted by this builder.
FETCHING_ATTRS = frozenset((
    "action", "archive", "background", "cite", "codebase", "data", "dynsrc", "formaction",
    "href", "longdesc", "lowsrc", "manifest", "ping", "poster", "src", "srcset",
    "xlink:href"))
CSS_FETCH_RE = re.compile(r"url\s*\(|@import|image-set\s*\(|expression\s*\(|@font-face",
                          re.IGNORECASE)


class _OfflineAudit(HTMLParser):
    """Collects every construct that could make a browser request anything.

    html.parser decodes character references in attribute values, so `&#x68;ttps` in an
    attribute is judged as the browser will see it: as `https`."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.problems, self._in_style = [], False

    def handle_starttag(self, tag, attrs):
        if tag in FETCHING_TAGS:
            self.problems.append("<%s> element" % tag)
        if tag == "style":
            self._in_style = True
        for name, val in attrs:
            val = val or ""
            if name in FETCHING_ATTRS:
                self.problems.append("%s= on <%s>" % (name, tag))
            if name.startswith("on"):
                self.problems.append("event handler %s= on <%s>" % (name, tag))
            if tag == "meta" and name == "http-equiv":
                self.problems.append("<meta http-equiv>")
            if name == "style" and CSS_FETCH_RE.search(val):
                self.problems.append("fetching CSS in a style attribute on <%s>" % tag)
            if "http" in val.lower() and not (tag == "svg" and name == "xmlns"
                                              and val == SVG_NS):
                self.problems.append("a URL in %s= on <%s>" % (name, tag))

    def handle_endtag(self, tag):
        if tag == "style":
            self._in_style = False

    def handle_data(self, data):
        if self._in_style and (CSS_FETCH_RE.search(data) or "http" in data.lower()):
            self.problems.append("fetching CSS in a <style> element")


def audit_offline(page):
    """Every reason the page could make a network request; [] means none. Judged on the
    parsed page, so it holds even where e() has defanged a URL in a text node."""
    a = _OfflineAudit()
    a.feed(page)
    a.close()
    return sorted(set(a.problems))


# --------------------------------------------------------------------------------------

def ratified_file_sha(dumps_root, ratified, fname, cur, base):
    """sha256 of one file in the ratified folder: the hash already taken when that folder is
    one of the two read for this pack, else read now. None when it cannot be read."""
    for c in (cur, base):
        if c and c["name"] == ratified:
            hit = [f for f in c["files"] if f["name"] == fname and f["present"]]
            return hit[0]["sha256"] if hit else None
    path = os.path.join(dumps_root, ratified, fname)
    if not os.path.isfile(path):
        return None
    try:
        return sha256_bytes(read_bytes(path))
    except Refusal:
        return None


def build(folder, out, baseline=None, differ=None, allow_missing_manifest=False,
          standards_dir=None):
    """Read, compare, judge, render, write. Returns (model, findings, page bytes)."""
    folder = os.path.abspath(folder)
    dumps_root = os.path.dirname(folder)
    # The standard pages sit beside the dumps directory unless told otherwise.
    standards_dir = os.path.abspath(standards_dir or os.path.dirname(dumps_root))
    if baseline and os.path.realpath(baseline) == os.path.realpath(folder):
        raise Refusal("--baseline and --folder are the same folder (%s). A self-comparison "
                      "always reads clean, which is indistinguishable from a clean cycle."
                      % folder)
    cur = read_cycle(folder, dumps_root, True, allow_missing_manifest)
    base = read_cycle(os.path.abspath(baseline), dumps_root, False, True) if baseline else None
    ratified, problem = read_ratified(dumps_root)
    diff = None
    if base:
        differ = differ or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "diff_baseline.py")
        diff = run_differ(differ, base["rows_path"], cur["rows_path"])
    pages = read_standard_pages(standards_dir, dumps_root)
    # The ratified folder's raw export and rows, as they hash NOW: every page must cite the
    # first in Ratified from and the second in its generated block. None when unreadable.
    ratified_sha = ratified_rows_sha = None
    if ratified and not problem:
        ratified_sha = ratified_file_sha(dumps_root, ratified, RAW_EXPORT, cur, base)
        ratified_rows_sha = ratified_file_sha(dumps_root, ratified, ROWS, cur, base)
    override = None
    if os.path.realpath(standards_dir) != os.path.realpath(os.path.dirname(dumps_root)):
        override = os.path.relpath(standards_dir, dumps_root).replace(os.sep, "/")
    m = build_model(cur, base, ratified, problem, diff, pages, ratified_sha,
                    ratified_rows_sha, override)
    fs = compute_findings(m)
    page = render(m, fs)
    leaks = audit_offline(page)
    if leaks:
        raise Refusal("the rendered pack could make a network request (%s). That is a defect "
                      "in this builder, not in the inputs; nothing was written."
                      % "; ".join(leaks))
    data = page.encode("utf-8")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    try:
        with open(out, "wb") as f:
            f.write(data)
    except OSError as x:
        raise Refusal("cannot write %s: %s" % (out, x))
    return m, fs, data


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--folder", required=True, help="the dated cycle folder to evidence")
    ap.add_argument("--baseline", default=None,
                    help="an earlier dated folder to compare against (normally the ratified one)")
    ap.add_argument("--out", required=True, help="where to write the HTML pack")
    ap.add_argument("--differ", default=None,
                    help="path to diff_baseline.py (default: the one beside this script)")
    ap.add_argument("--allow-missing-manifest", action="store_true",
                    help="build a pack for a folder with no collection-manifest.json; every "
                         "provenance field then reads NOT RECORDED and a finding says so")
    ap.add_argument("--standards-dir", default=None,
                    help="the folder holding the hardening-standard pages, whose approval "
                         "tables the pack shows (default: the parent of the dumps directory)")
    a = ap.parse_args(argv)
    try:
        m, fs, data = build(a.folder, a.out, a.baseline, a.differ, a.allow_missing_manifest,
                            a.standards_dir)
    except Refusal as x:
        sys.stderr.write("error: %s\n" % x)
        return 2
    if m["cur"]["manifest"] is None:
        sys.stderr.write("WARNING: %s has no %s. The pack was built, but it is NOT dated at "
                         "collection and NOT attributed; it says so in its header and as a "
                         "high-severity finding.\n" % (m["cur"]["name"], MANIFEST))
    if m["cur"]["incidents_state"] == "recorded" and m["cur"]["incidents"]:
        sys.stderr.write("WARNING: %s's %s records %s: this export is INCOMPLETE. The pack "
                         "says so in its header, in section 01 and as a high-severity "
                         "finding.\n" % (m["cur"]["name"], MANIFEST,
                                         plural(len(m["cur"]["incidents"]), "incident")))
    sev ={k: sum(1 for x in fs if x["sev"] == k) for k in ("high", "medium", "low")}
    print("wrote %s  %d bytes  sha256 %s" % (a.out, len(data), sha256_bytes(data)))
    print("inputs: %d file(s) hashed, input digest %s" % (len(m["present"]), m["digest"]))
    print("rows: %d across %d object(s)" % (len(m["rows"]), len(m["objects"])))
    for pg in m["pages"]:
        c = pg["cells"]
        print("approval: %s %s" % (pg["std_id"], (
            "version %s, approved by %s on %s, ratified from %s"
            % (c["Version"], c["Approved by"], c["Approved on"], c["Ratified from"])
            if pg["present"] and not pg["problem"] else "%s %s" % (pg["name"], pg["problem"]))))
    if m["base"]:
        print("comparison: %s -> %s, differ exit %d"
              % (m["base"]["name"], m["cur"]["name"], m["diff"]["exit"]))
    else:
        print("comparison: none (no --baseline)")
    print("findings: %d high, %d medium, %d low" % (sev["high"], sev["medium"], sev["low"]))
    for x in fs:
        print("  [%s] %s" % (x["sev"], x["title"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
