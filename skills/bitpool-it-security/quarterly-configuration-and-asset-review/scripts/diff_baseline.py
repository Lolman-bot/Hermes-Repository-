#!/usr/bin/env python3
"""Diff two hardening baselines and report what moved, in a form an auditor can read.

This is the reason the dumps are retained in the repo rather than regenerated and thrown
away. A live Intune query only ever shows today. It cannot answer "what changed since
June, and did anyone sign it off" -- and that question IS the quarterly review. Two dated
baseline-rows.json files can answer it; one cannot.

ROW CONTRACT v2 -- IDENTITY IS THE OBJECT ID, NEVER THE NAME
------------------------------------------------------------
The join key is `row_key`:

    row_key = collection|object_id|setting_id        (object_id, setting_id lowercased)

There is no name and no platform in it. A policy is identified by its Intune object id,
which survives a rename; its display name is carried as a SETTING of its own -- one
synthetic `@displayName` row per object, mode `identity`. So a rename is exactly one
visible change, on one row, and no other row's identity moves. That is the defect v1 had:
it keyed on the normalised name, so a rename re-keyed every row of the policy and handed
each one a brand-new BP- id.

WHAT IS COMPARED, AND WHAT IS NOT
---------------------------------
Only `required_value`, plus whether a row exists. Never `setting_name`, `display_value`,
`object_name`, `enforced_at` or `verify`. The labels are resolved from Microsoft's
Settings Catalog definitions for DISPLAY ONLY; if Microsoft relabels a setting, comparing
labels would manufacture a difference in a tenant where nothing changed. Relabels are
listed under "not counted" so they are visible without driving the exit code.

The classes:

    RENAMED     the @displayName row changed. ONE object event naming the old and new
                name, the object id, and how many settings were unaffected. Never also
                reported as CHANGED
    REASSIGNED  an object that crossed between the rows and meta.scope.excluded_objects,
                matched on object_id. Unassigning one Settings Catalog policy removes
                eighty rows in a single stroke; this makes it one event, not eighty.
                `reason` is why the object is excluded NOW (null once it is assigned
                again); `previous_reason` is why it was excluded in the BASELINE (null
                when it was assigned then). Exactly one of the two is set
    OBJECT REMOVED / OBJECT ADDED
                every row of an object vanished / appeared, and it was not merely
                (un)assigned. One event per object, never a wall of rows
    CHANGED     same row_key, different required_value -- the standard drifted
    REMOVED     a row gone from an object that still exists -- a control that stopped
                being enforced. Record it; never let a row vanish quietly
    ADDED       a row new to an object that already existed -- not yet ratified
    INTEGRITY   the id map broke its promise: one row_key carrying two ids across
                cycles, one id on two rows, or a retired id handed to a different row.
                Not an estate change, but loud -- a renumbered standard silently
                invalidates every prior sign-off that cited an id

A clean cycle is a finding, not the absence of one. The summary prints full counts either
way, so "no change" arrives as evidence the comparison ran rather than as a claim.

REFUSALS -- exit 2, because a convincing wrong answer is worse than none
------------------------------------------------------------------------
    * baselines from different generator MAJOR versions. v1 keyed rows on names, v2 on
      object ids; across that line every row reads as removed and re-added
    * a file that is not v2 at all, or carries no generator_version
    * a row whose row_key is not collection|object_id|setting_id built from its own fields
    * duplicate row_keys (the join would silently drop one), unless --allow-duplicate-keys
    * a baseline diffed against itself -- that always reports a perfectly clean cycle

Exit codes are the contract with whatever runs this:

    0   no differences
    1   differences found        <- expected on a normal cycle; NOT a failure
    2   error, or the comparison could not be trusted

Depends only on the documented row contract. It never imports, reads, or assumes anything
about the generator's internals -- a different generator emitting the same shape works.
Output is deterministic: same two inputs, byte-identical markdown and json. Nothing reads
the clock, and the markdown / json carry portable file labels (`2026-09-24/baseline-rows
.json`), never the absolute path they happened to be read from.

Pure stdlib. Run through WSL.

Usage:
    diff_baseline.py --baseline dumps/2026-09-24/baseline-rows.json \\
                     --current  dumps/2026-12-24/baseline-rows.json
    diff_baseline.py --baseline B --current C --format markdown -o C_DIR/diff-vs-2026-09-24.md
    diff_baseline.py --baseline B --current C --format json     -o C_DIR/diff-vs-2026-09-24.json

    # all three in one pass: text on stdout, the two records written beside it
    diff_baseline.py --baseline B --current C \\
                     --markdown-out C_DIR/diff-vs-2026-09-24.md \\
                     --json-out     C_DIR/diff-vs-2026-09-24.json
"""

import argparse
import json
import os
import re
import sys
import traceback
from pathlib import Path

DIFF_VERSION = "2.0"

# The row contract this differ implements. A file from any other major is refused.
SUPPORTED_MAJOR = 2

# The synthetic per-object row whose value is the object's display name.
NAME_SETTING_ID = "@displayName"

# Truncation for on-screen values only. The json format always carries them in full --
# a macOS plist property or a compliance rule list can run to hundreds of characters, and
# a report nobody can read is a report nobody checks.
TEXT_VALUE_WIDTH = 110
MD_VALUE_WIDTH = 200

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
VERSION_RE = re.compile(r"^\d+(\.\d+)*$")
ID_RE = re.compile(r"^BP-([A-Z]{3})-(\d{4})$")

# Contract sort order: platform, then collection, then object name, then object id, then
# the name row first, then setting id. Anything unlisted sorts after, alphabetically.
PLATFORM_ORDER = {"windows10": 0, "macos": 1, "ios": 2}
COLLECTION_ORDER = {"configurationPolicies": 0, "deviceConfigurations": 1,
                    "deviceCompliancePolicies": 2}

ROW_FIELDS = ["row_key", "id", "platform", "collection", "object_type", "object_id",
              "object_name", "setting_id", "setting_name", "required_value",
              "display_value", "mode", "enforced_at", "verify"]

# The classes that drive the exit code, in report order.
COUNTED = ["integrity", "renamed", "reassigned", "object_removed", "object_added",
           "changed", "removed", "added"]


class DiffError(Exception):
    """Anything that means the comparison cannot be trusted. Always exit 2."""


# --------------------------------------------------------------------------------------
# Loading, and refusing to produce a convincing wrong answer
# --------------------------------------------------------------------------------------

