#!/usr/bin/env python3
"""Tests for diff_baseline.py -- the properties the quarterly review stands on.

Like the generator's tests, these are not coverage tests. Each one guards a way the diff
could go wrong QUIETLY -- still run, still exit, still print a tidy report, and be wrong:

    rename is one event   a renamed policy must read as ONE rename, with zero CHANGED rows
                          and zero ids moved. Anything else and a typo fix in the Intune
                          UI buries the real change under a wall of false churn.
    rollups               a whole object appearing, vanishing, or crossing the assigned
                          boundary is ONE event, not one per row.
    reassignment by id    REASSIGNED is matched on object_id, never on name -- a
                          different object that happens to share a name is not the same
                          policy being unassigned.
    labels are not diffed a Microsoft relabel (display_value, setting_name) must produce
                          NO difference; only required_value is compared.
    refusals              cross-major baselines, malformed keys, duplicates and a
                          self-diff all exit 2, because each yields a convincing wrong
                          answer.
    clean is evidence     a no-change run exits 0 AND prints full counts.
    untrusted text        a policy name cannot inject html, a link or a table column
                          into the markdown record.

Fixtures are hand-built to ROW CONTRACT v2 -- nothing here imports or assumes the
generator's internals. Ids come from a test-local id map keyed on row_key and shared
between the baseline and current fixture, exactly as the real id-map.json spans cycles.
The end-to-end tests run the real generator through its CLI on the newest retained dump.
They skip only when there is no retained dump or no generator file to run. A generator that
crashes, or emits anything but 2.x rows, FAILS them -- a skip there would let a generator
regression read as "OK (skipped=N)" in this suite.

Pure stdlib. Run through WSL:
    python3 -m unittest discover -s scripts -p 'test_*.py' -v
    python3 scripts/test_diff_baseline.py
"""

import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import diff_baseline as db  # noqa: E402

DIFFER = HERE / "diff_baseline.py"
GENERATOR = HERE / "generate_baseline.py"

NAME = "@displayName"
PREFIX = {"windows10": "WIN", "macos": "MAC", "ios": "IOS"}
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


# --------------------------------------------------------------------------------------
# Contract-v2 fixture builder
# --------------------------------------------------------------------------------------

class IdMap:
    """A permanent row_key -> BP- id map, as the contract describes it: reuse existing,
    next free number per prefix for new keys, never recycle."""

    def __init__(self):
        self.ids, self.high = {}, {}

    def id_for(self, key, platform):
        if key not in self.ids:
            prefix = PREFIX.get((platform or "").lower(), "GEN")
            self.high[prefix] = self.high.get(prefix, 0) + 1
            self.ids[key] = "BP-%s-%04d" % (prefix, self.high[prefix])
        return self.ids[key]


def setting(setting_id, value, display=None, label=None):
    return {"setting_id": setting_id, "value": value, "display": display, "label": label}


def obj(name, oid, platform="windows10", collection="configurationPolicies", settings=()):
    return {"name": name, "object_id": oid, "platform": platform, "collection": collection,
            "object_type": "#microsoft.graph.%s" % collection, "settings": list(settings)}


def rows_for(o):
    mode = "compliance" if o["collection"] == "deviceCompliancePolicies" else "enforced"
    items = [(NAME, o["name"], o["name"], "Policy name", "identity")]
    for s in o["settings"]:
        items.append((s["setting_id"], s["value"],
                      s["display"] if s["display"] is not None else s["value"],
                      s["label"] if s["label"] is not None else s["setting_id"], mode))
    out = []
    for sid, raw, display, label, mode_ in items:
        out.append({
            "row_key": "%s|%s|%s" % (o["collection"], o["object_id"].lower(), sid.lower()),
            "platform": o["platform"],
            "collection": o["collection"],
            "object_type": o["object_type"],
            "object_id": o["object_id"],
            "object_name": o["name"],
            "setting_id": sid,
            "setting_name": label,
            "required_value": raw,
            "display_value": display,
            "mode": mode_,
            "enforced_at": "Intune > %s > %s" % (o["collection"], o["name"]),
            "verify": "$.%s[?(@.id=='%s')].%s" % (o["collection"], o["object_id"], sid),
        })
    return out


def build_doc(objects, id_map, excluded=(), version="2.0",
              generated_at="2026-09-24T00:00:00Z", source_sha256=None):
    rows = [r for o in objects for r in rows_for(o)]
    rows.sort(key=db.row_sort_key)
    for r in rows:  # a fresh map assigns in reading order, as the contract requires
        r["id"] = id_map.id_for(r["row_key"], r["platform"])
    counts = {}
    for r in rows:
        per = counts.setdefault(r["platform"], {})
        per[r["collection"]] = per.get(r["collection"], 0) + 1
    return {
        "meta": {
            "generator_version": version,
            "generated_from": "intune-config-export.json",
            "generated_at": generated_at,
            "source_sha256": source_sha256 or hashlib.sha256(generated_at.encode()).hexdigest(),
            "definitions_sha256": None,
            "display_resolution": {"mode": "none", "resolved": 0, "unresolved": 0},
            "row_count": len(rows),
            "counts": counts,
            "scope": {"assigned_only": True,
                      "excluded_objects": [dict(e) for e in excluded],
                      "assignment_disagreements": []},
        },
        "rows": rows,
    }