def load_doc(path, label):
    try:
        raw = Path(path).read_text(encoding="utf-8-sig")
    except OSError as e:
        raise DiffError("cannot read the %s file %s: %s" % (label, path, e))
    try:
        doc = json.loads(raw)
    except ValueError as e:
        raise DiffError("the %s file %s is not valid JSON: %s" % (label, path, e))
    if not isinstance(doc, dict) or not isinstance(doc.get("rows"), list):
        raise DiffError("%s is not a baseline (no 'rows' list). Produce it with "
                        "generate_baseline.py." % path)
    if not isinstance(doc.get("meta"), dict):
        doc["meta"] = {}
    return doc


def generator_version(doc, path):
    """(major, version string). A file that does not say which contract it follows is
    refused rather than guessed at -- the two majors disagree on what a row IS."""
    v = doc["meta"].get("generator_version")
    if not isinstance(v, str) or not VERSION_RE.match(v.strip()):
        raise DiffError(
            "%s carries no usable meta.generator_version (found %r).\n"
            "       The differ cannot tell which row contract the file follows, and will\n"
            "       not guess. Regenerate it with generate_baseline.py." % (path, v))
    v = v.strip()
    return int(v.split(".")[0]), v


def check_versions(base, curr, bpath, cpath):
    bmaj, bv = generator_version(base, bpath)
    cmaj, cv = generator_version(curr, cpath)
    if bmaj != cmaj:
        raise DiffError(
            "refusing to compare across generator major versions:\n"
            "         baseline %s is generator %s\n"
            "         current  %s is generator %s\n"
            "       A major version changes what a row's identity IS. v1 keyed each row on\n"
            "       the policy NAME; v2 keys it on the Intune object id. Compared across\n"
            "       that line, every row reads as removed and re-added, and the report is\n"
            "       noise that looks like evidence. Regenerate the older folder with the\n"
            "       current generator (run_config_cycle.py generate <date>) and diff again."
            % (bpath, bv, cpath, cv))
    if bmaj != SUPPORTED_MAJOR:
        raise DiffError(
            "both files are generator %d.x, but this differ implements row contract v%d\n"
            "       (row_key = collection|object_id|setting_id, one @displayName row per\n"
            "       object). Regenerate both folders with generator %d.x and diff again."
            % (bmaj, SUPPORTED_MAJOR, SUPPORTED_MAJOR))
    return bv, cv


def expected_row_key(row):
    return "%s|%s|%s" % (row["collection"], row["object_id"].lower(),
                         row["setting_id"].lower())


def index_rows(doc, label, allow_dupes, warnings):
    """row_key -> row, refusing anything that would make the join silently wrong.

    Two checks beyond "is it a dict":

      * row_key must be exactly collection|object_id|setting_id built from the row's own
        fields. A key built any other way -- a v1 name-based key that slipped past the
        version stamp, a hand edit -- means the join is not joining what it claims to.
      * duplicate keys. Two rows sharing one identity means the join drops one, and a
        dropped row can never be reported as REMOVED because the differ never saw it.
        That produces a report that is clean in exactly the place it should not be.
    """
    out, dupes, bad_fields, bad_keys = {}, {}, [], []
    for i, r in enumerate(doc["rows"]):
        if not isinstance(r, dict):
            bad_fields.append("row %d is not an object" % i)
            continue
        missing = [f for f in ("row_key", "collection", "object_id", "setting_id")
                   if not isinstance(r.get(f), str) or not r.get(f)]
        if "required_value" not in r:
            missing.append("required_value")
        if missing:
            bad_fields.append("row %d missing %s" % (i, ", ".join(missing)))
            continue
        want = expected_row_key(r)
        if r["row_key"] != want:
            bad_keys.append("row %d: %s  (expected %s)" % (i, r["row_key"], want))
            continue
        k = r["row_key"]
        if k in out:
            dupes.setdefault(k, []).append(r)
        else:
            out[k] = r

    if bad_fields:
        raise DiffError("%s: %d row(s) do not meet the v2 row contract:\n       %s%s"
                        % (label, len(bad_fields), "\n       ".join(bad_fields[:5]),
                           "\n       ... and %d more" % (len(bad_fields) - 5)
                           if len(bad_fields) > 5 else ""))
    if bad_keys:
        raise DiffError(
            "%s: %d row(s) carry a row_key that is not collection|object_id|setting_id\n"
            "       built from the row's own fields, so the join would not join what it\n"
            "       claims to:\n       %s%s"
            % (label, len(bad_keys), "\n       ".join(bad_keys[:5]),
               "\n       ... and %d more" % (len(bad_keys) - 5) if len(bad_keys) > 5 else ""))
    if dupes:
        n = sum(len(v) for v in dupes.values())
        if not allow_dupes:
            raise DiffError(
                "%s carries %d duplicate row_key(s) shadowing %d row(s).\n"
                "       row_key is the durable identity, so the join would silently drop\n"
                "       these and the report would look clean where it is not. Fix the\n"
                "       generator, or re-run with --allow-duplicate-keys to proceed with\n"
                "       the first occurrence of each:\n       %s"
                % (label, len(dupes), n, "\n       ".join(sorted(dupes)[:10])))
        warnings.append("%s: %d duplicate row_key(s) shadowing %d row(s); the first "
                        "occurrence of each was kept (--allow-duplicate-keys)."
                        % (label, len(dupes), n))
    return out


def is_name_row(row):
    return (row.get("setting_id") or "").lower() == NAME_SETTING_ID.lower()


def build_objects(rows_by_key, label, warnings):
    """(collection, object_id lowercased) -> the object and the row_keys it owns.

    The object's name is read from its @displayName row -- the one place v2 says the name
    lives -- and only falls back to object_name when that row is missing, which is itself
    warned about: without it, a rename cannot be seen at all.
    """
    objs = {}
    for k in sorted(rows_by_key):
        r = rows_by_key[k]
        ok = (r["collection"], r["object_id"].lower())
        o = objs.get(ok)
        if o is None:
            o = objs[ok] = {"collection": r["collection"], "object_id": r["object_id"],
                            "platform": r.get("platform"),
                            "object_type": r.get("object_type"),
                            "name": r.get("object_name"), "name_row": None,
                            "keys": set()}
        o["keys"].add(k)
        if is_name_row(r):
            o["name_row"] = k
            o["name"] = r.get("required_value")
    nameless = sorted(o["object_id"] for o in objs.values() if o["name_row"] is None)
    if nameless:
        warnings.append("%s: %d object(s) carry no @displayName row, so a rename of them "
                        "cannot be detected: %s" % (label, len(nameless), ", ".join(nameless)))
    return objs


def excluded_index(doc, label, warnings):
    """object_id (lowercased) -> meta.scope.excluded_objects entry.

    This is what tells "somebody unassigned the policy" apart from "somebody deleted the
    policy". Both make every row disappear; only one of them is a five-second fix.
    """
    out, no_id = {}, 0
    scope = doc["meta"].get("scope") or {}
    for e in scope.get("excluded_objects") or []:
        if not isinstance(e, dict):
            continue
        oid = e.get("object_id")
        if not isinstance(oid, str) or not oid:
            no_id += 1
            continue
        out[oid.lower()] = e
    if no_id:
        warnings.append("%s: %d excluded_objects entr(ies) carry no object_id and cannot be "
                        "matched for REASSIGNED" % (label, no_id))
    return out