WIN_POLICY = "AAAAAAAA-0000-4000-8000-000000000001"
MAC_POLICY = "aaaaaaaa-0000-4000-8000-000000000002"
WIN_CONFIG = "aaaaaaaa-0000-4000-8000-000000000003"
WIN_COMPLY = "aaaaaaaa-0000-4000-8000-000000000004"
DORMANT = "aaaaaaaa-0000-4000-8000-000000000005"
NEWCOMER = "aaaaaaaa-0000-4000-8000-000000000006"


def estate():
    """A small tenant: two Settings Catalog policies, one property-bag configuration and
    one compliance policy assigned, one policy deliberately unassigned."""
    return [
        obj("Default Defender Windows", WIN_POLICY, "windows10", "configurationPolicies", [
            setting("device_vendor_msft_policy_config_defender_allowrealtimemonitoring",
                    "device_vendor_msft_policy_config_defender_allowrealtimemonitoring_1",
                    "Allowed", "Allow Realtime Monitoring"),
            setting("device_vendor_msft_policy_config_defender_allowcloudprotection",
                    "device_vendor_msft_policy_config_defender_allowcloudprotection_1",
                    "Allowed", "Allow Cloud Protection"),
            setting("device_vendor_msft_policy_config_defender_puaprotection",
                    "device_vendor_msft_policy_config_defender_puaprotection_1",
                    "PUA Protection on", "PUA Protection"),
        ]),
        obj("Defualt FileVault macOS", MAC_POLICY, "macOS", "configurationPolicies", [
            setting("com.apple.mcx.filevault2_enable", "com.apple.mcx.filevault2_enable_0",
                    "On", "Enable"),
            setting("com.apple.mcx.filevault2_defer", "com.apple.mcx.filevault2_defer_true",
                    "True", "Defer"),
        ]),
        obj("Windows Device Restrictions", WIN_CONFIG, "windows10", "deviceConfigurations", [
            setting("passwordRequired", "true"),
            setting("passwordMinimumLength", "12"),
        ]),
        obj("Windows Compliance", WIN_COMPLY, "windows10", "deviceCompliancePolicies", [
            setting("osMinimumVersion", "10.0.19045"),
            setting("bitLockerEnabled", "true"),
        ]),
    ]


EXCLUDED = [{"collection": "configurationPolicies", "object_id": DORMANT,
             "name": "TROUBLESHOOTING Disable all firewalls", "platform": "windows10",
             "reason": "unassigned"}]

TOTAL_ROWS = 4 + 3 + 3 + 3   # settings + one name row per object


def find(objects, oid):
    return [o for o in objects if o["object_id"] == oid][0]


def pair(mutate=None, base_excluded=EXCLUDED, curr_excluded=EXCLUDED, **curr_kw):
    """Baseline from estate(); current from a mutated deep copy. One id map spans both."""
    id_map = IdMap()
    base_objs = estate()
    base = build_doc(base_objs, id_map, base_excluded)
    curr_objs = copy.deepcopy(base_objs)
    curr_excl = copy.deepcopy(list(curr_excluded))
    if mutate:
        mutate(curr_objs, curr_excl)
    curr = build_doc(curr_objs, id_map, curr_excl, generated_at="2026-12-24T00:00:00Z",
                     **curr_kw)
    return base, curr


def diff(base, curr):
    return db.compare(copy.deepcopy(base), copy.deepcopy(curr))


def counted(d):
    return {k: len(d[k]) for k in db.COUNTED}


ZERO = {k: 0 for k in db.COUNTED}


def expect(**nonzero):
    out = dict(ZERO)
    out.update(nonzero)
    return out


def ids_by_key(doc):
    return {r["row_key"]: r["id"] for r in doc["rows"]}