def vkey(v):
    """Order-stable comparable form. required_value is a string under the contract, but a
    list or dict must not differ merely by key order."""
    if isinstance(v, str):
        return "s:" + v
    try:
        return "j:" + json.dumps(v, sort_keys=True, default=str)
    except (TypeError, ValueError):
        return "r:" + repr(v)


# --------------------------------------------------------------------------------------
# Ordering -- deterministic, never dict order
# --------------------------------------------------------------------------------------

def platform_rank(p):
    p = (p or "").lower()
    return (PLATFORM_ORDER.get(p, 3), p)


def collection_rank(c):
    return (COLLECTION_ORDER.get(c, 3), c or "")


def row_sort_key(r):
    return (platform_rank(r.get("platform")), collection_rank(r.get("collection")),
            (r.get("object_name") or "").casefold(), (r.get("object_id") or "").lower(),
            0 if is_name_row(r) else 1, (r.get("setting_id") or "").casefold(),
            r.get("row_key") or "")


def event_sort_key(e):
    return (platform_rank(e.get("platform")), collection_rank(e.get("collection")),
            str(e.get("name") or "").casefold(), (e.get("object_id") or "").lower())


def rowref(r):
    return {k: r.get(k) for k in ROW_FIELDS}


def platform_counts(rows_by_key):
    counts = {}
    for r in rows_by_key.values():
        per = counts.setdefault(r.get("platform") or "unknown", {})
        per[r["collection"]] = per.get(r["collection"], 0) + 1
    return counts


def stats(rows_by_key, objs, excluded):
    return {"row_count": len(rows_by_key), "object_count": len(objs),
            "excluded_count": len(excluded), "counts": platform_counts(rows_by_key)}


def meta_warnings(doc, rows_by_key, label, warnings):
    """The file's own claims about itself, checked against its rows. A mismatch means a
    hand edit or a truncated write -- not fatal, but it goes in the report body."""
    meta = doc["meta"]
    rc = meta.get("row_count")
    if isinstance(rc, int) and rc != len(doc["rows"]):
        warnings.append("%s: meta.row_count says %d but the file carries %d row(s)"
                        % (label, rc, len(doc["rows"])))
    declared = meta.get("counts")
    if isinstance(declared, dict) and declared != platform_counts(rows_by_key):
        warnings.append("%s: meta.counts does not match the per-platform counts of its "
                        "own rows" % label)
    no_id = sum(1 for r in rows_by_key.values() if not r.get("id"))
    if no_id:
        warnings.append("%s: %d row(s) carry no BP- id, so id permanence cannot be checked "
                        "for them" % (label, no_id))


# --------------------------------------------------------------------------------------
# The comparison
# --------------------------------------------------------------------------------------

def object_event(o, rows):
    keys = sorted(o["keys"], key=lambda k: row_sort_key(rows[k]))
    return {"object_id": o["object_id"], "collection": o["collection"],
            "platform": o["platform"], "object_type": o["object_type"],
            "name": o["name"], "row_count": len(keys),
            "ids": [rows[k].get("id") for k in keys if rows[k].get("id")],
            "rows": [rowref(rows[k]) for k in keys]}


def reassign_reason(e):
    """The exclusion reason of a REASSIGNED event, labelled with the side it belongs to.
    An object that became assigned carries only the reason it USED to be excluded."""
    if e.get("reason") is not None:
        return "now excluded: %s" % as_text(e["reason"])
    if e.get("previous_reason") is not None:
        return "was excluded: %s" % as_text(e["previous_reason"])
    return "excluded"