class CliCase(unittest.TestCase):
    """Writes fixtures into dated folders in a temp dir and runs the differ's CLI."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def place(self, doc, date):
        path = self.tmp / date / "baseline-rows.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        return path

    def run_differ(self, base, curr, *args, base_date="2026-09-24", curr_date="2026-12-24"):
        bp = base if isinstance(base, Path) else self.place(base, base_date)
        cp = curr if isinstance(curr, Path) else self.place(curr, curr_date)
        return subprocess.run([sys.executable, str(DIFFER), "--baseline", str(bp),
                               "--current", str(cp)] + list(args),
                              capture_output=True, text=True, env=ENV)

    def run_json(self, base, curr):
        p = self.run_differ(base, curr, "--format", "json")
        self.assertIn(p.returncode, (0, 1), p.stderr)
        return p.returncode, json.loads(p.stdout)


# --------------------------------------------------------------------------------------
# No change -- clean is evidence, not silence
# --------------------------------------------------------------------------------------

class CleanRun(CliCase):

    def test_no_change_exits_0_and_prints_full_counts(self):
        base, curr = pair()
        p = self.run_differ(base, curr)
        self.assertEqual(p.returncode, 0, p.stderr)
        out = p.stdout
        self.assertIn("renamed=0 reassigned=0 objects_removed=0 objects_added=0", out)
        self.assertIn("changed=0 removed=0 added=0 integrity=0", out)
        self.assertIn("total differences: 0", out)
        self.assertIn("rows %d -> %d (+0), %d unchanged; objects 4 -> 4; excluded 1 -> 1"
                      % (TOTAL_ROWS, TOTAL_ROWS, TOTAL_ROWS), out)
        # Per-platform counts for both sides -- the evidence the comparison covered
        # everything, not a bare "no change".
        self.assertRegex(out, r"windows10\s+configurationPolicies\s+4\s+4\s+\+0")
        self.assertRegex(out, r"macOS\s+configurationPolicies\s+3\s+3\s+\+0")
        self.assertRegex(out, r"windows10\s+deviceCompliancePolicies\s+3\s+3\s+\+0")
        self.assertIn("No differences this cycle", out)

    def test_no_change_json_carries_full_counts(self):
        base, curr = pair()
        rc, j = self.run_json(base, curr)
        self.assertEqual(rc, 0)
        self.assertEqual(j["difference_count"], 0)
        self.assertEqual(j["summary"], ZERO)
        self.assertEqual(j["baseline"]["row_count"], TOTAL_ROWS)
        self.assertEqual(j["current"]["row_count"], TOTAL_ROWS)
        self.assertEqual(j["unchanged_rows"], TOTAL_ROWS)
        self.assertEqual(j["baseline"]["object_count"], 4)
        self.assertEqual(j["current"]["excluded_count"], 1)
        self.assertEqual(j["current"]["counts"]["macOS"]["configurationPolicies"], 3)
        self.assertEqual(j["warnings"], [])


# --------------------------------------------------------------------------------------
# Row-level classes
# --------------------------------------------------------------------------------------

class RowLevel(CliCase):

    def test_added_row(self):
        def m(objs, _):
            find(objs, WIN_POLICY)["settings"].append(
                setting("device_vendor_msft_policy_config_defender_allowioavprotection",
                        "device_vendor_msft_policy_config_defender_allowioavprotection_1"))
        base, curr = pair(m)
        d = diff(base, curr)
        self.assertEqual(counted(d), expect(added=1))
        row = d["added"][0]
        self.assertEqual(row["object_id"], WIN_POLICY)
        # A new key takes the NEXT free number -- never a gap, never an existing id.
        self.assertNotIn(row["id"], ids_by_key(base).values())
        self.assertEqual(row["id"], "BP-WIN-%04d" % (len([
            i for i in ids_by_key(base).values() if i.startswith("BP-WIN-")]) + 1))

    def test_removed_row(self):
        def m(objs, _):
            find(objs, WIN_CONFIG)["settings"].pop()   # passwordMinimumLength
        base, curr = pair(m)
        d = diff(base, curr)
        self.assertEqual(counted(d), expect(removed=1))
        self.assertEqual(d["removed"][0]["setting_id"], "passwordMinimumLength")
        self.assertEqual(d["removed"][0]["required_value"], "12")

    def test_changed_row(self):
        def m(objs, _):
            s = find(objs, WIN_POLICY)["settings"][0]
            s["value"] = "device_vendor_msft_policy_config_defender_allowrealtimemonitoring_0"
            s["display"] = "Not allowed"
        base, curr = pair(m)
        d = diff(base, curr)
        self.assertEqual(counted(d), expect(changed=1))
        e = d["changed"][0]
        self.assertTrue(e["from"].endswith("_1"))
        self.assertTrue(e["to"].endswith("_0"))
        self.assertEqual((e["from_display"], e["to_display"]), ("Allowed", "Not allowed"))
        self.assertEqual(e["setting_name"], "Allow Realtime Monitoring")
        self.assertEqual(ids_by_key(base)[e["row_key"]], e["id"])

    def test_differences_exit_1(self):
        def m(objs, _):
            find(objs, WIN_COMPLY)["settings"][0]["value"] = "10.0.22631"
        base, curr = pair(m)
        p = self.run_differ(base, curr)
        self.assertEqual(p.returncode, 1, p.stderr)
        self.assertIn("total differences: 1", p.stdout)
        self.assertIn("from: 10.0.19045", p.stdout)
        self.assertIn("to:   10.0.22631", p.stdout)


# --------------------------------------------------------------------------------------
# RENAMED -- the name is a diffed setting, and a rename is ONE event
# --------------------------------------------------------------------------------------

class Renamed(CliCase):

    def rename(self, oid, new):
        def m(objs, _):
            find(objs, oid)["name"] = new
        return m

    def test_rename_is_one_event_with_no_changed_rows_and_no_ids_moved(self):
        base, curr = pair(self.rename(MAC_POLICY, "Default FileVault macOS"))
        d = diff(base, curr)
        self.assertEqual(counted(d), expect(renamed=1))
        self.assertEqual(db.difference_count(d), 1)
        e = d["renamed"][0]
        self.assertEqual(e["from"], "Defualt FileVault macOS")
        self.assertEqual(e["to"], "Default FileVault macOS")
        self.assertEqual(e["object_id"], MAC_POLICY)
        self.assertEqual(e["total_settings"], 2)
        self.assertEqual(e["unaffected_settings"], 2)
        self.assertEqual((e["changed_settings"], e["added_settings"], e["removed_settings"]),
                         (0, 0, 0))
        self.assertEqual(e["ids_moved"], 0)
        # Zero CHANGED rows, and not one row identity or id moved anywhere.
        self.assertEqual(d["changed"], [])
        self.assertEqual(d["integrity"], [])
        self.assertEqual(ids_by_key(base), ids_by_key(curr))

    def test_rename_does_not_double_report_the_name_row(self):
        base, curr = pair(self.rename(WIN_POLICY, "Defender Windows (prod)"))
        d = diff(base, curr)
        self.assertFalse([c for c in d["changed"] if c["setting_id"] == NAME])
        self.assertFalse([r for r in d["added"] + d["removed"] if r["setting_id"] == NAME])

    def test_case_only_rename_is_still_a_rename(self):
        # Raw compare -- a casing fix is a real, visible change to the standard's wording.
        base, curr = pair(self.rename(WIN_CONFIG, "windows device restrictions"))
        d = diff(base, curr)
        self.assertEqual(counted(d), expect(renamed=1))

    def test_rename_plus_value_change_reports_both_separately(self):
        def m(objs, _):
            o = find(objs, WIN_POLICY)
            o["name"] = "Defender Windows"
            o["settings"][2]["value"] = "device_vendor_msft_policy_config_defender_puaprotection_2"
        base, curr = pair(m)
        d = diff(base, curr)
        self.assertEqual(counted(d), expect(renamed=1, changed=1))
        self.assertEqual(d["renamed"][0]["unaffected_settings"], 2)
        self.assertEqual(d["renamed"][0]["changed_settings"], 1)
        self.assertEqual(d["changed"][0]["setting_id"],
                         "device_vendor_msft_policy_config_defender_puaprotection")
        self.assertEqual(d["renamed"][0]["ids_moved"], 0)

    def test_rename_renders_old_and_new_name(self):
        base, curr = pair(self.rename(MAC_POLICY, "Default FileVault macOS"))
        p = self.run_differ(base, curr)
        self.assertEqual(p.returncode, 1, p.stderr)
        self.assertIn("from: Defualt FileVault macOS", p.stdout)
        self.assertIn("to:   Default FileVault macOS", p.stdout)
        self.assertIn("2 of 2 setting(s) unaffected", p.stdout)
        self.assertIn("0 id(s) moved", p.stdout)
        self.assertIn("CHANGED (required_value drifted) -- 0", p.stdout)


# --------------------------------------------------------------------------------------
# Whole-object rollups
# --------------------------------------------------------------------------------------

class WholeObject(unittest.TestCase):

    def test_whole_object_added_is_one_event(self):
        def m(objs, _):
            objs.append(obj("Windows Firewall", NEWCOMER, "windows10", "configurationPolicies", [
                setting("vendor_msft_firewall_mdmstore_domainprofile_enablefirewall",
                        "vendor_msft_firewall_mdmstore_domainprofile_enablefirewall_true"),
                setting("vendor_msft_firewall_mdmstore_publicprofile_enablefirewall",
                        "vendor_msft_firewall_mdmstore_publicprofile_enablefirewall_true"),
            ]))
        base, curr = pair(m)
        d = diff(base, curr)
        self.assertEqual(counted(d), expect(object_added=1))
        e = d["object_added"][0]
        self.assertEqual((e["object_id"], e["name"], e["row_count"]),
                         (NEWCOMER, "Windows Firewall", 3))
        self.assertEqual(len(e["ids"]), 3)
        self.assertEqual(d["added"], [])   # no row-level noise under the rollup

    def test_whole_object_removed_is_one_event(self):
        base, curr = pair(lambda objs, _: objs.remove(find(objs, WIN_COMPLY)))
        d = diff(base, curr)
        self.assertEqual(counted(d), expect(object_removed=1))
        e = d["object_removed"][0]
        self.assertEqual((e["object_id"], e["name"], e["row_count"]),
                         (WIN_COMPLY, "Windows Compliance", 3))
        self.assertEqual(d["removed"], [])


# --------------------------------------------------------------------------------------
# REASSIGNED -- matched on object_id, one event, both directions
# --------------------------------------------------------------------------------------

class Reassigned(CliCase):

    def test_assigned_to_unassigned(self):
        def m(objs, excl):
            objs.remove(find(objs, MAC_POLICY))
            excl.append({"collection": "configurationPolicies", "object_id": MAC_POLICY,
                         "name": "Defualt FileVault macOS", "platform": "macOS",
                         "reason": "unassigned"})
        base, curr = pair(m)
        d = diff(base, curr)
        self.assertEqual(counted(d), expect(reassigned=1))
        e = d["reassigned"][0]
        self.assertEqual(e["direction"], "assigned -> unassigned")
        self.assertEqual((e["object_id"], e["reason"], e["row_count"]),
                         (MAC_POLICY, "unassigned", 3))
        self.assertIsNone(e["previous_reason"])   # it was assigned in the baseline
        self.assertEqual(d["removed"], [])
        self.assertEqual(d["object_removed"], [])

    def test_unassigned_to_assigned(self):
        def m(objs, excl):
            excl.clear()
            objs.append(obj("TROUBLESHOOTING Disable all firewalls", DORMANT, "windows10",
                            "configurationPolicies", [
                                setting("vendor_msft_firewall_mdmstore_global_disable",
                                        "vendor_msft_firewall_mdmstore_global_disable_true")]))
        base, curr = pair(m)
        d = diff(base, curr)
        self.assertEqual(counted(d), expect(reassigned=1))
        e = d["reassigned"][0]
        self.assertEqual(e["direction"], "unassigned -> assigned")
        self.assertEqual((e["object_id"], e["row_count"]), (DORMANT, 2))
        # It is assigned NOW: the exclusion reason is the baseline side, never `reason`.
        self.assertIsNone(e["reason"])
        self.assertEqual(e["previous_reason"], "unassigned")
        self.assertEqual(d["added"], [])
        self.assertEqual(d["object_added"], [])

    def test_reassignment_carries_a_simultaneous_rename(self):
        def m(objs, excl):
            objs.remove(find(objs, MAC_POLICY))
            excl.append({"collection": "configurationPolicies", "object_id": MAC_POLICY,
                         "name": "RETIRED FileVault macOS", "platform": "macOS",
                         "reason": "unassigned"})
        base, curr = pair(m)
        e = diff(base, curr)["reassigned"][0]
        self.assertEqual((e["previous_name"], e["name"]),
                         ("Defualt FileVault macOS", "RETIRED FileVault macOS"))

    def test_reason_is_labelled_with_the_side_it_belongs_to(self):
        # "unassigned -> assigned (unassigned)" read as though the object were still
        # unassigned. Each direction must say whether the reason is now, or was.
        def became_assigned(objs, excl):
            excl.clear()
            objs.append(obj("TROUBLESHOOTING Disable all firewalls", DORMANT, "windows10",
                            "configurationPolicies", [
                                setting("vendor_msft_firewall_mdmstore_global_disable",
                                        "vendor_msft_firewall_mdmstore_global_disable_true")]))

        def became_unassigned(objs, excl):
            objs.remove(find(objs, MAC_POLICY))
            excl.append({"collection": "configurationPolicies", "object_id": MAC_POLICY,
                         "name": "Defualt FileVault macOS", "platform": "macOS",
                         "reason": "unassigned"})

        for mutate, direction, label in (
                (became_assigned, "unassigned -> assigned", "was excluded: unassigned"),
                (became_unassigned, "assigned -> unassigned", "now excluded: unassigned")):
            with self.subTest(direction=direction):
                base, curr = pair(mutate)
                text = self.run_differ(base, curr)
                self.assertEqual(text.returncode, 1, text.stderr)
                self.assertIn("%s  (%s)" % (direction, label), text.stdout)
                self.assertNotIn("%s  (unassigned)" % direction, text.stdout)
                md = self.run_differ(base, curr, "--format", "markdown")
                self.assertEqual(md.returncode, 1, md.stderr)
                self.assertIn("| Exclusion reason |", md.stdout)
                row = [ln for ln in md.stdout.splitlines()
                       if ln.startswith("|") and direction.replace(" -> ", " to ") in ln]
                self.assertEqual(len(row), 1, md.stdout)
                self.assertIn("| %s |" % label, row[0])
                rc, j = self.run_json(base, curr)
                self.assertEqual(rc, 1)
                ev = j["reassigned"][0]
                self.assertEqual(sum(ev[k] is not None for k in ("reason", "previous_reason")),
                                 1, ev)

    def test_matched_on_object_id_never_on_name(self):
        # A DIFFERENT object with the same name appears in the excluded list, while the
        # original is deleted outright. That is a removal, not an unassignment.
        def m(objs, excl):
            objs.remove(find(objs, MAC_POLICY))
            excl.append({"collection": "configurationPolicies",
                         "object_id": "bbbbbbbb-0000-4000-8000-000000000099",
                         "name": "Defualt FileVault macOS", "platform": "macOS",
                         "reason": "unassigned"})
        base, curr = pair(m)
        d = diff(base, curr)
        self.assertEqual(counted(d), expect(object_removed=1))
        self.assertEqual(len(d["excluded_added"]), 1)   # listed, not counted


# --------------------------------------------------------------------------------------
# What is NOT compared
# --------------------------------------------------------------------------------------

class NotCompared(CliCase):

    def test_pure_display_value_change_is_no_difference(self):
        def m(objs, _):
            s = find(objs, WIN_POLICY)["settings"][0]
            s["display"] = "Allowed. Turns on real-time protection."   # Microsoft relabel
            s["label"] = "Allow Real-time Monitoring"
        base, curr = pair(m)
        d = diff(base, curr)
        self.assertEqual(db.difference_count(d), 0)
        self.assertEqual(len(d["display_only"]), 1)   # visible, but not counted
        p = self.run_differ(base, curr)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("total differences: 0", p.stdout)
        self.assertIn("display-only relabels=1", p.stdout)

    def test_object_name_enforced_at_and_verify_are_not_compared(self):
        base, curr = pair()
        for r in curr["rows"]:
            if r["setting_id"] != NAME:
                r["object_name"] = "something else"
                r["enforced_at"] = "Intune > elsewhere"
                r["verify"] = "$.moved"
        d = diff(base, curr)
        self.assertEqual(db.difference_count(d), 0)


# --------------------------------------------------------------------------------------
# Refusals -- exit 2
# --------------------------------------------------------------------------------------

class Refusals(CliCase):

    def test_cross_major_version_is_refused(self):
        base, curr = pair()
        base["meta"]["generator_version"] = "1.0"
        p = self.run_differ(base, curr)
        self.assertEqual(p.returncode, 2)
        self.assertIn("refusing to compare across generator major versions", p.stderr)
        self.assertEqual(p.stdout, "")

    def test_two_v1_files_are_refused(self):
        base, curr = pair()
        base["meta"]["generator_version"] = curr["meta"]["generator_version"] = "1.0"
        p = self.run_differ(base, curr)
        self.assertEqual(p.returncode, 2)
        self.assertIn("implements row contract v2", p.stderr)

    def test_missing_version_is_refused(self):
        base, curr = pair()
        del curr["meta"]["generator_version"]
        p = self.run_differ(base, curr)
        self.assertEqual(p.returncode, 2)
        self.assertIn("no usable meta.generator_version", p.stderr)

    def test_minor_version_difference_is_accepted(self):
        base, curr = pair(version="2.3")
        self.assertEqual(self.run_differ(base, curr).returncode, 0)

    def test_self_diff_is_refused(self):
        base, _ = pair()
        path = self.place(base, "2026-09-24")
        p = self.run_differ(path, path)
        self.assertEqual(p.returncode, 2)
        self.assertIn("against itself", p.stderr)

    def test_v1_style_name_key_is_refused(self):
        base, curr = pair()
        r = curr["rows"][1]
        r["row_key"] = "|".join([r["collection"], r["platform"], "default defender windows",
                                 r["setting_id"].lower()])
        p = self.run_differ(base, curr)
        self.assertEqual(p.returncode, 2)
        self.assertIn("not collection|object_id|setting_id", p.stderr)

    def test_duplicate_row_key_is_refused_unless_allowed(self):
        base, curr = pair()
        curr["rows"].append(copy.deepcopy(curr["rows"][1]))
        p = self.run_differ(base, curr)
        self.assertEqual(p.returncode, 2)
        self.assertIn("duplicate row_key", p.stderr)
        p = self.run_differ(base, curr, "--allow-duplicate-keys")
        self.assertIn(p.returncode, (0, 1), p.stderr)
        self.assertIn("duplicate row_key", p.stdout)   # on the record, in the body

    def test_an_unexpected_crash_exits_2_never_1(self):
        # 1 means "differences found". A crash must never be mistaken for drift.
        base, curr = pair()
        curr["rows"][3]["platform"] = 5
        p = self.run_differ(base, curr)
        self.assertEqual(p.returncode, 2, p.stdout)
        self.assertIn("did not complete", p.stderr)

    def test_non_ascii_names_survive_an_ascii_locale(self):
        def m(objs, _):
            find(objs, WIN_POLICY)["name"] = "Richtlinie f\u00fcr Ger\u00e4te \u2014 Windows"
        base, curr = pair(m)
        env = dict(ENV, PYTHONIOENCODING="ascii", LC_ALL="C", LANG="C")
        bp, cp = self.place(base, "2026-09-24"), self.place(curr, "2026-12-24")
        p = subprocess.run([sys.executable, str(DIFFER), "--baseline", str(bp), "--current",
                            str(cp)], capture_output=True, env=env)
        self.assertEqual(p.returncode, 1, p.stderr)
        self.assertIn("to:   Richtlinie f\u00fcr Ger\u00e4te \u2014 Windows",
                      p.stdout.decode("utf-8"))

    def test_invalid_json_is_refused(self):
        base, _ = pair()
        bad = self.tmp / "2026-12-24" / "baseline-rows.json"
        bad.parent.mkdir(parents=True)
        bad.write_text('{"meta": {"generator_version": "2.0"}, "rows": [', encoding="utf-8")
        p = self.run_differ(base, bad)
        self.assertEqual(p.returncode, 2)
        self.assertIn("not valid JSON", p.stderr)


# --------------------------------------------------------------------------------------
# Integrity -- the id map is permanent
# --------------------------------------------------------------------------------------

class Integrity(CliCase):

    def test_id_changed_under_a_stable_row_key(self):
        base, curr = pair()
        curr["rows"][2]["id"] = "BP-WIN-0999"
        d = diff(base, curr)
        self.assertEqual(counted(d), expect(integrity=1))
        self.assertEqual(d["integrity"][0]["kind"], "id changed for an unchanged row_key")
        self.assertEqual(self.run_differ(base, curr).returncode, 1)

    def test_retired_id_reused_for_a_different_row(self):
        def m(objs, _):
            find(objs, WIN_CONFIG)["settings"].pop()
        base, curr = pair(m)
        retired = [r["id"] for r in base["rows"] if r["setting_id"] == "passwordMinimumLength"][0]
        curr["rows"].append(dict(rows_for(obj("X", NEWCOMER, settings=[]))[0], id=retired))
        d = diff(base, curr)
        kinds = [e["kind"] for e in d["integrity"]]
        self.assertIn("id reused for a different row_key", kinds)


# --------------------------------------------------------------------------------------
# Outputs -- the markdown and json records for the dated folder
# --------------------------------------------------------------------------------------

def table_blocks(md):
    """Consecutive '|'-lines grouped into tables."""
    blocks, cur = [], []
    for line in md.splitlines():
        if line.startswith("|"):
            cur.append(line)
        elif cur:
            blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)
    return blocks


def cell_count(line):
    return len(re.split(r"(?<!\\)\|", line.strip())) - 2


class Outputs(CliCase):

    HOSTILE = ("<script>alert(1)</script> | [x](javascript:alert(1)) `tick` *bold* "
               "_emph_ keep_intraword")

    def hostile_pair(self):
        def m(objs, _):
            find(objs, WIN_POLICY)["name"] = self.HOSTILE
            find(objs, WIN_CONFIG)["settings"][0]["value"] = "a|b<i>c</i>`d`"
        return pair(m)

    def test_markdown_frontmatter_is_a_record(self):
        base, curr = pair()
        p = self.run_differ(base, curr, "--format", "markdown")
        self.assertEqual(p.returncode, 0, p.stderr)
        md = p.stdout
        self.assertTrue(md.startswith("---\ntype: Record\n"), md[:80])
        head = md.split("\n---\n", 1)[0]
        for line in ("doc_type: record", "status: active", "last_reviewed: 2026-12-24",
                     'title: "Configuration baseline diff 2026-12-24 against 2026-09-24"',
                     "  - ../2026-09-24/README.md"):
            self.assertIn(line, head.splitlines())
        self.assertIn("**No differences this cycle.**", md)

    def test_markdown_escapes_untrusted_text(self):
        base, curr = self.hostile_pair()
        p = self.run_differ(base, curr, "--format", "markdown")
        self.assertEqual(p.returncode, 1, p.stderr)
        md = p.stdout
        self.assertNotIn("<script>", md)
        # The hostile VALUE survives only inside an inline code span, where html is inert.
        span = "`` a\\|b<i>c</i>`d` ``"
        self.assertIn(span, md)
        self.assertNotIn("<i>", md.replace(span, ""))
        self.assertNotIn("[x](javascript", md)
        self.assertIn("&lt;script&gt;", md)
        self.assertIn("\\*bold\\*", md)
        self.assertIn("\\_emph\\_ keep_intraword", md)   # edges escaped, intraword left
        # Every row of every table has the same number of cells as its header: nothing
        # smuggled an extra column in.
        for block in table_blocks(md.split("\n---\n", 1)[1]):
            widths = {cell_count(line) for line in block}
            self.assertEqual(len(widths), 1, "\n".join(block))

    def test_outputs_are_deterministic_and_portable(self):
        base, curr = self.hostile_pair()
        runs = [self.run_differ(base, curr, "--format", f) for f in ("markdown", "json") * 2]
        self.assertEqual(runs[0].stdout, runs[2].stdout)
        self.assertEqual(runs[1].stdout, runs[3].stdout)
        for p in runs:
            self.assertNotIn(str(self.tmp), p.stdout)   # no machine-specific path
        j = json.loads(runs[1].stdout)
        self.assertEqual(j["baseline"]["path"], "2026-09-24/baseline-rows.json")
        self.assertEqual(j["current"]["date"], "2026-12-24")

    def test_json_top_level_lists_are_exactly_the_counted_classes(self):
        # A consumer (the evidence pack) may render every top-level list as a class of
        # drift. Relabels and never-assigned churn must therefore never sit up there.
        def m(objs, excl):
            find(objs, WIN_POLICY)["settings"][0]["display"] = "relabelled"
            excl.append({"collection": "configurationPolicies", "object_id": NEWCOMER,
                         "name": "Draft policy", "platform": "windows10",
                         "reason": "unassigned"})
        base, curr = pair(m)
        rc, j = self.run_json(base, curr)
        self.assertEqual(rc, 0)
        lists = {k for k, x in j.items() if isinstance(x, list)}
        self.assertEqual(lists, set(db.COUNTED) | {"warnings"})
        self.assertEqual(j["not_counted_summary"],
                         {"display_only": 1, "excluded_added": 1, "excluded_removed": 0})
        self.assertEqual(j["not_counted"]["excluded_added"][0]["object_id"], NEWCOMER)

    def test_one_pass_writes_both_records_and_prints_text(self):
        def m(objs, _):
            find(objs, WIN_COMPLY)["settings"][1]["value"] = "false"
        base, curr = pair(m)
        md = self.tmp / "2026-12-24" / "diff-vs-2026-09-24.md"
        js = self.tmp / "2026-12-24" / "diff-vs-2026-09-24.json"
        p = self.run_differ(base, curr, "--markdown-out", str(md), "--json-out", str(js))
        self.assertEqual(p.returncode, 1, p.stderr)
        self.assertIn("total differences: 1", p.stdout)
        self.assertTrue(md.read_text(encoding="utf-8").startswith("---\ntype: Record\n"))
        j = json.loads(js.read_text(encoding="utf-8"))
        self.assertEqual(j["summary"], expect(changed=1))
        # The written records match what the --format mode produces.
        self.assertEqual(md.read_text(encoding="utf-8"),
                         self.run_differ(base, curr, "--format", "markdown").stdout)


# --------------------------------------------------------------------------------------
# End to end -- the real generator, through its CLI, on the retained dump
# --------------------------------------------------------------------------------------

def standards_repo():
    """STANDARDS_REPO, else the sibling checkout of ai-skills. None when this file has
    been copied somewhere too shallow to have one (a temp dir, say)."""
    env = os.environ.get("STANDARDS_REPO")
    if env:
        return Path(env)
    parents = HERE.parents
    return parents[5] / "security-documentation-restricted" if len(parents) > 5 else None


def newest_dump():
    repo = standards_repo()
    root = repo / "configuration-hardening" / "dumps" if repo else None
    if root is None or not root.is_dir():
        return None
    dated = sorted(p for p in root.iterdir()
                   if p.is_dir() and re.match(r"^\d{4}-\d{2}-\d{2}$", p.name)
                   and (p / "intune-config-export.json").is_file())
    return dated[-1] / "intune-config-export.json" if dated else None


class EndToEnd(unittest.TestCase):
    """Reads the retained dump; writes only to temp. Skips ONLY when there is no retained
    dump or no generator file. A generator that fails, or emits non-2.x rows, is a FAILURE:
    v2 has landed, and a skip there would hide a generator regression."""

    def setUp(self):
        self.dump = newest_dump()
        if self.dump is None or not GENERATOR.is_file():
            self.skipTest("no retained dump or no generator to run end to end")
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.id_map = self.tmp / "id-map.json"

    def tearDown(self):
        if hasattr(self, "_tmp"):
            self._tmp.cleanup()

    def generate(self, dump_obj, date):
        folder = self.tmp / date
        folder.mkdir()
        dump = folder / "intune-config-export.json"
        dump.write_text(json.dumps(dump_obj), encoding="utf-8")
        out = folder / "baseline-rows.json"
        p = subprocess.run([sys.executable, str(GENERATOR), "--dump", str(dump), "--out",
                            str(out), "--id-map", str(self.id_map),
                            "--generated-at", "%sT00:00:00Z" % date],
                           capture_output=True, text=True, env=ENV)
        if p.returncode != 0:
            self.fail("generator exited %d on the retained dump: %s"
                      % (p.returncode, p.stderr.strip()[-300:]))
        doc = json.loads(out.read_text(encoding="utf-8"))
        if not str(doc["meta"].get("generator_version", "")).startswith("2."):
            self.fail("generator emits %r rows, not 2.x"
                      % doc["meta"].get("generator_version"))
        return out, doc

    def differ(self, a, b):
        return subprocess.run([sys.executable, str(DIFFER), "--baseline", str(a), "--current",
                               str(b), "--format", "json"],
                              capture_output=True, text=True, env=ENV)

    def test_rename_unassign_and_flip_on_the_real_dump(self):
        raw = json.loads(self.dump.read_text(encoding="utf-8-sig"))
        base_path, base = self.generate(raw, "2026-09-24")

        # Choose targets from the ROWS (the contract), then mutate the dump to match.
        by_obj = {}
        for r in base["rows"]:
            by_obj.setdefault((r["collection"], r["object_id"]), []).append(r)
        catalog = sorted(oid for (col, oid), rows in by_obj.items()
                         if col == "configurationPolicies" and len(rows) >= 3)
        self.assertGreaterEqual(len(catalog), 2)
        rename_id, unassign_id = catalog[0], catalog[1]
        flip = [r for r in base["rows"] if r["collection"] == "deviceConfigurations"
                and r["required_value"] in ("true", "false") and "#" not in r["setting_id"]]
        self.assertTrue(flip)
        flip = flip[0]

        mutated = copy.deepcopy(raw)
        for p in mutated["configurationPolicies"]:
            if p["id"] == rename_id:
                old_name = p["name"]
                p["name"] = old_name + " (renamed)"
            if p["id"] == unassign_id:
                p["isAssigned"] = False
                p["assignments"] = []
        for o in mutated["deviceConfigurations"]:
            if o["id"] == flip["object_id"]:
                o[flip["setting_id"]] = not o[flip["setting_id"]]
        curr_path, curr = self.generate(mutated, "2026-12-24")

        p = self.differ(base_path, curr_path)
        self.assertEqual(p.returncode, 1, p.stderr)
        j = json.loads(p.stdout)
        self.assertEqual(j["summary"], expect(renamed=1, reassigned=1, changed=1), j["summary"])
        e = j["renamed"][0]
        self.assertEqual((e["object_id"], e["from"], e["to"]),
                         (rename_id, old_name, old_name + " (renamed)"))
        self.assertEqual(e["ids_moved"], 0)
        self.assertEqual(e["unaffected_settings"], e["total_settings"])
        self.assertEqual(j["reassigned"][0]["object_id"], unassign_id)
        self.assertEqual(j["reassigned"][0]["direction"], "assigned -> unassigned")
        self.assertEqual((j["reassigned"][0]["reason"], j["reassigned"][0]["previous_reason"]),
                         ("unassigned", None))
        self.assertEqual(j["changed"][0]["row_key"], flip["row_key"])
        # Permanence across the real id map: every surviving row kept its id.
        b_ids, c_ids = ids_by_key(base), ids_by_key(curr)
        for k in set(b_ids) & set(c_ids):
            self.assertEqual(b_ids[k], c_ids[k], k)

    def test_regenerating_the_same_dump_is_clean(self):
        raw = json.loads(self.dump.read_text(encoding="utf-8-sig"))
        a, _ = self.generate(raw, "2026-09-24")
        b, doc = self.generate(raw, "2026-12-24")
        p = self.differ(a, b)
        self.assertEqual(p.returncode, 0, p.stderr)
        j = json.loads(p.stdout)
        self.assertEqual(j["difference_count"], 0)
        self.assertEqual(j["unchanged_rows"], len(doc["rows"]))
        self.assertIn("SAME source dump", j["warnings"][0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