def compare(base, curr, allow_dupes=False, base_label="baseline", curr_label="current"):
    """Pure: two loaded v2 documents in, the classified differences out. Raises DiffError
    on anything that would make the result untrustworthy. Version checking is the
    caller's job (check_versions) -- it needs the paths for its message."""
    warnings = []

    b = index_rows(base, base_label, allow_dupes, warnings)
    c = index_rows(curr, curr_label, allow_dupes, warnings)
    meta_warnings(base, b, base_label, warnings)
    meta_warnings(curr, c, curr_label, warnings)
    bo = build_objects(b, base_label, warnings)
    co = build_objects(c, curr_label, warnings)
    bx = excluded_index(base, base_label, warnings)
    cx = excluded_index(curr, curr_label, warnings)

    for label, objs, x in ((base_label, bo, bx), (curr_label, co, cx)):
        both = sorted(o["object_id"] for o in objs.values() if o["object_id"].lower() in x)
        if both:
            warnings.append("%s: %d object(s) appear both in the rows and in "
                            "excluded_objects: %s" % (label, len(both), ", ".join(both)))

    # ---- object level first, so a whole-object event never decomposes into row noise ----
    reassigned, obj_removed, obj_added = [], [], []
    consumed = set()

    for ok in sorted(set(bo) - set(co)):
        o = bo[ok]
        ev = object_event(o, b)
        entry = cx.get(ok[1])
        if entry is not None:
            ev.update(direction="assigned -> unassigned",
                      reason=entry.get("reason") or "excluded",
                      previous_reason=None,
                      previous_name=o["name"],
                      name=entry.get("name") if entry.get("name") is not None else o["name"])
            reassigned.append(ev)
        else:
            obj_removed.append(ev)
        consumed |= o["keys"]

    for ok in sorted(set(co) - set(bo)):
        o = co[ok]
        ev = object_event(o, c)
        entry = bx.get(ok[1])
        if entry is not None:
            # The exclusion reason belongs to the BASELINE side: the object is assigned
            # now, so it carries no current reason. Reporting it as `reason` read as
            # "unassigned -> assigned (unassigned)" -- as if it were still unassigned.
            ev.update(direction="unassigned -> assigned",
                      reason=None,
                      previous_reason=entry.get("reason") or "excluded",
                      previous_name=entry.get("name")
                      if entry.get("name") is not None else o["name"])
            reassigned.append(ev)
        else:
            obj_added.append(ev)
        consumed |= o["keys"]

    for events in (reassigned, obj_removed, obj_added):
        events.sort(key=event_sort_key)

    # ---- renames: the @displayName row changed. ONE event, never also CHANGED. ----
    renamed = []
    for ok in sorted(set(bo) & set(co)):
        ob, oc = bo[ok], co[ok]
        if ob["name_row"] is None or oc["name_row"] is None:
            continue  # warned in build_objects
        if vkey(b[ob["name_row"]].get("required_value")) == \
                vkey(c[oc["name_row"]].get("required_value")):
            continue
        shared = (ob["keys"] & oc["keys"]) - {ob["name_row"]}
        unaffected = sum(1 for k in shared
                         if vkey(b[k].get("required_value")) == vkey(c[k].get("required_value")))
        renamed.append({
            "object_id": oc["object_id"], "collection": oc["collection"],
            "platform": oc["platform"], "object_type": oc["object_type"],
            "row_key": oc["name_row"], "id": c[oc["name_row"]].get("id"),
            "from": ob["name"], "to": oc["name"],
            "total_settings": len(oc["keys"]) - 1,
            "unaffected_settings": unaffected,
            "changed_settings": len(shared) - unaffected,
            "added_settings": len(oc["keys"] - ob["keys"]),
            "removed_settings": len(ob["keys"] - oc["keys"]),
            # The whole point of v2: a rename re-keys nothing, so no id may move. Anything
            # but zero here is also an INTEGRITY finding.
            "ids_moved": sum(1 for k in ob["keys"] & oc["keys"]
                             if b[k].get("id") != c[k].get("id")),
        })
    renamed.sort(key=lambda e: event_sort_key(dict(e, name=e["to"])))

    # ---- row-level residue ----
    added = [c[k] for k in sorted(set(c) - set(b) - consumed, key=lambda k: row_sort_key(c[k]))]
    removed = [b[k] for k in sorted(set(b) - set(c) - consumed, key=lambda k: row_sort_key(b[k]))]

    changed, display_only, mode_drift = [], [], []
    unchanged = 0
    for k in sorted(set(b) & set(c), key=lambda k: row_sort_key(c[k])):
        rb, rc = b[k], c[k]
        same = vkey(rb.get("required_value")) == vkey(rc.get("required_value"))
        if rb.get("mode") != rc.get("mode"):
            mode_drift.append(k)
        if is_name_row(rc):
            if same:
                unchanged += 1
            continue  # a differing name row is the RENAMED event above -- never CHANGED
        if same:
            unchanged += 1
            if (rb.get("display_value") != rc.get("display_value")
                    or rb.get("setting_name") != rc.get("setting_name")):
                display_only.append({
                    "row_key": k, "id": rc.get("id"), "setting_id": rc.get("setting_id"),
                    "object_name": rc.get("object_name"),
                    "required_value": rc.get("required_value"),
                    "from_setting_name": rb.get("setting_name"),
                    "to_setting_name": rc.get("setting_name"),
                    "from_display": rb.get("display_value"),
                    "to_display": rc.get("display_value")})
            continue
        changed.append({
            "row_key": k, "id": rc.get("id"), "platform": rc.get("platform"),
            "collection": rc.get("collection"), "object_id": rc.get("object_id"),
            "object_name": rc.get("object_name"), "setting_id": rc.get("setting_id"),
            "setting_name": rc.get("setting_name"),
            "from": rb.get("required_value"), "to": rc.get("required_value"),
            "from_display": rb.get("display_value"), "to_display": rc.get("display_value"),
            "verify": rc.get("verify")})

    if mode_drift:
        warnings.append("%d row(s) changed mode under an unchanged row_key. Mode is fixed by "
                        "collection in contract v2, so this is a generator-semantics change, "
                        "not an estate change, and it is not counted: %s"
                        % (len(mode_drift), ", ".join(mode_drift[:5])))

    # ---- integrity: the id map is supposed to be permanent ----
    integrity = []
    for k in sorted(set(b) & set(c)):
        ib, ic = b[k].get("id"), c[k].get("id")
        if ib and ic and ib != ic:
            integrity.append({"kind": "id changed for an unchanged row_key", "row_key": k,
                              "baseline_id": ib, "current_id": ic,
                              "detail": "the id map is supposed to be permanent"})
    for label, rows, side in ((base_label, b, "baseline"), (curr_label, c, "current")):
        seen = {}
        for k in sorted(rows):
            i = rows[k].get("id")
            if not i:
                continue
            if i in seen:
                integrity.append({"kind": "id used on two rows", "row_key": k,
                                  "baseline_id": i if side == "baseline" else None,
                                  "current_id": i if side == "current" else None,
                                  "detail": "%s: also on %s" % (label, seen[i])})
            else:
                seen[i] = k
    base_ids = {}
    for k in sorted(b):
        if b[k].get("id"):
            base_ids.setdefault(b[k]["id"], k)
    for k in sorted(c):
        i = c[k].get("id")
        if i and i in base_ids and base_ids[i] != k:
            integrity.append({"kind": "id reused for a different row_key", "row_key": k,
                              "baseline_id": i, "current_id": i,
                              "detail": "baseline had %s on %s" % (i, base_ids[i])})

    # ---- not counted: churn among objects that were never in scope ----
    b_all = {ok[1] for ok in bo} | set(bx)
    c_all = {ok[1] for ok in co} | set(cx)

    def excl(entry):
        return {k: entry.get(k) for k in ("collection", "object_id", "name", "platform",
                                          "reason")}

    def excl_sort(e):
        return (collection_rank(e.get("collection")), str(e.get("name") or "").casefold(),
                (e.get("object_id") or "").lower())

    excluded_added = sorted((excl(cx[o]) for o in cx if o not in b_all), key=excl_sort)
    excluded_removed = sorted((excl(bx[o]) for o in bx if o not in c_all), key=excl_sort)

    return {
        "warnings": warnings,
        "integrity": integrity, "renamed": renamed, "reassigned": reassigned,
        "object_removed": obj_removed, "object_added": obj_added,
        "changed": changed, "removed": removed, "added": added,
        "display_only": display_only,
        "excluded_added": excluded_added, "excluded_removed": excluded_removed,
        "unchanged_rows": unchanged,
        "baseline_stats": stats(b, bo, bx),
        "current_stats": stats(c, co, cx),
    }


def difference_count(d):
    """What drives the exit code. Each object event counts once, however many rows it
    carries. Integrity defects count -- a renumbered id map is not an estate change, but
    it is emphatically not 'no differences' either."""
    return sum(len(d[k]) for k in COUNTED)


# --------------------------------------------------------------------------------------
# Provenance
# --------------------------------------------------------------------------------------

def file_label(path):
    """Portable name for a baseline file: `2026-09-24/baseline-rows.json` when it sits in a
    dated cycle folder, else its basename. Never the absolute path -- the markdown and
    json are committed records and must not depend on whose machine made them."""
    p = Path(os.path.abspath(path))
    return "%s/%s" % (p.parent.name, p.name) if DATE_RE.match(p.parent.name) else p.name


def cycle_label(path, doc, override):
    if override:
        return override
    parent = Path(os.path.abspath(path)).parent.name
    if DATE_RE.match(parent):
        return parent
    ga = doc["meta"].get("generated_at")
    if isinstance(ga, str) and DATE_RE.match(ga[:10]):
        return ga[:10]
    return "unknown"


def side_info(path, doc, label_override, st):
    m = doc["meta"]
    info = {"path": file_label(path), "date": cycle_label(path, doc, label_override),
            "generator_version": m.get("generator_version"),
            "generated_at": m.get("generated_at"),
            "source_sha256": m.get("source_sha256"),
            "definitions_sha256": m.get("definitions_sha256")}
    info.update(st)
    return info


# --------------------------------------------------------------------------------------
# Rendering helpers
# --------------------------------------------------------------------------------------

def as_text(v):
    if v is None:
        return ""
    return v if isinstance(v, str) else json.dumps(v, sort_keys=True)


def truncate(s, width):
    return s if len(s) <= width else s[:width - 3] + "..."


def short(v, width=TEXT_VALUE_WIDTH):
    return truncate(re.sub(r"\s+", " ", as_text(v)), width)


def shown(display, raw, width=TEXT_VALUE_WIDTH):
    """Human label first, raw value beside it whenever they differ -- the raw value is
    what was compared, so it is never hidden behind the label."""
    r = short(raw, width)
    if display is None or as_text(display) == as_text(raw):
        return r
    return "%s  [raw %s]" % (short(display, width), r)


def id_ranges(ids):
    """['BP-WIN-0001', 'BP-WIN-0002', 'BP-WIN-0003'] -> 'BP-WIN-0001 to BP-WIN-0003'.

    A fresh map hands ids out in reading order, so one object's ids are nearly always a
    single run. Anything that does not look like a BP- id is listed as it is."""
    groups, other = {}, []
    for i in ids:
        m = ID_RE.match(i or "")
        if m:
            groups.setdefault(m.group(1), set()).add(int(m.group(2)))
        elif i:
            other.append(i)
    parts = []
    for prefix in sorted(groups):
        nums = sorted(groups[prefix])
        start = prev = nums[0]
        for n in nums[1:] + [None]:
            if n is not None and n == prev + 1:
                prev = n
                continue
            a, z = "BP-%s-%04d" % (prefix, start), "BP-%s-%04d" % (prefix, prev)
            parts.append(a if start == prev else "%s to %s" % (a, z))
            if n is not None:
                start = prev = n
    return ", ".join(parts + sorted(other)) or "-"


def count_keys(bi, ci):
    pairs = set()
    for counts in (bi["counts"], ci["counts"]):
        for p in counts:
            for col in counts[p]:
                pairs.add((p, col))
    return sorted(pairs, key=lambda pc: (platform_rank(pc[0]), collection_rank(pc[1])))


# --------------------------------------------------------------------------------------
# Text
# --------------------------------------------------------------------------------------

def summary_lines(bi, ci, d):
    return [
        "  SUMMARY  renamed=%d reassigned=%d objects_removed=%d objects_added=%d"
        % (len(d["renamed"]), len(d["reassigned"]), len(d["object_removed"]),
           len(d["object_added"])),
        "           changed=%d removed=%d added=%d integrity=%d"
        % (len(d["changed"]), len(d["removed"]), len(d["added"]), len(d["integrity"])),
        "           total differences: %d" % difference_count(d),
        "           rows %d -> %d (%+d), %d unchanged; objects %d -> %d; excluded %d -> %d"
        % (bi["row_count"], ci["row_count"], ci["row_count"] - bi["row_count"],
           d["unchanged_rows"], bi["object_count"], ci["object_count"],
           bi["excluded_count"], ci["excluded_count"]),
        "           not counted: display-only relabels=%d, never-assigned objects +%d/-%d"
        % (len(d["display_only"]), len(d["excluded_added"]), len(d["excluded_removed"])),
    ]


def render_text(bi, ci, d, bpath, cpath):
    o = [""]
    w = o.append
    w("Intune hardening baseline diff (row contract v%d)" % SUPPORTED_MAJOR)
    w("=" * 78)
    for label, i, path in (("baseline", bi, bpath), ("current ", ci, cpath)):
        w("  %s  %-10s  rows=%d objects=%d excluded=%d  generator=%s"
          % (label, i["date"], i["row_count"], i["object_count"], i["excluded_count"],
             i["generator_version"]))
        w("            generated=%s  source sha256=%s"
          % (i["generated_at"] or "?", (i["source_sha256"] or "?")[:16]))
        w("            file=%s" % path)
    w("")
    for line in summary_lines(bi, ci, d):
        w(line)
    w("")

    w("  ROWS BY PLATFORM                              baseline  current   delta")
    for p, col in count_keys(bi, ci):
        nb = bi["counts"].get(p, {}).get(col, 0)
        nc = ci["counts"].get(p, {}).get(col, 0)
        w("    %-10s %-30s %8d %8d %+7d" % (p, col, nb, nc, nc - nb))
    w("")

    for x in d["warnings"]:
        w("  !! %s" % x)
    if d["warnings"]:
        w("")

    def block(title, rows, body):
        w("%s -- %d" % (title, len(rows)))
        if not rows:
            w("  none")
        for r in rows:
            for line in body(r):
                w("  " + line)
        w("")

    block("INTEGRITY (id map defect -- not an estate change)", d["integrity"],
          lambda e: ["! %-38s %s" % (e["kind"], e["row_key"]),
                     "      %s -> %s   (%s)" % (e["baseline_id"], e["current_id"], e["detail"])])

    block("RENAMED (the name is a diffed setting -- one event per object)", d["renamed"],
          lambda e: ["~ %-9s %-26s %s" % (e["platform"] or "-", e["collection"], e["object_id"]),
                     "      from: %s" % short(e["from"]),
                     "      to:   %s" % short(e["to"]),
                     "      %d of %d setting(s) unaffected; %d changed, %d added, %d removed; "
                     "%d id(s) moved"
                     % (e["unaffected_settings"], e["total_settings"], e["changed_settings"],
                        e["added_settings"], e["removed_settings"], e["ids_moved"])])

    block("REASSIGNED (crossed the assigned boundary -- one event, not one per row)",
          d["reassigned"],
          lambda e: ["~ %-9s %-26s %s" % (e["platform"] or "-", e["collection"], short(e["name"])),
                     "      %s  (%s)  %s -- %d row(s): %s"
                     % (e["direction"], reassign_reason(e), e["object_id"], e["row_count"],
                        id_ranges(e["ids"]))]
          + (["      name was: %s" % short(e["previous_name"])]
             if as_text(e["previous_name"]) != as_text(e["name"]) else []))

    block("OBJECT REMOVED (gone, and not recorded as unassigned)", d["object_removed"],
          lambda e: ["- %-9s %-26s %s" % (e["platform"] or "-", e["collection"], short(e["name"])),
                     "      %s -- %d row(s): %s" % (e["object_id"], e["row_count"],
                                                    id_ranges(e["ids"]))])

    block("OBJECT ADDED (new object, not previously unassigned)", d["object_added"],
          lambda e: ["+ %-9s %-26s %s" % (e["platform"] or "-", e["collection"], short(e["name"])),
                     "      %s -- %d row(s): %s" % (e["object_id"], e["row_count"],
                                                    id_ranges(e["ids"]))])

    block("CHANGED (required_value drifted)", d["changed"],
          lambda e: ["~ %-11s %-9s %s" % (e["id"] or "-", e["platform"] or "-",
                                          short(e["object_name"])),
                     "      %s  (%s)" % (short(e["setting_name"]), e["setting_id"]),
                     "      from: %s" % shown(e["from_display"], e["from"]),
                     "      to:   %s" % shown(e["to_display"], e["to"])])

    block("REMOVED (control no longer enforced -- record it)", d["removed"],
          lambda r: ["- %-11s %-9s %s" % (r.get("id") or "-", r.get("platform") or "-",
                                          short(r.get("object_name"))),
                     "      %s  (%s)" % (short(r.get("setting_name")), r.get("setting_id")),
                     "      was: %s" % shown(r.get("display_value"), r.get("required_value"))])

    block("ADDED (setting not yet ratified)", d["added"],
          lambda r: ["+ %-11s %-9s %s" % (r.get("id") or "-", r.get("platform") or "-",
                                          short(r.get("object_name"))),
                     "      %s  (%s)" % (short(r.get("setting_name")), r.get("setting_id")),
                     "      now: %s" % shown(r.get("display_value"), r.get("required_value"))])

    block("NOT COUNTED -- display-only relabels (raw value unchanged)", d["display_only"],
          lambda e: ["  %-11s %s" % (e["id"] or "-", e["setting_id"]),
                     "      label: %s -> %s" % (short(e["from_setting_name"]),
                                                short(e["to_setting_name"])),
                     "      value: %s -> %s" % (short(e["from_display"]),
                                                short(e["to_display"]))])

    never = ([("+", e) for e in d["excluded_added"]] + [("-", e) for e in d["excluded_removed"]])
    block("NOT COUNTED -- never-assigned objects appeared (+) or went (-)", never,
          lambda pe: ["%s %-26s %s  (%s)" % (pe[0], pe[1].get("collection"),
                                             short(pe[1].get("name")), pe[1].get("object_id"))])

    if difference_count(d) == 0:
        w("No differences this cycle. That is the evidence the review ran -- record the")
        w("counts above in full, alongside both file paths and both source_sha256 values,")
        w("rather than writing \"no change\".")
        w("")
    return "\n".join(o)


# --------------------------------------------------------------------------------------
# Markdown -- a committed Record in the dated folder
# --------------------------------------------------------------------------------------

# Every value in a cell is untrusted text: policy names are typed by whoever administers
# Intune. Escape markdown AND html, so a name cannot become a link, a script tag, or an
# extra table column. `&<>` become entities; the markdown punctuation is backslashed.
# An underscore BETWEEN two alphanumerics cannot open emphasis in GFM, so only edge
# underscores are escaped -- an unresolved label such as device_vendor_msft_... stays
# readable in the raw file.
MD_ESCAPE = str.maketrans({"\\": "\\\\", "`": "\\`", "*": "\\*", "[": "\\[", "]": "\\]",
                           "|": "\\|", "~": "\\~", "&": "&amp;", "<": "&lt;", ">": "&gt;"})
MD_EDGE_UNDERSCORE = re.compile(r"(?<![A-Za-z0-9])_|_(?![A-Za-z0-9])")


def md_text(v, width=MD_VALUE_WIDTH):
    s = truncate(re.sub(r"\s+", " ", as_text(v)).strip(), width)
    return MD_EDGE_UNDERSCORE.sub(r"\\_", s.translate(MD_ESCAPE))


def md_code(v, width=MD_VALUE_WIDTH):
    """An inline code span that survives any content. Code spans render literally, so
    html inside one is inert; the fence is one backtick longer than the longest run in the
    value, and a pipe is backslashed because GFM splits table cells before it parses
    inline code."""
    s = truncate(re.sub(r"[\r\n]+", " ", as_text(v)), width)
    if s == "":
        return "_(empty)_"
    s = s.replace("|", "\\|")
    run = max([len(m) for m in re.findall(r"`+", s)] or [0])
    fence = "`" * (run + 1)
    pad = " " if (s.startswith("`") or s.endswith("`")) else ""
    return "%s%s%s%s%s" % (fence, pad, s, pad, fence)


def md_value(display, raw):
    if display is None or as_text(display) == as_text(raw):
        return md_code(raw)
    return "%s (%s)" % (md_text(display), md_code(raw))


def yq(s):
    """A YAML double-quoted scalar. JSON string syntax is valid YAML, and it means no
    label -- however odd -- can break the frontmatter."""
    return json.dumps(s, ensure_ascii=True)


def md_frontmatter(bi, ci, d):
    cur, base = ci["date"], bi["date"]
    last = cur if DATE_RE.match(cur) else (ci["generated_at"] or "")[:10]
    lines = [
        "---",
        "type: Record",
        "title: %s" % yq("Configuration baseline diff %s against %s" % (cur, base)),
        "description: %s" % yq(
            "Row-level comparison of the Intune configuration baseline collected %s against "
            "%s. %d counted difference(s). Generated by diff_baseline.py; regenerate, do "
            "not edit." % (cur, base, difference_count(d))),
        "audience:",
        "  - security-team",
        "  - it-team",
        "  - auditors",
        "  - ai-agents",
    ]
    if DATE_RE.match(last):
        lines.append("last_reviewed: %s" % last)
    lines += [
        "status: active",
        "doc_type: record",
        "sources:",
        "  - internal",
        "  - drata:DCF-12",
        "keywords:",
        "  - configuration-hardening",
        "  - baseline-diff",
        "  - intune",
        "related:",
        "  - README.md",
    ]
    if DATE_RE.match(base):
        lines.append("  - ../%s/README.md" % base)
    lines += [
        "  - ../../hardening-standard-windows-endpoints.md",
        "  - ../../hardening-standard-macos-endpoints.md",
        "  - ../../hardening-standard-ios-endpoints.md",
        "iso27001_controls:",
        '  - "8.9"',
        "drata_controls:",
        "  - DCF-12",
        "risk_level: high",
        "requires_admin: false",
        "---",
    ]
    return lines


def render_markdown(bi, ci, d):
    o = md_frontmatter(bi, ci, d)
    w = o.append
    n = difference_count(d)
    w("")
    w("# Configuration baseline diff %s against %s" % (md_text(ci["date"]), md_text(bi["date"])))
    w("")
    w("> Generated by `diff_baseline.py` from the two `baseline-rows.json` files below. "
      "Regenerate it rather than edit it. Only `required_value` and row presence are "
      "compared; labels are for reading. Every counted difference takes exactly one "
      "disposition in the quarterly review: A rationale, B risk, or C gap.")
    w("")
    w("## Provenance")
    w("")
    w("| | Cycle | Rows | Objects | Excluded | Generator | Generated at | Source dump sha256 "
      "| File |")
    w("| --- | --- | ---: | ---: | ---: | --- | --- | --- | --- |")
    for label, i in (("Baseline", bi), ("Current", ci)):
        w("| **%s** | %s | %d | %d | %d | %s | %s | %s | %s |"
          % (label, md_text(i["date"]), i["row_count"], i["object_count"],
             i["excluded_count"], md_text(i["generator_version"]),
             md_text(i["generated_at"] or "?"), md_code((i["source_sha256"] or "?")[:16]),
             md_code(i["path"])))
    w("")
    w("## Summary")
    w("")
    w("| Class | Count |")
    w("| --- | ---: |")
    for k, lbl in (("integrity", "Integrity defects (id map)"),
                   ("renamed", "Objects renamed"),
                   ("reassigned", "Objects reassigned (assigned / unassigned)"),
                   ("object_removed", "Objects removed outright"),
                   ("object_added", "Objects added outright"),
                   ("changed", "Settings changed"),
                   ("removed", "Settings removed"),
                   ("added", "Settings added")):
        w("| %s | %d |" % (lbl, len(d[k])))
    w("| **Total counted differences** | **%d** |" % n)
    w("")
    w("Rows %d to %d (%+d), %d unchanged. Objects %d to %d. Excluded %d to %d. Not counted: "
      "%d display-only relabel(s); %d never-assigned object(s) appeared and %d went."
      % (bi["row_count"], ci["row_count"], ci["row_count"] - bi["row_count"],
         d["unchanged_rows"], bi["object_count"], ci["object_count"],
         bi["excluded_count"], ci["excluded_count"], len(d["display_only"]),
         len(d["excluded_added"]), len(d["excluded_removed"])))
    w("")
    w("| Platform | Collection | Baseline rows | Current rows | Delta |")
    w("| --- | --- | ---: | ---: | ---: |")
    for p, col in count_keys(bi, ci):
        nb = bi["counts"].get(p, {}).get(col, 0)
        nc = ci["counts"].get(p, {}).get(col, 0)
        w("| %s | %s | %d | %d | %+d |" % (md_text(p), md_code(col), nb, nc, nc - nb))
    w("")

    if d["warnings"]:
        w("## Warnings")
        w("")
        for x in d["warnings"]:
            w("- %s" % md_text(x, 2000))
        w("")

    def table(title, rows, head, body):
        w("## %s (%d)" % (title, len(rows)))
        w("")
        if not rows:
            w("None.")
            w("")
            return
        w("| " + " | ".join(head) + " |")
        w("| " + " | ".join(["---"] * len(head)) + " |")
        for r in rows:
            w("| " + " | ".join(body(r)) + " |")
        w("")

    table("Integrity defects", d["integrity"],
          ["Kind", "row_key", "Baseline id", "Current id", "Detail"],
          lambda e: [md_text(e["kind"]), md_code(e["row_key"]), md_code(e["baseline_id"] or "-"),
                     md_code(e["current_id"] or "-"), md_text(e["detail"])])

    table("Objects renamed", d["renamed"],
          ["ID", "Object id", "Collection", "Old name", "New name", "Settings unaffected",
           "ids moved"],
          lambda e: [md_code(e["id"] or "-"), md_code(e["object_id"]), md_code(e["collection"]),
                     md_text(e["from"]), md_text(e["to"]),
                     "%d of %d" % (e["unaffected_settings"], e["total_settings"]),
                     str(e["ids_moved"])])

    table("Objects reassigned", d["reassigned"],
          ["Object", "Object id", "Collection", "Platform", "Direction", "Exclusion reason",
           "Rows", "IDs"],
          lambda e: [md_text(e["name"]) + (
                         " (was %s)" % md_text(e["previous_name"])
                         if as_text(e["previous_name"]) != as_text(e["name"]) else ""),
                     md_code(e["object_id"]), md_code(e["collection"]),
                     md_text(e["platform"] or "-"),
                     md_text(e["direction"].replace(" -> ", " to ")),
                     md_text(reassign_reason(e)), str(e["row_count"]),
                     md_text(id_ranges(e["ids"]))])

    for key, title in (("object_removed", "Objects removed outright"),
                       ("object_added", "Objects added outright")):
        table(title, d[key],
              ["Object", "Object id", "Collection", "Platform", "Rows", "IDs"],
              lambda e: [md_text(e["name"]), md_code(e["object_id"]), md_code(e["collection"]),
                         md_text(e["platform"] or "-"), str(e["row_count"]),
                         md_text(id_ranges(e["ids"]))])

    table("Settings changed", d["changed"],
          ["ID", "Object", "Setting", "Was", "Now", "Verify"],
          lambda e: [md_code(e["id"] or "-"), md_text(e["object_name"]),
                     md_text(e["setting_name"]), md_value(e["from_display"], e["from"]),
                     md_value(e["to_display"], e["to"]), md_code(e["setting_id"])])

    for key, title, col in (("removed", "Settings removed", "Was"),
                            ("added", "Settings added", "Now")):
        table(title, d[key], ["ID", "Object", "Setting", col, "Verify"],
              lambda r: [md_code(r.get("id") or "-"), md_text(r.get("object_name")),
                         md_text(r.get("setting_name")),
                         md_value(r.get("display_value"), r.get("required_value")),
                         md_code(r.get("setting_id"))])

    table("Not counted: display-only relabels", d["display_only"],
          ["ID", "Setting id", "Label was", "Label now", "Value label was", "Value label now"],
          lambda e: [md_code(e["id"] or "-"), md_code(e["setting_id"]),
                     md_text(e["from_setting_name"]), md_text(e["to_setting_name"]),
                     md_text(e["from_display"]), md_text(e["to_display"])])

    never = ([("appeared", e) for e in d["excluded_added"]]
             + [("went", e) for e in d["excluded_removed"]])
    table("Not counted: never-assigned objects", never,
          ["Change", "Object", "Object id", "Collection", "Reason"],
          lambda pe: [pe[0], md_text(pe[1].get("name")), md_code(pe[1].get("object_id")),
                      md_code(pe[1].get("collection")), md_text(pe[1].get("reason"))])

    if n == 0:
        w("**No differences this cycle.** Both baselines were read and compared in full; the "
          "counts above are the evidence the review ran.")
        w("")
    return "\n".join(o).rstrip("\n") + "\n"


# --------------------------------------------------------------------------------------
# JSON
# --------------------------------------------------------------------------------------

def render_json(bi, ci, d):
    out = {
        "diff_version": DIFF_VERSION,
        "row_contract": SUPPORTED_MAJOR,
        "compared": "required_value and row presence only",
        "baseline": bi,
        "current": ci,
        "summary": {k: len(d[k]) for k in COUNTED},
        "difference_count": difference_count(d),
        "net_row_movement": ci["row_count"] - bi["row_count"],
        "unchanged_rows": d["unchanged_rows"],
        "warnings": d["warnings"],
        # Every TOP-LEVEL list is a counted difference class -- a consumer may render each
        # one as a class of drift. What is merely visible (relabels, never-assigned
        # objects coming and going) is therefore nested here, never at the top level.
        "not_counted": {"display_only": d["display_only"],
                        "excluded_added": d["excluded_added"],
                        "excluded_removed": d["excluded_removed"]},
        "not_counted_summary": {"display_only": len(d["display_only"]),
                                "excluded_added": len(d["excluded_added"]),
                                "excluded_removed": len(d["excluded_removed"])},
        "integrity": d["integrity"],
        "renamed": d["renamed"],
        "reassigned": d["reassigned"],
        "object_removed": d["object_removed"],
        "object_added": d["object_added"],
        "changed": d["changed"],
        "removed": [rowref(r) for r in d["removed"]],
        "added": [rowref(r) for r in d["added"]],
    }
    return json.dumps(out, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n"


# --------------------------------------------------------------------------------------

def write(path, text):
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    except OSError as e:
        raise DiffError("cannot write %s: %s" % (path, e))


def run(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--baseline", required=True,
                    help="the RATIFIED cycle's baseline-rows.json")
    ap.add_argument("--current", required=True,
                    help="this cycle's freshly generated baseline-rows.json")
    ap.add_argument("--format", choices=["text", "markdown", "json"], default="text")
    ap.add_argument("-o", "--out", default=None,
                    help="write the --format report here instead of stdout")
    ap.add_argument("--markdown-out", default=None,
                    help="also write the markdown record here (e.g. diff-vs-<date>.md)")
    ap.add_argument("--json-out", default=None,
                    help="also write the json record here (e.g. diff-vs-<date>.json)")
    ap.add_argument("--baseline-label", default=None,
                    help="cycle date shown for the baseline (default: its folder name when "
                         "that is YYYY-MM-DD, else meta.generated_at's date)")
    ap.add_argument("--current-label", default=None,
                    help="cycle date shown for the current file (same default)")
    ap.add_argument("--allow-duplicate-keys", action="store_true",
                    help="proceed when a file carries duplicate row_keys, keeping the first "
                         "occurrence of each (see the warning it prints)")
    a = ap.parse_args(argv)

    # A baseline diffed against ITSELF reports a perfectly clean cycle. That is the most
    # convincing wrong answer this tool can produce, because it looks exactly like the
    # outcome everyone wants and reads as proof the review happened. Refuse it. Identity
    # is checked on the resolved path, so a second spelling of the same path is caught.
    if os.path.realpath(a.baseline) == os.path.realpath(a.current):
        raise DiffError("refusing to diff a baseline against itself (%s).\n"
                        "       A self-diff always reports no change, which is\n"
                        "       indistinguishable from a clean cycle. Pass the RATIFIED\n"
                        "       cycle's file as --baseline." % a.baseline)

    base, curr = load_doc(a.baseline, "baseline"), load_doc(a.current, "current")
    check_versions(base, curr, a.baseline, a.current)

    d = compare(base, curr, a.allow_duplicate_keys, file_label(a.baseline),
                file_label(a.current))
    bi = side_info(a.baseline, base, a.baseline_label, d["baseline_stats"])
    ci = side_info(a.current, curr, a.current_label, d["current_stats"])

    # Same source dump, two files. Legitimate when testing; a mistake on a real cycle,
    # because the comparison is then guaranteed clean regardless of what Intune holds.
    # Warn rather than refuse -- and put it in the REPORT BODY, not just on stderr, so it
    # survives being pasted into a ticket as evidence.
    bs, cs = bi["source_sha256"], ci["source_sha256"]
    if bs and bs == cs:
        msg = ("both baselines were generated from the SAME source dump (sha256 %s) -- this "
               "comparison cannot detect a real change and is not cycle evidence." % bs[:16])
        d["warnings"].insert(0, msg)
        sys.stderr.write("warning: %s\n" % msg)

    renderers = {"text": lambda: render_text(bi, ci, d, a.baseline, a.current),
                 "markdown": lambda: render_markdown(bi, ci, d),
                 "json": lambda: render_json(bi, ci, d)}
    n = difference_count(d)

    for fmt, path in (("markdown", a.markdown_out), ("json", a.json_out)):
        if path:
            write(path, renderers[fmt]())
            sys.stderr.write("wrote %s (%s)\n" % (path, fmt))

    report = renderers[a.format]()
    if not report.endswith("\n"):
        report += "\n"
    if a.out:
        write(a.out, report)
        # This one-liner is all you see when writing to a file, so it names every class.
        print("wrote %s (%s) -- %d difference(s): renamed=%d reassigned=%d "
              "objects_removed=%d objects_added=%d changed=%d removed=%d added=%d "
              "integrity=%d"
              % (a.out, a.format, n, len(d["renamed"]), len(d["reassigned"]),
                 len(d["object_removed"]), len(d["object_added"]), len(d["changed"]),
                 len(d["removed"]), len(d["added"]), len(d["integrity"])))
    else:
        sys.stdout.write(report)
    return 1 if n else 0


def main(argv=None):
    # Policy names are free text and routinely non-ASCII. Under a C / POSIX locale a
    # print would raise UnicodeEncodeError halfway through the report -- so the report
    # is always UTF-8, which is also what every caller decodes it as.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    try:
        return run(argv)
    except DiffError as e:
        sys.stderr.write("error: %s\n" % e)
        return 2
    except Exception:  # noqa: BLE001 -- deliberate: see below
        # An uncaught exception makes Python exit 1, and 1 MEANS "differences found" --
        # a crash would read as an ordinary cycle with drift. Anything unexpected is an
        # untrusted comparison, so it is 2, with the traceback for whoever has to fix it.
        traceback.print_exc()
        sys.stderr.write("error: the comparison did not complete, so no part of it can be "
                         "trusted (exit 2).\n")
        return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(2)
