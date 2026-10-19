#!/usr/bin/env python3
"""Tests for generate_baseline.py (contract v2) -- the properties the quarterly diff
depends on.

These are not coverage tests. Each one guards a property that, if it broke, would break
the review QUIETLY: the diff would still run, still produce a report, and the report
would be wrong. That is the failure mode worth spending tests on.

    id permanence      a re-run must not renumber. A renumbered standard invalidates
                       every prior review note and every ticket citing a row id, and
                       nothing about the output would look wrong.
    no id reuse        a row that disappears keeps its number reserved.
    rename stability   identity is the Intune object id. A rename -- typo fix or not --
                       moves no id and changes exactly one value: the name row's.
    v1 map refusal     a name-keyed v1 id-map is refused, never silently migrated.
    display only       labels from the Settings Catalog definitions never touch
                       row_key, id or required_value -- the only fields the diff reads.
    sort order         platform, collection, name, object id, name row first, setting.
    determinism        same input, byte-identical output, through the CLI as well.
    no clock           build_rows must not read the time.
    payload hashing    a 12KB base64 plist must never reach required_value.
    preview only       --format markdown is a preview: it is not the ratify block, and
                       it never writes the id-map -- a look at a dump cannot reserve ids.
    refuse, not crash  a dump whose collections hold zero objects is refused; a shape
                       the contract does not know is refused by JSON path, never a
                       traceback and never a plausible row built from the wrong thing.
    incidents shown    the cycle record states manifest incidents and tool.git_dirty,
                       so an --accept-incomplete collection never reads as a clean one.
    truncation refused a dump whose settingCount disagrees with its settings exits 1,
                       naming each policy and both numbers, and writes nothing. The
                       --allow-truncated override is recorded in meta, the cycle record
                       and the preview, so a truncated baseline never passes as complete.
    known limits       duplicate-then-delete is an add plus a remove, not a rename; a
                       repeated settingDefinitionId is identified by position. Pinned, so
                       changing either is a decision rather than an accident.

V1 -> V2 LEDGER (the 24 v1 tests; every change is deliberate)
    Unchanged: second_run_does_not_renumber, a_removed_row_keeps_its_number_reserved,
        platform_filter_cannot_renumber_another_platform, prefix_is_per_platform,
        base64_payload_is_hashed_not_inlined, windows_update_type_is_not_read_as_bare_
        windows, leaf_counts_separate_scalar_from_collection, byte_identical_across_runs,
        source_ordering_does_not_change_output, build_rows_never_reads_the_clock,
        headings_are_not_swallowed_by_the_preceding_table, authority_carries_the_
        generated_at_date.
    adding_a_row_does_not_disturb_existing_ids: the new id is BP-WIN-0004, not 0003 --
        the object's name row now holds BP-WIN-0001.
    Flattening x4, metadata_nulls_and_empty_containers_are_not_rows: assert on SETTING
        rows only, because every object now also carries its identity row.
    unassigned_objects_are_excluded_with_a_reason: excluded entries now carry
        object_id and platform (contract v2).
    assignment_signal_disagreement...: 2 rows (name + setting), not 1.
    pipes_in_a_value_cannot_break_the_table: picks the VALUE row -- the first BP- row is
        now the name row, which has no pipes and would pass vacuously.
    NameNormalisation x3 -> RenameStability: normalise_name() is gone, because identity no
        longer reads the name at all. The property those tests protected -- a typo fix
        causes no id churn -- is now asserted directly and more strongly: ANY rename,
        not just the two folded typos, moves no id.

Pure stdlib. Run through WSL:
    python3 -m unittest discover -s scripts -p 'test_*.py' -v
    python3 scripts/test_generate_baseline.py
    BASELINE_REAL_DUMP=/path/to/intune-config-export.json python3 ...   (adds RealDump)
"""

import contextlib
import copy
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import generate_baseline as gb

GENERATED_AT = "2026-09-24T00:00:00Z"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "synthetic-setting-definitions.json"


def guid_for(name):
    """A stable, distinct GUID per object name -- identity is the GUID, so fixtures must
    carry distinct ones exactly as Graph does."""
    d = hashlib.sha256(name.encode("utf-8")).hexdigest()
    return "%s-%s-%s-%s-%s" % (d[:8], d[8:12], d[12:16], d[16:20], d[20:32])


def choice(definition_id, value, children=None):
    return {
        "@odata.type": "#microsoft.graph.deviceManagementConfigurationChoiceSettingInstance",
        "settingDefinitionId": definition_id,
        "choiceSettingValue": {"value": value, "children": children or []},
    }


def simple(definition_id, value):
    return {
        "@odata.type": "#microsoft.graph.deviceManagementConfigurationSimpleSettingInstance",
        "settingDefinitionId": definition_id,
        "simpleSettingValue": {"value": value},
    }


def simple_collection(definition_id, values):
    return {
        "@odata.type": "#microsoft.graph.deviceManagementConfigurationSimpleSettingCollectionInstance",
        "settingDefinitionId": definition_id,
        "simpleSettingCollectionValue": [{"value": v} for v in values],
    }


def choice_collection(definition_id, values):
    return {
        "@odata.type": "#microsoft.graph.deviceManagementConfigurationChoiceSettingCollectionInstance",
        "settingDefinitionId": definition_id,
        "choiceSettingCollectionValue": [{"value": v, "children": []} for v in values],
    }


def policy(name, platform, instances, assigned=True, guid=None):
    return {
        "id": guid or guid_for(name),
        "name": name,
        "platforms": platform,
        "isAssigned": assigned,
        "assignments": [{"target": {}}] if assigned else [],
        "settings": [{"id": str(i), "settingInstance": inst}
                     for i, inst in enumerate(instances)],
    }


def bag(name, odata_type, props, assigned=True, guid=None):
    """A deviceConfigurations / deviceCompliancePolicies object."""
    obj = {"@odata.type": odata_type, "id": guid or guid_for(name), "displayName": name,
           "assignments": [{"target": {}}] if assigned else []}
    obj.update(props)
    return obj


def mini_dump(policies=None, device_configurations=None, compliance=None):
    return {
        "configurationPolicies": policies or [],
        "deviceConfigurations": device_configurations or [],
        "deviceCompliancePolicies": compliance or [],
    }


def mixed_dump():
    """One object in each collection, shaped like the real tenant's."""
    return mini_dump(
        [policy("Default LAPS Policy", "windows10", [
            choice("device_vendor_msft_laps_policies_backupdirectory",
                   "device_vendor_msft_laps_policies_backupdirectory_1"),
            simple("device_vendor_msft_laps_policies_passphraselength", 3),
        ])],
        device_configurations=[bag("Default Device Restrictions Configuration",
                                   "#microsoft.graph.macOSGeneralDeviceConfiguration",
                                   {"passwordRequired": True,
                                    "passwordMinimumLength": 12})],
        compliance=[bag("Default iOS Compliance", "#microsoft.graph.iosCompliancePolicy",
                        {"passcodeRequired": True})])


def generate(dump, id_map, platform_filter="all", definitions=None):
    doc = gb.build_rows(dump, GENERATED_AT, "deadbeef", "intune-config-export.json",
                        platform_filter, definitions=definitions)
    gb.assign_ids(doc["rows"], id_map)
    return doc


def settings(rows):
    """Setting rows only -- every object also carries one identity (name) row."""
    return [r for r in rows if r["mode"] != "identity"]


def keyed(doc):
    return {r["row_key"]: r for r in doc["rows"]}


def run_cli(argv):
    """-> (exit code or message, stdout, stderr) without letting output reach the run."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = gb.main(argv)
        except SystemExit as exc:
            code = exc.code
    return code, out.getvalue(), err.getvalue()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


# ------------------------------------------------------------------------ v1 retained

class IdPermanence(unittest.TestCase):
    """The single most important property. Ids are cited in tickets and audit notes."""

    def setUp(self):
        self.dump = mini_dump([
            policy("Default Defender Windows", "windows10", [
                choice("setting_alpha", "setting_alpha_1"),
                choice("setting_bravo", "setting_bravo_0"),
            ]),
            policy("Default FileVault macOS", "macOS", [
                choice("setting_charlie", "setting_charlie_1"),
            ]),
        ])

    def test_second_run_does_not_renumber(self):
        id_map = {}
        first = {r["row_key"]: r["id"] for r in generate(self.dump, id_map)["rows"]}
        second = {r["row_key"]: r["id"] for r in generate(self.dump, id_map)["rows"]}
        self.assertEqual(first, second)

    def test_adding_a_row_does_not_disturb_existing_ids(self):
        id_map = {}
        before = {r["row_key"]: r["id"] for r in generate(self.dump, id_map)["rows"]}

        # Next quarter: a new setting lands in the FIRST policy, which would shift every
        # subsequent row if ids came from position rather than from the map.
        self.dump["configurationPolicies"][0]["settings"].insert(
            0, {"id": "9", "settingInstance": choice("setting_aardvark",
                                                     "setting_aardvark_1")})
        after = {r["row_key"]: r["id"] for r in generate(self.dump, id_map)["rows"]}

        for key, value in before.items():
            self.assertEqual(after[key], value, "renumbered: %s" % key)
        new = set(after) - set(before)
        self.assertEqual(len(new), 1)
        # Next free number, not a gap-fill. v2: the name row holds BP-WIN-0001, the two
        # settings 0002-0003, so the newcomer is 0004.
        self.assertEqual(after[new.pop()], "BP-WIN-0004")

    def test_a_removed_row_keeps_its_number_reserved(self):
        id_map = {}
        before = generate(self.dump, id_map)
        retired = [r["id"] for r in before["rows"] if r["setting_id"] == "setting_bravo"][0]

        # The setting is removed from the tenant...
        self.dump["configurationPolicies"][0]["settings"] = [
            {"id": "0", "settingInstance": choice("setting_alpha", "setting_alpha_1")}]
        generate(self.dump, id_map)

        # ...and then a different setting appears. It must NOT inherit the retired id.
        self.dump["configurationPolicies"][0]["settings"].append(
            {"id": "1", "settingInstance": choice("setting_delta", "setting_delta_1")})
        after = generate(self.dump, id_map)

        issued = [r["id"] for r in after["rows"]]
        self.assertNotIn(retired, issued)
        self.assertIn(retired, id_map.values(), "retired id vanished from the map")

    def test_platform_filter_cannot_renumber_another_platform(self):
        """Generating only Windows must leave the macOS numbering untouched."""
        id_map = {}
        full = {r["row_key"]: r["id"] for r in generate(self.dump, id_map)["rows"]}
        generate(self.dump, id_map, platform_filter="windows")
        after = {r["row_key"]: r["id"] for r in generate(self.dump, id_map)["rows"]}
        self.assertEqual(full, after)

    def test_prefix_is_per_platform(self):
        rows = generate(self.dump, {})["rows"]
        prefixes = {r["platform"]: r["id"][:6] for r in rows}
        self.assertEqual(prefixes, {"windows10": "BP-WIN", "macOS": "BP-MAC"})


class RenameStability(unittest.TestCase):
    """Identity is the object id. Replaces v1's NameNormalisation -- see the ledger."""

    def assert_only_the_name_row_changed(self, before, after, id_map_size, id_map):
        self.assertEqual(set(keyed(before)), set(keyed(after)), "a rename moved a row_key")
        for key, row in keyed(before).items():
            self.assertEqual(keyed(after)[key]["id"], row["id"], "renumbered: %s" % key)
        changed = [k for k, r in keyed(before).items()
                   if keyed(after)[k]["required_value"] != r["required_value"]]
        self.assertTrue(changed)
        self.assertTrue(all(k.endswith("|@displayname") for k in changed), changed)
        self.assertEqual(len(id_map), id_map_size, "the rename created id-map entries")
        return changed

    def test_both_default_typos_fold(self):
        """v1 folded 'Defualt' and 'Defult' in the key. v2 needs no folding: fixing
        EITHER typo moves no id, and the fix is one visible change on the name row."""
        for typo in ("Defualt Edge Settings macOS", "Defult Edge Settings macOS"):
            id_map = {}
            guid = "0bd1c962-0981-4a01-b410-b14e0f37b916"
            before = generate(mini_dump([policy(typo, "macOS", [
                choice("setting_alpha", "setting_alpha_1")], guid=guid)]), id_map)
            after = generate(mini_dump([policy("Default Edge Settings macOS", "macOS", [
                choice("setting_alpha", "setting_alpha_1")], guid=guid)]), id_map)
            changed = self.assert_only_the_name_row_changed(before, after, 2, id_map)
            self.assertEqual(len(changed), 1)

    def test_whitespace_and_case_collapse(self):
        """v1 collapsed whitespace and case out of the key, which also HID a
        whitespace-only rename. v2 keeps the name verbatim: no id moves, and the change
        is visible rather than silently absorbed."""
        id_map, guid = {}, "3cb265f4-208f-48bd-bbc6-a0e351d3bcf4"
        messy = "  Default   NGP\tWindows  "
        before = generate(mini_dump([policy(messy, "windows10", [choice("a", "a_1")],
                                            guid=guid)]), id_map)
        self.assertEqual(before["rows"][0]["required_value"], messy, "name not verbatim")
        after = generate(mini_dump([policy("default ngp windows", "windows10",
                                           [choice("a", "a_1")], guid=guid)]), id_map)
        self.assert_only_the_name_row_changed(before, after, 2, id_map)

    def test_fixing_the_typo_in_intune_causes_no_churn(self):
        """The reason v1's folding existed: a UI typo fix must not read as delete+add."""
        id_map, guid = {}, "0bd1c962-0981-4a01-b410-b14e0f37b916"
        typo = mini_dump([policy("Defualt Edge Settings macOS", "macOS",
                                 [choice("setting_alpha", "setting_alpha_1")], guid=guid)])
        before = {r["row_key"]: r["id"] for r in generate(typo, id_map)["rows"]}

        fixed = mini_dump([policy("Default Edge Settings macOS", "macOS",
                                  [choice("setting_alpha", "setting_alpha_1")], guid=guid)])
        after = {r["row_key"]: r["id"] for r in generate(fixed, id_map)["rows"]}

        self.assertEqual(before, after)
        self.assertEqual(len(id_map), 2, "the rename created a new id-map entry")

    def test_renaming_every_object_in_a_dump_copy_moves_no_id(self):
        """All three collections at once, on a copy -- exactly as next quarter's dump
        would arrive: every id unchanged, one changed value per renamed object."""
        id_map = {}
        original = mixed_dump()
        before = generate(original, id_map)
        renamed = copy.deepcopy(original)
        renamed["configurationPolicies"][0]["name"] = "LAPS - Windows (renamed)"
        renamed["deviceConfigurations"][0]["displayName"] = "macOS Restrictions"
        renamed["deviceCompliancePolicies"][0]["displayName"] = "iOS Compliance v2"
        after = generate(renamed, id_map)

        changed = self.assert_only_the_name_row_changed(before, after, len(id_map), id_map)
        self.assertEqual(len(changed), 3)
        self.assertEqual(sorted(keyed(after)[k]["required_value"] for k in changed),
                         ["LAPS - Windows (renamed)", "iOS Compliance v2",
                          "macOS Restrictions"])

    def test_every_object_has_exactly_one_name_row(self):
        doc = generate(mixed_dump(), {})
        names = [r for r in doc["rows"] if r["setting_id"] == gb.NAME_SETTING_ID]
        self.assertEqual(len(names), 3)
        for row in names:
            self.assertEqual(row["mode"], "identity")
            self.assertEqual(row["setting_name"], "Policy name")
            self.assertEqual(row["display_value"], row["required_value"])
            self.assertEqual(row["required_value"], row["object_name"])

    def test_row_key_carries_no_name_and_no_platform(self):
        doc = generate(mixed_dump(), {})
        for row in doc["rows"]:
            self.assertEqual(row["row_key"], "%s|%s|%s" % (
                row["collection"], row["object_id"].lower(), row["setting_id"].lower()))


class Flattening(unittest.TestCase):

    def test_group_nodes_are_containers_not_rows(self):
        """A group node has no value of its own; only its descendants earn rows."""
        nested = {
            "@odata.type": "#microsoft.graph.deviceManagementConfigurationGroupSettingCollectionInstance",
            "settingDefinitionId": "group_outer",
            "groupSettingCollectionValue": [
                {"children": [choice("leaf_inner", "leaf_inner_1")]}],
        }
        rows = settings(generate(mini_dump([policy("P", "windows10", [nested])]), {})["rows"])
        self.assertEqual([r["setting_id"] for r in rows], ["leaf_inner"])

    def test_children_of_a_choice_are_rows_in_their_own_right(self):
        parent = choice("leaf_parent", "leaf_parent_1",
                        children=[choice("leaf_child", "leaf_child_0")])
        rows = settings(generate(mini_dump([policy("P", "windows10", [parent])]), {})["rows"])
        self.assertEqual(sorted(r["setting_id"] for r in rows),
                         ["leaf_child", "leaf_parent"])

    def test_collection_leaf_preserves_order(self):
        """The Windows logon message is three elements that are three lines of one
        message. Sorting them would rewrite the message."""
        instance = simple_collection("logon_message", ["zebra", "apple"])
        rows = settings(generate(mini_dump([policy("P", "windows10", [instance])]),
                                 {})["rows"])
        self.assertEqual(rows[0]["required_value"], '["zebra","apple"]')

    def test_duplicate_setting_id_in_one_policy_is_disambiguated(self):
        """Zero occurrences in the 2026-09 dump, but the tree permits it -- and an
        undisambiguated collision would silently merge two settings into one row."""
        rows = settings(generate(mini_dump([policy("P", "windows10", [
            choice("same_id", "same_id_0"),
            choice("same_id", "same_id_1"),
        ])]), {})["rows"])
        self.assertEqual(sorted(r["setting_id"] for r in rows), ["same_id", "same_id#2"])
        self.assertEqual(len({r["row_key"] for r in rows}), 2)


class PropertyBags(unittest.TestCase):

    def test_base64_payload_is_hashed_not_inlined(self):
        blob = "A" * 5000
        dump = mini_dump(device_configurations=[{
            "@odata.type": "#microsoft.graph.macOSCustomConfiguration",
            "id": "guid", "displayName": "MDE macOS Onboarding",
            "assignments": [{"target": {}}],
            "payload": blob, "payloadFileName": "mde.mobileconfig",
        }])
        rows = {r["setting_id"]: r["required_value"] for r in generate(dump, {})["rows"]}
        self.assertTrue(rows["payload"].startswith("sha256:"))
        self.assertNotIn("AAAA", rows["payload"])
        self.assertEqual(rows["payload"], "sha256:" + gb.sha256_text(blob))
        # A short field alongside it is still inlined.
        self.assertEqual(rows["payloadFileName"], "mde.mobileconfig")

    def test_metadata_nulls_and_empty_containers_are_not_rows(self):
        dump = mini_dump(compliance=[{
            "@odata.type": "#microsoft.graph.windows10CompliancePolicy",
            "id": "guid", "displayName": "Win Baseline", "description": "notes",
            "version": 4, "createdDateTime": "2025-01-01T00:00:00Z",
            "assignments": [{"target": {}}],
            "bitLockerEnabled": True, "osMinimumVersion": None,
            "validOperatingSystemBuildRanges": [],
        }])
        all_rows = generate(dump, {})["rows"]
        rows = settings(all_rows)
        self.assertEqual([r["setting_id"] for r in rows], ["bitLockerEnabled"])
        self.assertEqual(rows[0]["required_value"], "true")
        self.assertEqual(rows[0]["mode"], "compliance")
        self.assertEqual(rows[0]["platform"], "windows10")
        # displayName is carried by the name row, never as a second settings row.
        self.assertEqual([r["setting_id"] for r in all_rows],
                         ["@displayName", "bitLockerEnabled"])

    def test_windows_update_type_is_not_read_as_bare_windows(self):
        """Longest-prefix matching -- windows10CompliancePolicy vs windowsUpdate...."""
        self.assertEqual(
            gb.platform_from_odata("#microsoft.graph.windowsUpdateForBusinessConfiguration"),
            "windows10")
        self.assertEqual(
            gb.platform_from_odata("#microsoft.graph.iosGeneralDeviceConfiguration"), "iOS")
        self.assertEqual(
            gb.platform_from_odata("#microsoft.graph.macOSCustomConfiguration"), "macOS")

    def test_graph_annotations_are_not_settings(self):
        dump = mini_dump(device_configurations=[bag(
            "X", "#microsoft.graph.windows10GeneralConfiguration",
            {"@odata.context": "ignored", "passwordRequired@odata.type": "ignored",
             "passwordRequired": True})])
        self.assertEqual([r["setting_id"] for r in settings(generate(dump, {})["rows"])],
                         ["passwordRequired"])


class Scope(unittest.TestCase):

    def test_unassigned_objects_are_excluded_with_a_reason(self):
        dump = mini_dump([
            policy("Live", "windows10", [choice("a", "a_1")]),
            policy("INACTIVE Audit Mode", "windows10", [choice("b", "b_1")], assigned=False),
        ])
        doc = generate(dump, {})
        self.assertEqual({r["object_name"] for r in doc["rows"]}, {"Live"})
        self.assertEqual(doc["meta"]["scope"]["excluded_objects"],
                         [{"collection": "configurationPolicies",
                           "object_id": guid_for("INACTIVE Audit Mode"),
                           "name": "INACTIVE Audit Mode", "platform": "windows10",
                           "reason": "unassigned"}])

    def test_assignment_signal_disagreement_is_recorded_not_resolved_silently(self):
        dump = mini_dump([policy("Odd", "windows10", [choice("a", "a_1")])])
        dump["configurationPolicies"][0]["isAssigned"] = False  # but assignments is non-empty
        doc = generate(dump, {})
        disagreements = doc["meta"]["scope"]["assignment_disagreements"]
        self.assertEqual(len(disagreements), 1)
        self.assertEqual(disagreements[0]["name"], "Odd")
        self.assertEqual(disagreements[0]["object_id"], guid_for("Odd"))
        # Included, not dropped -- omitting a live setting is the worse failure.
        self.assertEqual(len(doc["rows"]), 2)  # name row + the setting

    def test_leaf_counts_separate_scalar_from_collection(self):
        """meta carries the 84/56/2-style scalar figure so a run stays checkable."""
        instance = simple_collection("list_setting", ["x"])
        doc = generate(mini_dump([policy("P", "windows10",
                                         [choice("a", "a_1"), instance])]), {})
        self.assertEqual(doc["meta"]["scope"]["leaf_counts"]["windows10"],
                         {"policies": 1, "scalar": 1, "collection": 1, "rows": 2})

    def test_counts_sum_to_row_count_and_objects_are_counted(self):
        doc = generate(mixed_dump(), {})
        meta = doc["meta"]
        self.assertEqual(sum(sum(p.values()) for p in meta["counts"].values()),
                         meta["row_count"])
        self.assertEqual(meta["counts"], {
            "windows10": {"configurationPolicies": 3},
            "macOS": {"deviceConfigurations": 3},
            "iOS": {"deviceCompliancePolicies": 2}})
        self.assertEqual(meta["scope"]["in_scope_objects"], {
            "windows10": {"configurationPolicies": 1},
            "macOS": {"deviceConfigurations": 1},
            "iOS": {"deviceCompliancePolicies": 1}})
        self.assertEqual(meta["generator_version"], "2.0")

    def test_an_assigned_object_with_no_settings_still_has_its_name_row(self):
        """Real case: 'Default Device Features Configuration' (macOS) is assigned and
        carries only metadata. It is in scope, so it is visible -- as its name row."""
        dump = mini_dump(device_configurations=[bag(
            "Default Device Features Configuration",
            "#microsoft.graph.macOSDeviceFeaturesConfiguration", {"version": 1})])
        rows = generate(dump, {})["rows"]
        self.assertEqual([r["setting_id"] for r in rows], ["@displayName"])


class Integrity(unittest.TestCase):

    def test_a_repeated_object_id_is_refused_not_merged(self):
        guid = "00000000-0000-0000-0000-0000000000ff"
        dump = mini_dump([policy("One", "windows10", [choice("a", "a_1")], guid=guid),
                          policy("Two", "windows10", [choice("a", "a_2")], guid=guid)])
        with self.assertRaises(gb.GeneratorError) as ctx:
            generate(dump, {})
        self.assertIn("duplicate row_key", str(ctx.exception))

    def test_an_object_without_an_id_is_refused(self):
        dump = mini_dump([policy("P", "windows10", [choice("a", "a_1")])])
        del dump["configurationPolicies"][0]["id"]
        with self.assertRaises(gb.GeneratorError):
            generate(dump, {})

    def test_an_empty_dump_is_refused_by_the_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            dump = Path(tmp) / "2026-09-24" / "intune-config-export.json"
            write_json(dump, {"mobileApps": []})
            code, _, _ = run_cli(["--dump", str(dump), "--out", str(Path(tmp) / "o.json"),
                                  "--id-map", str(Path(tmp) / "id-map.json"),
                                  "--generated-at", GENERATED_AT])
            self.assertIn("none of the expected collections", str(code))
            self.assertFalse((Path(tmp) / "o.json").exists())


# --------------------------------------------------------------------------- id map

class IdMapSchema(unittest.TestCase):

    def cli(self, tmp, id_map_path):
        dump = Path(tmp) / "2026-09-24" / "intune-config-export.json"
        write_json(dump, mixed_dump())
        out = Path(tmp) / "2026-09-24" / "baseline-rows.json"
        code, _, _ = run_cli(["--dump", str(dump), "--out", str(out),
                              "--id-map", str(id_map_path), "--generated-at", GENERATED_AT])
        return code, out

    def test_v1_map_is_refused_with_delete_and_regenerate(self):
        with tempfile.TemporaryDirectory() as tmp:
            id_map = Path(tmp) / "id-map.json"
            v1 = {"configurationPolicies|windows10|default laps policy|x": "BP-WIN-0001"}
            write_json(id_map, v1)
            original = id_map.read_bytes()
            code, out = self.cli(tmp, id_map)
            message = str(code)
            self.assertIn("v1 map", message)
            self.assertIn("Delete", message)
            self.assertIn("regenerate", message)
            self.assertEqual(id_map.read_bytes(), original, "a refused map was rewritten")
            self.assertFalse(out.exists(), "output written despite the refusal")

    def test_unknown_schema_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "id-map.json"
            write_json(path, {"schema": 3, "ids": {}})
            with self.assertRaises(gb.GeneratorError):
                gb.load_id_map(path)

    def test_malformed_or_shared_ids_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "id-map.json"
            write_json(path, {"schema": 2, "ids": {"a|b|c": "WIN-1"}})
            with self.assertRaises(gb.GeneratorError):
                gb.load_id_map(path)
            write_json(path, {"schema": 2, "ids": {"a|b|c": "BP-WIN-0001",
                                                   "a|b|d": "BP-WIN-0001"}})
            with self.assertRaises(gb.GeneratorError) as ctx:
                gb.load_id_map(path)
            self.assertIn("BP-WIN-0001", str(ctx.exception))

    def test_invalid_json_map_is_refused_not_restarted(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "id-map.json"
            path.write_text("{not json", encoding="utf-8")
            with self.assertRaises(gb.GeneratorError):
                gb.load_id_map(path)

    def test_fresh_map_is_schema_2_in_reading_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            id_map = Path(tmp) / "id-map.json"
            code, out = self.cli(tmp, id_map)
            self.assertEqual(code, 0)
            document = json.loads(id_map.read_text(encoding="utf-8"))
            self.assertEqual(list(document), ["schema", "ids"])
            self.assertEqual(document["schema"], 2)
            rows = json.loads(out.read_text(encoding="utf-8"))["rows"]
            self.assertEqual(document["ids"], {r["row_key"]: r["id"] for r in rows})
            for prefix in ("WIN", "MAC", "IOS"):
                numbers = [int(r["id"][-4:]) for r in rows if r["id"][3:6] == prefix]
                self.assertEqual(numbers, list(range(1, len(numbers) + 1)), prefix)

    def test_a_second_run_leaves_the_map_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            id_map = Path(tmp) / "id-map.json"
            self.cli(tmp, id_map)
            first = id_map.read_bytes()
            self.cli(tmp, id_map)
            self.assertEqual(id_map.read_bytes(), first)


# ----------------------------------------------------------------- display resolution

def definition(definition_id, display_name, options=None, odata="ChoiceSettingDefinition"):
    body = {"@odata.type": "#microsoft.graph.deviceManagementConfiguration" + odata,
            "id": definition_id, "displayName": display_name}
    if options is not None:
        body["options"] = [{"itemId": item, "displayName": label} for item, label in options]
    return body


class DisplayResolution(unittest.TestCase):

    def setUp(self):
        self.definitions = {
            "_unresolved": ["never_fetched"],
            "choice_setting": definition("choice_setting", "Choice Setting",
                                         [("choice_setting_0", "Off"),
                                          ("choice_setting_1", "On")]),
            "simple_setting": definition("simple_setting", "Simple Setting",
                                         odata="SimpleSettingDefinition"),
            "multi_choice": definition("multi_choice", "Multi Choice",
                                       [("multi_choice_a", "Alpha"),
                                        ("multi_choice_b", "Bravo")],
                                       odata="ChoiceSettingCollectionDefinition"),
            "multi_simple": definition("multi_simple", "Multi Simple",
                                       odata="SimpleSettingCollectionDefinition"),
            # Same key as a property-bag property -- must still never label it.
            "passwordRequired": definition("passwordRequired", "INVENTED LABEL",
                                           odata="SimpleSettingDefinition"),
        }

    def rows(self, instances, definitions="default", bags=None):
        defs = self.definitions if definitions == "default" else definitions
        doc = generate(mini_dump([policy("P", "windows10", instances)],
                                 device_configurations=bags), {}, definitions=defs)
        return doc, {r["setting_id"]: r for r in doc["rows"]}

    def test_choice_hit_labels_setting_and_value(self):
        doc, rows = self.rows([choice("choice_setting", "choice_setting_1")])
        row = rows["choice_setting"]
        self.assertEqual(row["setting_name"], "Choice Setting")
        self.assertEqual(row["display_value"], "On")
        self.assertEqual(row["required_value"], "choice_setting_1")
        self.assertEqual(doc["meta"]["display_resolution"]["mode"], "catalog")
        self.assertEqual((doc["meta"]["display_resolution"]["resolved"],
                          doc["meta"]["display_resolution"]["unresolved"]), (1, 0))

    def test_option_miss_falls_back_to_raw_and_is_counted(self):
        doc, rows = self.rows([choice("choice_setting", "choice_setting_7")])
        row = rows["choice_setting"]
        self.assertEqual(row["setting_name"], "Choice Setting")
        self.assertEqual(row["display_value"], "choice_setting_7")
        resolution = doc["meta"]["display_resolution"]
        self.assertEqual((resolution["resolved"], resolution["unresolved"]), (0, 1))
        self.assertEqual(resolution["missing_options"],
                         ["choice_setting = choice_setting_7"])

    def test_definition_miss_falls_back_to_setting_id_and_is_counted(self):
        doc, rows = self.rows([choice("not_in_catalog", "not_in_catalog_1")])
        row = rows["not_in_catalog"]
        self.assertEqual(row["setting_name"], "not_in_catalog")
        self.assertEqual(row["display_value"], "not_in_catalog_1")
        resolution = doc["meta"]["display_resolution"]
        self.assertEqual(resolution["unresolved"], 1)
        self.assertEqual(resolution["missing_definitions"], ["not_in_catalog"])
        self.assertEqual(resolution["unfetched_at_export"], ["never_fetched"])

    def test_collections_join_display_values_and_keep_raw_json(self):
        _, rows = self.rows([choice_collection("multi_choice",
                                               ["multi_choice_b", "multi_choice_a"]),
                             simple_collection("multi_simple", ["x", "y"])])
        self.assertEqual(rows["multi_choice"]["display_value"], "Bravo; Alpha")
        self.assertEqual(rows["multi_choice"]["required_value"],
                         '["multi_choice_b","multi_choice_a"]')
        self.assertEqual(rows["multi_simple"]["display_value"], "x; y")
        self.assertEqual(rows["multi_simple"]["required_value"], '["x","y"]')

    def test_a_partial_collection_miss_falls_back_whole(self):
        doc, rows = self.rows([choice_collection("multi_choice",
                                                 ["multi_choice_a", "multi_choice_z"])])
        self.assertEqual(rows["multi_choice"]["display_value"],
                         '["multi_choice_a","multi_choice_z"]')
        self.assertEqual(doc["meta"]["display_resolution"]["unresolved"], 1)

    def test_simple_value_gets_a_label_but_keeps_its_value(self):
        _, rows = self.rows([simple("simple_setting", 900)])
        self.assertEqual(rows["simple_setting"]["setting_name"], "Simple Setting")
        self.assertEqual(rows["simple_setting"]["display_value"], "900")

    def test_property_bag_rows_never_get_an_invented_label(self):
        bags = [bag("Mac", "#microsoft.graph.macOSGeneralDeviceConfiguration",
                    {"passwordRequired": True})]
        _, rows = self.rows([choice("choice_setting", "choice_setting_1")], bags=bags)
        self.assertEqual(rows["passwordRequired"]["setting_name"], "passwordRequired")
        self.assertEqual(rows["passwordRequired"]["display_value"], "true")

    def test_lookup_falls_back_to_case_insensitive(self):
        _, rows = self.rows([choice("CHOICE_Setting", "CHOICE_SETTING_1")])
        self.assertEqual(rows["CHOICE_Setting"]["setting_name"], "Choice Setting")
        self.assertEqual(rows["CHOICE_Setting"]["display_value"], "On")

    def test_duplicate_occurrence_keeps_its_disambiguator_in_the_label(self):
        _, rows = self.rows([choice("choice_setting", "choice_setting_0"),
                             choice("choice_setting", "choice_setting_1")])
        self.assertEqual(rows["choice_setting#2"]["setting_name"], "Choice Setting #2")
        self.assertEqual(rows["choice_setting#2"]["display_value"], "On")

    def test_resolution_never_changes_the_fields_the_diff_reads(self):
        instances = [choice("choice_setting", "choice_setting_1"),
                     choice("not_in_catalog", "x"), simple("simple_setting", 3)]
        plain = generate(mini_dump([policy("P", "windows10", instances)]), {})
        labelled = generate(mini_dump([policy("P", "windows10", instances)]), {},
                            definitions=self.definitions)
        project = lambda doc: [(r["row_key"], r["id"], r["required_value"], r["mode"])
                               for r in doc["rows"]]
        self.assertEqual(project(plain), project(labelled))
        self.assertNotEqual([r["display_value"] for r in plain["rows"]],
                            [r["display_value"] for r in labelled["rows"]])

    def test_without_definitions_mode_is_none(self):
        doc = generate(mixed_dump(), {})
        resolution = doc["meta"]["display_resolution"]
        self.assertEqual((resolution["mode"], resolution["resolved"],
                          resolution["unresolved"]), ("none", 0, 0))
        self.assertIsNone(doc["meta"]["definitions_sha256"])
        for row in doc["rows"]:
            self.assertEqual(row["display_value"], row["required_value"])

    def test_the_synthetic_fixture_can_never_pass_for_catalog_data(self):
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(fixture["_unresolved"], sorted(fixture["_unresolved"]))
        bodies = {k: v for k, v in fixture.items() if not k.startswith("_")}
        self.assertTrue(4 <= len(bodies) <= 12, "keep the fixture small")
        for key, body in bodies.items():
            self.assertEqual(body["id"], key)
            self.assertTrue(body["displayName"].startswith("SYNTHETIC"), key)
            for option in body.get("options", []):
                self.assertTrue(option["displayName"].startswith("SYNTHETIC"),
                                option["itemId"])

    def test_the_synthetic_fixture_resolves_real_shaped_rows(self):
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        doc = generate(mini_dump([policy("Default LAPS Policy", "windows10", [
            choice("device_vendor_msft_laps_policies_backupdirectory",
                   "device_vendor_msft_laps_policies_backupdirectory_1"),
            choice("device_vendor_msft_laps_policies_passwordcomplexity",
                   "device_vendor_msft_laps_policies_passwordcomplexity_7"),
        ])]), {}, definitions=fixture)
        rows = {r["setting_id"]: r for r in doc["rows"]}
        hit = rows["device_vendor_msft_laps_policies_backupdirectory"]
        self.assertEqual(hit["display_value"], "SYNTHETIC Back up to the directory")
        miss = rows["device_vendor_msft_laps_policies_passwordcomplexity"]
        self.assertEqual(miss["display_value"], miss["required_value"])
        self.assertEqual((doc["meta"]["display_resolution"]["resolved"],
                          doc["meta"]["display_resolution"]["unresolved"]), (1, 1))


# ------------------------------------------------------------------------ sort order

class SortOrder(unittest.TestCase):

    def test_platform_then_collection_then_name_then_object_id(self):
        dump = mini_dump(
            [policy("zeta", "iOS", [choice("a", "a_1")]),
             policy("Alpha", "macOS", [choice("a", "a_1")]),
             policy("Bravo", "windows10", [choice("a", "a_1")]),
             policy("alpha", "windows10", [choice("a", "a_1")]),
             policy("Dup", "windows10", [choice("a", "a_1")],
                    guid="00000000-0000-0000-0000-000000000002"),
             policy("Dup", "windows10", [choice("a", "a_1")],
                    guid="00000000-0000-0000-0000-000000000001"),
             policy("Gamma", "android", [choice("a", "a_1")])],
            device_configurations=[bag("Aardvark",
                                       "#microsoft.graph.windows10GeneralConfiguration",
                                       {"x": 1})],
            compliance=[bag("Aaa", "#microsoft.graph.windows10CompliancePolicy",
                            {"y": True})])
        objects = []
        for row in generate(dump, {})["rows"]:
            item = (row["platform"], row["collection"], row["object_name"],
                    row["object_id"][-1:])
            if not objects or objects[-1] != item:
                objects.append(item)
        self.assertEqual([o[:3] for o in objects], [
            ("windows10", "configurationPolicies", "alpha"),
            ("windows10", "configurationPolicies", "Bravo"),
            ("windows10", "configurationPolicies", "Dup"),
            ("windows10", "configurationPolicies", "Dup"),
            ("windows10", "deviceConfigurations", "Aardvark"),
            ("windows10", "deviceCompliancePolicies", "Aaa"),
            ("macOS", "configurationPolicies", "Alpha"),
            ("iOS", "configurationPolicies", "zeta"),
            ("android", "configurationPolicies", "Gamma"),
        ])
        # Same name: object id breaks the tie.
        self.assertEqual([o[3] for o in objects[2:4]], ["1", "2"])

    def test_name_row_first_even_when_setting_ids_sort_before_at(self):
        """'#', '!' and every digit sort before '@' in ASCII. The name row's place is a
        key component of its own, not an accident of '@' sorting early."""
        rows = generate(mini_dump([policy("P", "windows10", [
            choice("Zed", "z"), choice("0first", "0"), choice("!bang", "b"),
            choice("#hash", "h"), choice("alpha", "a")])]), {})["rows"]
        self.assertEqual([r["setting_id"] for r in rows],
                         ["@displayName", "!bang", "#hash", "0first", "alpha", "Zed"])

    def test_name_row_is_first_in_every_object(self):
        doc = generate(mixed_dump(), {})
        seen = set()
        for row in doc["rows"]:
            obj = (row["collection"], row["object_id"])
            if obj not in seen:
                seen.add(obj)
                self.assertEqual(row["setting_id"], gb.NAME_SETTING_ID, obj)
            else:
                self.assertNotEqual(row["setting_id"], gb.NAME_SETTING_ID, obj)
        self.assertEqual(len(seen), 3)


class Determinism(unittest.TestCase):

    def setUp(self):
        self.dump = mini_dump([
            policy("Zulu Policy", "windows10", [choice("z", "z_1")]),
            policy("Alpha Policy", "macOS", [choice("a", "a_1")]),
        ])

    def test_byte_identical_across_runs(self):
        id_map = {}
        first = json.dumps(generate(self.dump, id_map), indent=2)
        second = json.dumps(generate(self.dump, dict(id_map)), indent=2)
        self.assertEqual(first, second)

    def test_source_ordering_does_not_change_output(self):
        """Graph does not promise list order. A reordered dump must diff clean."""
        forward = generate(self.dump, {})
        self.dump["configurationPolicies"].reverse()
        reversed_run = generate(self.dump, {})
        self.assertEqual([r["row_key"] for r in forward["rows"]],
                         [r["row_key"] for r in reversed_run["rows"]])

    def test_source_key_order_does_not_change_output(self):
        forward = json.dumps(generate(mixed_dump(), {}), indent=2)
        shuffled = mixed_dump()
        for collection in gb.COLLECTIONS:
            shuffled[collection] = [dict(reversed(list(obj.items())))
                                    for obj in shuffled[collection]]
        self.assertEqual(forward, json.dumps(generate(shuffled, {}), indent=2))

    def test_build_rows_never_reads_the_clock(self):
        """generated_at is an argument. If a now() crept in, this catches it.

        Asserted as 'the module never imported a clock' rather than by grepping the
        source for 'datetime' -- the docstrings say the word precisely to explain why it
        is absent, and a test that fails on its own rationale gets deleted, not fixed.
        """
        doc = gb.build_rows(self.dump, GENERATED_AT, "deadbeef", "dump.json")
        self.assertEqual(doc["meta"]["generated_at"], GENERATED_AT)
        for clock in ("datetime", "time", "calendar"):
            self.assertFalse(hasattr(gb, clock),
                             "generate_baseline imported %s -- output is no longer "
                             "reproducible" % clock)

    def test_cli_outputs_are_byte_identical_across_runs_and_folders(self):
        """The whole CLI: baseline json, cycle record, markdown and id map. Two separate
        folders, so no absolute path can leak into any output either."""
        outputs = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp) / "dumps" / "2026-09-24"
                dump = folder / "intune-config-export.json"
                write_json(dump, mixed_dump())
                id_map = Path(tmp) / "dumps" / "id-map.json"
                common = ["--dump", str(dump), "--id-map", str(id_map),
                          "--generated-at", GENERATED_AT,
                          "--definitions", str(FIXTURE)]
                for _ in range(2):
                    code, _, _ = run_cli(common + [
                        "--out", str(folder / "baseline-rows.json"),
                        "--cycle-record", str(folder / "README.md")])
                    self.assertEqual(code, 0)
                    code, _, _ = run_cli(common + ["--out", str(Path(tmp) / "win.md"),
                                                   "--format", "markdown",
                                                   "--platform", "windows"])
                    self.assertEqual(code, 0)
                    outputs.append(tuple(p.read_bytes() for p in (
                        folder / "baseline-rows.json", folder / "README.md",
                        Path(tmp) / "win.md", id_map)))
        self.assertEqual(len(set(outputs)), 1, "CLI output differs between runs")


# -------------------------------------------------------------------------- markdown

class Markdown(unittest.TestCase):

    def render(self, dump, definitions=None, ratified_date=None):
        doc = generate(dump, {}, definitions=definitions)
        doc["rows"] = [gb.ordered(r) for r in doc["rows"]]
        return gb.to_markdown(doc, ratified_date)

    def test_pipes_in_a_value_cannot_break_the_table(self):
        body = self.render(mini_dump([policy("P", "windows10",
                                             [choice("a", "value|with|pipes")])]))
        row = [l for l in body.splitlines() if l.startswith("| BP-") and "value" in l][0]
        self.assertEqual(row.count("|") - row.count("\\|"), 9)  # 8 columns + closing pipe

    def test_headings_are_not_swallowed_by_the_preceding_table(self):
        lines = self.render(mini_dump([policy("Alpha", "windows10", [choice("a", "a_1")]),
                                       policy("Bravo", "windows10",
                                              [choice("b", "b_1")])])).splitlines()
        for index, line in enumerate(lines):
            if line.startswith("### ") and index:
                self.assertEqual(lines[index - 1], "",
                                 "no blank line before %r" % line)

    def test_authority_carries_the_generated_at_date(self):
        body = self.render(mini_dump([policy("P", "windows10", [choice("a", "a_1")])]))
        self.assertIn("bitpool:ratified 2026-09-24", body)

    def test_columns_and_cells_follow_the_contract(self):
        definitions = {"choice_setting": definition(
            "choice_setting", "Choice Setting", [("choice_setting_1", "On")])}
        body = self.render(mini_dump([policy("Pol", "windows10", [
            choice("choice_setting", "choice_setting_1"), choice("raw_one", "raw_one_0")])]),
            definitions=definitions, ratified_date="2026-06-30")
        self.assertIn(gb.MD_HEADER, body)
        table = [l for l in body.splitlines() if l.startswith("| BP-")]
        self.assertEqual(len(table), 3)
        self.assertTrue(table[0].startswith("| BP-WIN-0001 | Policy name | `Pol` |"), table[0])
        self.assertIn("| identity |", table[0])
        self.assertIn("`@displayName = Pol`", table[0])
        # Resolved: labels in plain text, raw pair in Verify.
        self.assertIn("| Choice Setting | On | bitpool:ratified 2026-06-30 | enforced |",
                      table[1])
        self.assertTrue(table[1].endswith("| none | `choice_setting = choice_setting_1` |"))
        # Unresolved: the raw value, shown as code.
        self.assertIn("| `raw_one` | `raw_one_0` |", table[2])
        self.assertIn("Object ID `%s`" % guid_for("Pol"), body)

    def test_a_platform_block_carries_only_that_platform(self):
        dump = mixed_dump()
        dump["configurationPolicies"].append(policy("Old Mac", "macOS", [choice("a", "a")],
                                                    assigned=False))
        dump["configurationPolicies"].append(policy("Old Win", "windows10",
                                                    [choice("a", "a")], assigned=False))
        doc = generate(dump, {}, platform_filter="windows")
        doc["rows"] = [gb.ordered(r) for r in doc["rows"]]
        body = gb.to_markdown(doc)
        self.assertIn("### Default LAPS Policy", body)
        self.assertNotIn("Default Device Restrictions Configuration", body)
        self.assertIn("Old Win", body)
        self.assertNotIn("Old Mac", body)
        self.assertTrue(body.index("### In scope") < body.index("### Excluded, and why")
                        < body.index("### Default LAPS Policy"))

    def test_untrusted_names_and_values_are_escaped(self):
        hostile = "<script>alert(1)</script> *bold* [x](http://e) |pipe| `tick`"
        body = self.render(mini_dump([policy(hostile, "windows10", [
            simple("s", "a`b|c\nd")])]))
        # Inside a code span '<' renders as literal text, so only prose is checked.
        prose = re.sub(r"(`+)(.+?)\1", "", body)
        self.assertNotIn("<script", prose)
        self.assertNotIn("[x](http", prose)
        self.assertIn("&lt;script", prose)
        for line in body.splitlines():
            if line.startswith("| BP-"):
                self.assertEqual(line.count("|") - line.count("\\|"), 9, line)
        self.assertIn("``a`b\\|c\\nd``", body)

    def test_a_backslash_before_a_pipe_cannot_open_a_cell(self):
        """'a\\|b' naively escaped is 'a\\\\|b': an escaped backslash, then a LIVE
        delimiter. The backslash run is doubled so the pipe stays escaped."""
        body = self.render(mini_dump([policy("P", "windows10", [simple("s", "a\\|b")])]))
        self.assertIn("`a\\\\\\|b`", body)
        for line in body.splitlines():
            if line.startswith("| BP-"):
                live = len(re.findall(r"(?<!\\)(?:\\\\)*\|", line))
                self.assertEqual(live, 9, line)

    def test_cli_markdown_authority_defaults_to_the_dated_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            dump = Path(tmp) / "2026-06-30" / "intune-config-export.json"
            write_json(dump, mixed_dump())
            out = Path(tmp) / "win.md"
            code, _, _ = run_cli(["--dump", str(dump), "--out", str(out),
                                  "--id-map", str(Path(tmp) / "id-map.json"),
                                  "--generated-at", "2026-07-01T09:00:00Z",
                                  "--format", "markdown", "--platform", "windows"])
            self.assertEqual(code, 0)
            text = out.read_text(encoding="utf-8")
            self.assertIn("bitpool:ratified 2026-06-30", text)
            self.assertNotIn("2026-07-01", text)
            self.assertNotIn("GENERATED:", text, "the markers belong to the ratify step")


# ---------------------------------------------------------------------- cycle record

class CycleRecord(unittest.TestCase):

    def build(self, tmp, manifest=None, extra_files=(), argv_extra=()):
        folder = Path(tmp) / "dumps" / "2026-09-25"
        dump = folder / "intune-config-export.json"
        write_json(dump, mixed_dump())
        (folder / "intune-config-export-readable.json").write_text("{}\n", encoding="utf-8")
        for name in extra_files:
            (folder / name).write_text("x\n", encoding="utf-8")
        if manifest is not None:
            write_json(folder / "collection-manifest.json", manifest(dump))
        code, out, err = run_cli([
            "--dump", str(dump), "--out", str(folder / "baseline-rows.json"),
            "--id-map", str(Path(tmp) / "dumps" / "id-map.json"),
            "--generated-at", "2026-09-25T03:14:15Z",
            "--cycle-record", str(folder / "README.md")] + list(argv_extra))
        record = (folder / "README.md").read_text(encoding="utf-8") \
            if (folder / "README.md").exists() else None
        return code, record, err, folder

    ABSENT = object()

    @classmethod
    def manifest(cls, sha_override=None, upn="collector@example.test", incidents=ABSENT,
                 git_dirty=ABSENT):
        def make(dump):
            data = dump.read_bytes()
            body = {"schema": 1, "collected_at_utc": "2026-09-25T03:14:15Z",
                    "collection_date": "2026-09-25",
                    "collector": {"upn": upn, "object_id": "11111111-2222-3333-4444-555555555555",
                                  "source": "access-token claims"},
                    "tenant_id": "00000000-0000-0000-0000-00000000000a",
                    "client_id": "00000000-0000-0000-0000-00000000000b",
                    "tool": {"name": "export-intune-config.sh", "git_commit": None},
                    "files": {"intune-config-export.json": {
                        "sha256": sha_override or hashlib.sha256(data).hexdigest(),
                        "bytes": len(data)}}}
            if incidents is not cls.ABSENT:
                body["incidents"] = incidents
            if git_dirty is not cls.ABSENT:
                body["tool"]["git_dirty"] = git_dirty
            return body
        return make

    @staticmethod
    def row(record, label):
        found = [l for l in record.splitlines() if l.startswith("| %s | " % label)]
        assert len(found) == 1, (label, found)
        return found[0]

    def frontmatter(self, record):
        self.assertTrue(record.startswith("---\n"))
        return record.split("---\n")[1]

    def test_frontmatter_is_a_valid_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, record, _, _ = self.build(tmp, self.manifest())
            self.assertEqual(code, 0)
            front = self.frontmatter(record)
            for line in ("type: Record", "doc_type: record", "status: active",
                         "  - security-team", "  - auditors", "  - ai-agents",
                         "  - internal", "  - drata:DCF-12", "last_reviewed: 2026-09-25",
                         "risk_level: high", "requires_admin: false"):
                self.assertIn(line + "\n", front)
            title = [l for l in front.splitlines() if l.startswith("title: ")][0][7:]
            self.assertIn("\n# %s\n" % title, record, "title must match the H1")
            for line in front.splitlines():
                if line.startswith(("title:", "description:")):
                    self.assertNotIn(": ", line.split(": ", 1)[1], "unquoted YAML colon")

    def test_lists_every_input_file_with_its_sha256_and_nothing_downstream(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, record, _, folder = self.build(
                tmp, self.manifest(),
                extra_files=("setting-definitions.json", "diff-vs-2026-06-24.md",
                             "diff-vs-2026-06-24.json", "evidence-pack.html", ".hidden"))
            for name in ("baseline-rows.json", "collection-manifest.json",
                         "intune-config-export-readable.json", "intune-config-export.json",
                         "setting-definitions.json"):
                data = (folder / name).read_bytes()
                self.assertIn("| `%s` | %d | `%s` |"
                              % (name, len(data), hashlib.sha256(data).hexdigest()),
                              record, name)
            for name in ("diff-vs-2026-06-24.md", "evidence-pack.html", ".hidden",
                         "README.md"):
                self.assertNotIn("| `%s` |" % name, record)
            self.assertIn("matches the manifest", record)
            self.assertIn("written by this run", record)

    def test_without_a_manifest_the_collector_is_not_recorded_never_invented(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, record, _, _ = self.build(tmp)
            self.assertEqual(code, 0)
            self.assertIn("| Collector | not recorded", record)
            self.assertIn("| Collected at (UTC) | not recorded", record)
            self.assertIn("| Incidents | not recorded", record)
            self.assertIn("from the folder name", record)
            self.assertNotIn("@", record.split("## Collection")[1].split("## Files")[0])

    def test_with_a_manifest_the_collector_and_instant_are_stated(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, record, _, _ = self.build(tmp, self.manifest())
            self.assertIn("`collector@example.test`", record)
            self.assertIn("| Collected at (UTC) | `2026-09-25T03:14:15Z` |", record)

    def test_a_null_collector_is_flagged_not_filled_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, record, err, _ = self.build(tmp, self.manifest(upn=None))
            self.assertIn("| Collector | **not determined**", record)
            self.assertIn("collector identity is null", err)

    def test_a_hash_mismatch_against_the_manifest_is_loud(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, record, err, _ = self.build(tmp, self.manifest(sha_override="0" * 64))
            self.assertIn("**MISMATCH**", record)
            self.assertIn("does not match its manifest hash", err)

    def test_ratification_is_pointed_elsewhere_not_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, record, _, _ = self.build(tmp, self.manifest())
            self.assertIn("`../RATIFIED`", record)
            self.assertIn("approval header", record)
            self.assertIn("not here", record)
            self.assertNotIn("bitpool:ratified", record)

    def test_counts_exclusions_and_resolution_are_stated(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, record, _, _ = self.build(tmp, self.manifest(),
                                         argv_extra=["--definitions", str(FIXTURE)])
            self.assertIn("| **Total** | | **3** | **5** | **3** | **8** |", record)
            self.assertIn("## Scope exclusions", record)
            self.assertIn("| Mode | `catalog`", record)
            self.assertIn("| Resolved | 2 |", record)

    def test_readme_is_an_alias_for_cycle_record(self):
        """run_config_cycle.py probes --help for --readme and passes that spelling."""
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "2026-09-24"
            write_json(folder / "intune-config-export.json", mixed_dump())
            code, _, _ = run_cli(["--dump", str(folder / "intune-config-export.json"),
                                  "--out", str(folder / "baseline-rows.json"),
                                  "--id-map", str(Path(tmp) / "id-map.json"),
                                  "--generated-at", GENERATED_AT,
                                  "--readme", str(folder / "README.md")])
            self.assertEqual(code, 0)
            self.assertTrue((folder / "README.md").read_text(encoding="utf-8")
                            .startswith("---\ntype: Record\n"))

    def test_a_manifest_without_incidents_or_git_dirty_says_not_recorded(self):
        """An older manifest. Absent is stated as absent -- never read as clean."""
        with tempfile.TemporaryDirectory() as tmp:
            _, record, _, _ = self.build(tmp, self.manifest())
            self.assertEqual(self.row(record, "Incidents"),
                             "| Incidents | not recorded — the manifest has no `incidents` "
                             "field |")
            self.assertIn("working tree not recorded (no `tool.git_dirty` in the "
                          "manifest)", self.row(record, "Tool"))
            self.assertNotIn("none recorded", record)
            self.assertNotIn("clean", self.row(record, "Tool"))

    def test_a_clean_collection_says_none_recorded_and_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, record, err, _ = self.build(tmp, self.manifest(incidents=[],
                                                                 git_dirty=False))
            self.assertEqual(code, 0)
            self.assertEqual(self.row(record, "Incidents"), "| Incidents | none recorded |")
            self.assertTrue(self.row(record, "Tool").endswith(" · working tree clean |"))
            self.assertNotIn("incident", err)
            self.assertNotIn("uncommitted", err)

    def test_an_accepted_incomplete_collection_is_loud_and_escaped(self):
        """The record of an --accept-incomplete dump must not look like a clean one."""
        incidents = ["deviceConfigurations: page 2 returned HTTP 403",
                     "<script>x</script> | a pipe | and `ticks`"]
        with tempfile.TemporaryDirectory() as tmp:
            code, record, err, _ = self.build(tmp, self.manifest(incidents=incidents))
            self.assertEqual(code, 0)
            row = self.row(record, "Incidents")
            self.assertIn("**2 recorded**", row)
            self.assertIn("INCOMPLETE", row)
            self.assertIn("`--accept-incomplete`", row)
            self.assertIn("1. deviceConfigurations: page 2 returned HTTP 403<br>2. ", row)
            self.assertIn("&lt;script>", row)
            self.assertNotIn("<script", row)
            # Two cells: three live pipes, whatever the incident text holds.
            self.assertEqual(len(re.findall(r"(?<!\\)(?:\\\\)*\|", row)), 3, row)
            self.assertIn("2 incident(s) recorded in collection-manifest.json", err)

    def test_a_dirty_or_undetermined_working_tree_is_stated(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, record, err, _ = self.build(tmp, self.manifest(incidents=[], git_dirty=True))
            self.assertIn("working tree **dirty** — the exporter differed from that "
                          "commit when it ran", self.row(record, "Tool"))
            self.assertIn("uncommitted changes", err)
        with tempfile.TemporaryDirectory() as tmp:
            _, record, _, _ = self.build(tmp, self.manifest(incidents=None, git_dirty=None))
            self.assertIn("working tree **not determined**", self.row(record, "Tool"))
            self.assertIn("| Incidents | **not determined**", record)

    def test_the_record_refuses_a_platform_filter(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, record, _, _ = self.build(tmp, argv_extra=["--platform", "windows"])
            self.assertIn("cannot be combined with --platform", str(code))
            self.assertIsNone(record)


# ---------------------------------------------------------------- markdown preview

class MarkdownPreview(unittest.TestCase):
    """--format markdown is a preview. It is not the block ratify injects (ratify renders
    its own), and a look at a dump must never reserve numbers in the permanent map."""

    def cli(self, tmp, dump_obj, fmt, extra=()):
        folder = Path(tmp) / "2026-09-24"
        write_json(folder / "intune-config-export.json", dump_obj)
        out = Path(tmp) / ("win.md" if fmt == "markdown" else "baseline-rows.json")
        code, stdout, stderr = run_cli([
            "--dump", str(folder / "intune-config-export.json"), "--out", str(out),
            "--id-map", str(Path(tmp) / "id-map.json"), "--generated-at", GENERATED_AT,
            "--format", fmt] + list(extra))
        return code, stdout, out

    def test_a_preview_never_creates_the_id_map(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, stdout, out = self.cli(tmp, mixed_dump(), "markdown")
            self.assertEqual(code, 0)
            self.assertFalse((Path(tmp) / "id-map.json").exists())
            self.assertIn("NOT written (markdown preview); 8 provisional id(s)", stdout)
            body = out.read_text(encoding="utf-8")
            table = [l for l in body.splitlines() if l.startswith("| BP-")]
            self.assertEqual(len(table), 8)
            self.assertTrue(all(" (provisional) |" in l for l in table))
            self.assertIn("8 id(s) marked (provisional)", body)

    def test_a_preview_leaves_an_existing_map_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            dump = mixed_dump()
            self.assertEqual(self.cli(tmp, dump, "json")[0], 0)
            id_map = Path(tmp) / "id-map.json"
            before = id_map.read_bytes()
            dump["configurationPolicies"][0]["settings"].append(
                {"id": "9", "settingInstance": choice("zz_new_setting", "zz_new_setting_1")})
            code, stdout, out = self.cli(tmp, dump, "markdown")
            self.assertEqual(code, 0)
            self.assertEqual(id_map.read_bytes(), before)
            self.assertIn("1 provisional id(s)", stdout)
            body = out.read_text(encoding="utf-8")
            marked = [l for l in body.splitlines() if "(provisional)" in l
                      and l.startswith("| BP-")]
            self.assertEqual(len(marked), 1)
            self.assertIn("zz_new_setting", marked[0])
            shown = marked[0].split(" ")[1]
            # The number the preview showed is the one the json run then fixes.
            self.assertEqual(self.cli(tmp, dump, "json")[0], 0)
            fixed = json.loads(id_map.read_text(encoding="utf-8"))["ids"]
            self.assertEqual(fixed["configurationPolicies|%s|zz_new_setting"
                                   % guid_for("Default LAPS Policy")], shown)

    def test_a_preview_says_it_is_not_the_ratified_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, out = self.cli(tmp, mixed_dump(), "markdown")
            first = out.read_text(encoding="utf-8").splitlines()[0]
            self.assertTrue(first.startswith("*Preview rendered by `generate_baseline.py`"))
            self.assertIn("This is not the standard: `run_config_cycle.py ratify` renders "
                          "the authoritative block", first)

    def test_no_text_claims_markdown_is_exactly_the_ratify_block(self):
        help_text = io.StringIO()
        with contextlib.redirect_stdout(help_text):
            with self.assertRaises(SystemExit):
                gb.main(["--help"])
        for text in (gb.__doc__, gb.to_markdown.__doc__, help_text.getvalue()):
            self.assertNotIn("exactly the block", " ".join(text.split()).lower())
        self.assertIn("PREVIEW", " ".join(help_text.getvalue().split()))

    def test_a_preview_cannot_write_a_cycle_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = Path(tmp) / "2026-09-24" / "README.md"
            code, _, out = self.cli(tmp, mixed_dump(), "markdown",
                                    ["--cycle-record", str(record)])
            self.assertIn("cannot be combined with --cycle-record", str(code))
            self.assertFalse(record.exists())
            self.assertFalse(out.exists())


# ------------------------------------------------------------------ shape refusals

def instance_policy(instance):
    return mini_dump([policy("P", "windows10", [instance])])


class ShapeRefusals(unittest.TestCase):
    """A dump the contract cannot read is refused by JSON path -- never a traceback, and
    never a plausible row built from the wrong thing."""

    SETTING = "$.configurationPolicies[0].settings[0]"
    INSTANCE = SETTING + ".settingInstance"

    def malformed(self):
        """(label, dump, the path and kind the refusal must name)."""
        cases = []

        def add(label, dump, expected):
            cases.append((label, dump, expected))

        dump = instance_policy(choice("a", "a_1"))
        dump["configurationPolicies"][0]["settings"] = "notalist"
        add("settings not a list", dump,
            "$.configurationPolicies[0].settings is a string, expected an array")
        dump = instance_policy(choice("a", "a_1"))
        dump["configurationPolicies"][0]["settings"] = ["x"]
        add("setting not an object", dump, self.SETTING + " is a string")
        dump = instance_policy(choice("a", "a_1"))
        del dump["configurationPolicies"][0]["settings"][0]["settingInstance"]
        add("settingInstance missing", dump, self.INSTANCE + " is null, expected an object")
        add("settingInstance a list", instance_policy([choice("a", "a_1")]),
            self.INSTANCE + " is an array, expected an object")
        bad = choice("a", "a_1")
        bad["choiceSettingValue"] = "str"
        add("choice value a string", instance_policy(bad),
            self.INSTANCE + ".choiceSettingValue is a string, expected an object")
        bad = simple("s", 1)
        bad["simpleSettingValue"] = [1]
        add("simple value a list", instance_policy(bad),
            self.INSTANCE + ".simpleSettingValue is an array, expected an object")
        bad = simple_collection("c", [])
        bad["simpleSettingCollectionValue"] = {"k1": 1, "k2": 2}
        add("collection value a dict", instance_policy(bad),
            self.INSTANCE + ".simpleSettingCollectionValue is an object, expected an array")
        bad = simple_collection("c", [])
        bad["simpleSettingCollectionValue"] = [1, 2]
        add("collection element a scalar", instance_policy(bad),
            self.INSTANCE + ".simpleSettingCollectionValue[0] is a number, expected an "
            "object")
        bad = choice_collection("c", [])
        bad["choiceSettingCollectionValue"] = "x"
        add("choice collection a string", instance_policy(bad),
            self.INSTANCE + ".choiceSettingCollectionValue is a string")
        bad = choice("a", "a_1")
        bad["settingDefinitionId"] = 5
        add("definition id a number", instance_policy(bad),
            self.INSTANCE + ".settingDefinitionId is a number, expected a non-empty string")
        bad = choice("a", "a_1")
        bad["settingDefinitionId"] = ""
        add("definition id empty", instance_policy(bad),
            self.INSTANCE + ".settingDefinitionId is empty")
        child = simple("child", 1)
        child["simpleSettingValue"] = "x"
        add("malformed child of a choice", instance_policy(choice("a", "a_1", [child])),
            self.INSTANCE + ".choiceSettingValue.children[0].simpleSettingValue is a "
            "string")
        dump = instance_policy(choice("a", "a_1"))
        dump["configurationPolicies"][0]["platforms"] = ["windows10"]
        add("platforms a list", dump, "$.configurationPolicies[0].platforms is an array")
        dump = instance_policy(choice("a", "a_1"))
        dump["configurationPolicies"][0]["assignments"] = {"target": {}}
        add("assignments an object", dump,
            "$.configurationPolicies[0].assignments is an object, expected an array")
        dump = instance_policy(choice("a", "a_1"))
        dump["configurationPolicies"][0]["isAssigned"] = "false"
        add("isAssigned a string", dump,
            "$.configurationPolicies[0].isAssigned is a string, expected a boolean")
        add("collection an object", {"configurationPolicies": {"a": 1}},
            "$.configurationPolicies is an object, expected an array")
        add("object a string", mini_dump(device_configurations=["str"]),
            "$.deviceConfigurations[0] is a string, expected an object")
        dump = mixed_dump()
        dump["deviceConfigurations"][0]["displayName"] = 42
        add("displayName a number", dump,
            "$.deviceConfigurations[0].displayName is a number, expected a string")
        dump = mixed_dump()
        dump["deviceCompliancePolicies"][0]["@odata.type"] = {"x": 1}
        add("odata type an object", dump,
            "$.deviceCompliancePolicies[0].@odata.type is an object, expected a string")
        return cases

    def test_every_malformed_shape_is_refused_by_path(self):
        for label, dump, expected in self.malformed():
            with self.subTest(label):
                with self.assertRaises(gb.GeneratorError) as ctx:
                    generate(dump, {})
                self.assertIn(expected, str(ctx.exception))

    def test_the_cli_refuses_cleanly_and_writes_nothing(self):
        for label, dump, expected in self.malformed():
            with self.subTest(label), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "2026-09-24" / "intune-config-export.json"
                write_json(path, dump)
                out, id_map = Path(tmp) / "o.json", Path(tmp) / "id-map.json"
                code, _, err = run_cli(["--dump", str(path), "--out", str(out),
                                        "--id-map", str(id_map),
                                        "--generated-at", GENERATED_AT])
                self.assertIsInstance(code, str, "expected a refusal, got exit %r" % code)
                self.assertTrue(code.startswith("error: "), code)
                self.assertIn(expected, code)
                self.assertNotIn("Traceback", err)
                self.assertFalse(out.exists())
                self.assertFalse(id_map.exists())

    def test_the_real_shapes_still_pass(self):
        """The helpers' shapes are the real dump's shapes: nothing above is too strict."""
        dump = mini_dump([policy("P", "windows10", [
            choice("a", "a_1", [simple("a_child", 3),
                                simple_collection("a_list", ["x", "y"])]),
            choice_collection("cc", ["cc_1", "cc_2"]),
            {"@odata.type": "#microsoft.graph.deviceManagementConfigurationGroupSetting"
                            "CollectionInstance",
             "settingDefinitionId": "grp",
             "groupSettingCollectionValue": [{"children": [simple("g_child", "v")]}]}])],
            device_configurations=[bag("D", "#microsoft.graph.macOSGeneralDevice"
                                            "Configuration", {"x": 1})])
        rows = settings(generate(dump, {})["rows"])
        self.assertEqual(sorted(r["setting_id"] for r in rows),
                         ["a", "a_child", "a_list", "cc", "g_child", "x"])


class EmptyDumps(unittest.TestCase):

    def cli(self, tmp, dump_obj, *extra):
        path = Path(tmp) / "2026-09-24" / "intune-config-export.json"
        write_json(path, dump_obj)
        out = Path(tmp) / "o.json"
        code, stdout, stderr = run_cli(["--dump", str(path), "--out", str(out),
                                        "--id-map", str(Path(tmp) / "id-map.json"),
                                        "--generated-at", GENERATED_AT] + list(extra))
        return code, stdout, stderr, out

    def test_collections_holding_zero_objects_are_refused(self):
        """The finding: present-but-empty passed the key-only guard and wrote 0 rows."""
        for dump_obj in ({"configurationPolicies": []}, mini_dump()):
            with self.subTest(sorted(dump_obj)), tempfile.TemporaryDirectory() as tmp:
                code, _, _, out = self.cli(tmp, dump_obj)
                self.assertIn("holds zero objects across the expected collections", str(code))
                self.assertFalse(out.exists())
        with tempfile.TemporaryDirectory() as tmp:
            code, _, _, _ = self.cli(tmp, {"configurationPolicies": []})
            self.assertIn("configurationPolicies 0, deviceConfigurations absent, "
                          "deviceCompliancePolicies absent", str(code))

    def test_allow_empty_still_permits_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, stdout, stderr, out = self.cli(tmp, mini_dump(), "--allow-empty")
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out.read_text(encoding="utf-8"))["meta"]["row_count"],
                             0)
            self.assertIn("0 rows in scope", stderr)

    def test_all_unassigned_is_not_refused_but_is_said(self):
        """Objects exist and every exclusion is listed, so this is a real (if alarming)
        state, not a failed export. It runs, and says so."""
        dump = mini_dump([policy("Off", "windows10", [choice("a", "a_1")],
                                 assigned=False)])
        with tempfile.TemporaryDirectory() as tmp:
            code, _, stderr, out = self.cli(tmp, dump)
            self.assertEqual(code, 0)
            self.assertIn("0 rows in scope (1 object(s) excluded as unassigned)", stderr)
            doc = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(len(doc["meta"]["scope"]["excluded_objects"]), 1)


# ------------------------------------------------------------ settingCount acceptance

def with_counts(dump):
    """Give every configurationPolicies entry the settingCount Graph would: the number of
    settings it carries. The other helpers leave it out, so they read as uncounted."""
    for entry in dump.get("configurationPolicies") or []:
        entry["settingCount"] = len(entry.get("settings") or [])
    return dump


def truncated_dump():
    """Counted, with two truncations: an ASSIGNED Windows policy fetched 2 of 5, and an
    UNASSIGNED macOS policy fetched 0 of 3 -- the check must not skip out-of-scope ones."""
    dump = with_counts(mini_dump([
        policy("Default Defender Windows", "windows10",
               [choice("a", "a_1"), choice("b", "b_1")]),
        policy("Default FileVault macOS", "macOS", [choice("c", "c_1")]),
        policy("TESTING Unassigned macOS", "macOS", [], assigned=False),
        policy("Complete Windows", "windows10", [choice("d", "d_1")]),
    ], device_configurations=[bag("Mac Restrictions",
                                  "#microsoft.graph.macOSGeneralDeviceConfiguration",
                                  {"airDropBlocked": True})]))
    dump["configurationPolicies"][0]["settingCount"] = 5
    dump["configurationPolicies"][2]["settingCount"] = 3
    return dump


GENERATOR_SCRIPT = Path(gb.__file__).resolve()


class SettingCountGate(unittest.TestCase):
    """The acceptance test, ENFORCED: a truncated dump diffs as no change, so it must be
    refused by default -- naming each policy with both numbers -- and an override must
    leave the result marked incomplete wherever it is read."""

    WIN = "'Default Defender Windows' (object id %s): settingCount 5, settings fetched 2" \
        % guid_for("Default Defender Windows")
    MAC = "'TESTING Unassigned macOS' (object id %s): settingCount 3, settings fetched 0" \
        % guid_for("TESTING Unassigned macOS")

    def cli(self, tmp, dump_obj, *extra, record=True):
        folder = Path(tmp) / "dumps" / "2026-09-24"
        dump = folder / "intune-config-export.json"
        write_json(dump, dump_obj)
        argv = ["--dump", str(dump), "--out", str(folder / "baseline-rows.json"),
                "--id-map", str(Path(tmp) / "dumps" / "id-map.json"),
                "--generated-at", GENERATED_AT]
        if record:
            argv += ["--cycle-record", str(folder / "README.md")]
        code, out, err = run_cli(argv + list(extra))
        return code, out, err, folder

    def test_build_rows_refuses_naming_each_policy_and_both_numbers(self):
        with self.assertRaises(gb.GeneratorError) as ctx:
            generate(truncated_dump(), {})
        message = str(ctx.exception)
        self.assertIn("2 Settings Catalog policies declare a settingCount that disagrees",
                      message)
        self.assertIn(self.WIN, message)
        self.assertIn(self.MAC, message)
        self.assertNotIn("Complete Windows", message, "a complete policy was named")
        self.assertIn("--allow-truncated", message)

    def test_the_cli_exits_1_and_writes_nothing(self):
        """Through a real process, so 'exit 1' is the status the wrapper actually sees."""
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "2026-09-24"
            dump = folder / "intune-config-export.json"
            write_json(dump, truncated_dump())
            proc = subprocess.run(
                [sys.executable, str(GENERATOR_SCRIPT), "--dump", str(dump),
                 "--out", str(folder / "baseline-rows.json"),
                 "--id-map", str(Path(tmp) / "id-map.json"),
                 "--generated-at", GENERATED_AT, "--cycle-record", str(folder / "README.md")],
                capture_output=True, text=True,
                env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
            self.assertEqual(proc.returncode, 1, proc.stderr)
            self.assertIn("error: 2 Settings Catalog policies", proc.stderr)
            self.assertIn(self.WIN, proc.stderr)
            self.assertIn(self.MAC, proc.stderr)
            self.assertNotIn("Traceback", proc.stderr)
            self.assertEqual(sorted(p.name for p in Path(tmp).rglob("*") if p.is_file()),
                             ["intune-config-export.json"], "a refused run wrote a file")

    def test_every_platform_filter_and_format_is_refused(self):
        """One truncated policy means the export is broken. A Windows-only run, a preview,
        and a platform whose policies are all complete are refused alike."""
        for extra in (["--platform", "windows"], ["--platform", "ios"],
                      ["--format", "markdown"]):
            with self.subTest(extra), tempfile.TemporaryDirectory() as tmp:
                code, _, _, folder = self.cli(tmp, truncated_dump(), *extra, record=False)
                self.assertIsInstance(code, str, "expected a refusal, got exit %r" % code)
                self.assertIn(self.MAC, code)
                self.assertFalse((folder / "baseline-rows.json").exists())
                self.assertFalse((Path(tmp) / "dumps" / "id-map.json").exists())

    def test_more_settings_than_declared_and_absent_settings_are_mismatches(self):
        more = with_counts(mini_dump([policy("P", "windows10", [choice("a", "a_1"),
                                                                 choice("b", "b_1")])]))
        more["configurationPolicies"][0]["settingCount"] = 1
        absent = with_counts(mini_dump([policy("Q", "windows10", [choice("a", "a_1")])]))
        del absent["configurationPolicies"][0]["settings"]
        absent["configurationPolicies"][0]["settingCount"] = 4
        for dump, expected in ((more, "settingCount 1, settings fetched 2"),
                               (absent, "settingCount 4, settings fetched 0")):
            with self.subTest(expected):
                with self.assertRaises(gb.GeneratorError) as ctx:
                    generate(dump, {})
                self.assertIn(expected, str(ctx.exception))

    def test_allow_truncated_generates_and_records_the_override_everywhere(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out, err, folder = self.cli(tmp, truncated_dump(), "--allow-truncated")
            self.assertEqual(code, 0)
            check = json.loads((folder / "baseline-rows.json").read_text(
                encoding="utf-8"))["meta"]["setting_count_check"]
            self.assertEqual(check["allowed_by"], "--allow-truncated")
            self.assertEqual((check["policies"], check["counted"], check["uncounted"]),
                             (4, 4, []))
            self.assertEqual(
                [(m["name"], m["object_id"], m["platform"], m["setting_count"],
                  m["settings_fetched"]) for m in check["mismatches"]],
                [("Default Defender Windows", guid_for("Default Defender Windows"),
                  "windows10", 5, 2),
                 ("TESTING Unassigned macOS", guid_for("TESTING Unassigned macOS"),
                  "macOS", 3, 0)])
            self.assertIn("2 mismatch(es) -- ALLOWED by --allow-truncated, baseline "
                          "INCOMPLETE", out)
            self.assertIn("WARNING       truncated under --allow-truncated: " + self.WIN, err)
            self.assertIn("WARNING       truncated under --allow-truncated: " + self.MAC, err)

            record = (folder / "README.md").read_text(encoding="utf-8")
            self.assertIn("\n## Export completeness\n", record)
            self.assertIn("| Count mismatches | **2 — generated under `--allow-truncated`; "
                          "this baseline is INCOMPLETE** |", record)
            self.assertIn("| Default Defender Windows | `%s` | `windows10` | 5 | 2 |"
                          % guid_for("Default Defender Windows"), record)
            self.assertIn("| TESTING Unassigned macOS | `%s` | `macOS` | 3 | 0 |"
                          % guid_for("TESTING Unassigned macOS"), record)

    def test_a_preview_under_the_override_says_incomplete(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "2026-09-24"
            dump = folder / "intune-config-export.json"
            write_json(dump, truncated_dump())
            out = Path(tmp) / "preview.md"
            code, _, _ = run_cli(["--dump", str(dump), "--out", str(out),
                                  "--id-map", str(Path(tmp) / "id-map.json"),
                                  "--generated-at", GENERATED_AT, "--format", "markdown",
                                  "--allow-truncated"])
            self.assertEqual(code, 0)
            text = out.read_text(encoding="utf-8")
            self.assertIn("**INCOMPLETE: generated under `--allow-truncated`.** 2 Settings "
                          "Catalog policies", text)
            self.assertIn("settingCount 5, settings fetched 2", text)
            self.assertLess(text.index("INCOMPLETE"), text.index("### In scope"))

    def test_a_complete_dump_passes_and_the_flag_changes_no_byte(self):
        """The override is recorded only when it let something through, so passing it on
        a complete dump cannot make two runs of the same input differ."""
        outputs = []
        for extra in ((), ("--allow-truncated",)):
            with tempfile.TemporaryDirectory() as tmp:
                code, out, err, folder = self.cli(tmp, with_counts(mixed_dump()), *extra)
                self.assertEqual(code, 0)
                self.assertIn("settingCount  1 of 1 policies counted, 0 mismatch(es)\n", out)
                self.assertNotIn("settingCount", err)
                outputs.append(tuple((folder / n).read_bytes()
                                     for n in ("baseline-rows.json", "README.md")))
        self.assertEqual(outputs[0], outputs[1])
        doc = json.loads(outputs[0][0].decode("utf-8"))
        self.assertEqual(doc["meta"]["setting_count_check"],
                         {"policies": 1, "counted": 1, "mismatches": [], "uncounted": [],
                          "allowed_by": None})
        record = outputs[0][1].decode("utf-8")
        self.assertIn("| Count mismatches | none |", record)
        self.assertIn("| No `settingCount` | none |", record)

    def test_a_policy_with_no_settingcount_is_listed_and_warned_not_refused(self):
        dump = mixed_dump()          # the helpers carry no settingCount
        with tempfile.TemporaryDirectory() as tmp:
            code, out, err, folder = self.cli(tmp, dump)
            self.assertEqual(code, 0)
            check = json.loads((folder / "baseline-rows.json").read_text(
                encoding="utf-8"))["meta"]["setting_count_check"]
            self.assertEqual((check["policies"], check["counted"], check["mismatches"]),
                             (1, 0, []))
            self.assertEqual([(u["name"], u["object_id"]) for u in check["uncounted"]],
                             [("Default LAPS Policy", guid_for("Default LAPS Policy"))])
            self.assertIn("settingCount  0 of 1 policies counted", out)
            self.assertIn("1 Settings Catalog policies carry no settingCount; their "
                          "completeness cannot be counted: 'Default LAPS Policy'", err)
            record = (folder / "README.md").read_text(encoding="utf-8")
            self.assertIn("| No `settingCount` | **1 — completeness of these cannot be "
                          "counted** |", record)
            self.assertIn("| Default LAPS Policy | `%s` | `windows10` |"
                          % guid_for("Default LAPS Policy"), record)

    def test_a_non_integer_settingcount_is_refused_by_path_even_with_the_override(self):
        for bad, kind in (("5", "a string"), (True, "a boolean"), (2.5, "a number")):
            dump = with_counts(mini_dump([policy("P", "windows10", [choice("a", "a_1")])]))
            dump["configurationPolicies"][0]["settingCount"] = bad
            with self.subTest(bad):
                with self.assertRaises(gb.GeneratorError) as ctx:
                    gb.build_rows(dump, GENERATED_AT, "deadbeef", "x.json",
                                  allow_truncated=True)
                self.assertIn("$.configurationPolicies[0].settingCount is %s, expected an "
                              "integer" % kind, str(ctx.exception))

    def test_the_check_does_not_depend_on_source_order(self):
        dump = truncated_dump()
        shuffled = copy.deepcopy(dump)
        shuffled["configurationPolicies"].reverse()
        checks = [gb.build_rows(d, GENERATED_AT, "deadbeef", "x.json",
                                allow_truncated=True)["meta"]["setting_count_check"]
                  for d in (dump, shuffled)]
        self.assertEqual(checks[0], checks[1])


# --------------------------------------------------------------------- known limits

class KnownLimits(unittest.TestCase):
    """The two limits the module docstring states. Pinned so that changing either is a
    decision someone makes, not a side effect nobody notices."""

    def test_duplicate_then_delete_is_an_add_plus_a_remove_not_a_rename(self):
        """Intune's Duplicate issues a new object id. Same name, same settings -- still a
        different object, so every row gets a fresh id and the old ids stay reserved."""
        instances = [choice("a", "a_1"), simple("b", 7)]
        id_map = {}
        original = generate(mini_dump([policy("Default Edge", "macOS", instances,
                                              guid="11111111-0000-0000-0000-000000000001")]),
                            id_map)
        copied = generate(mini_dump([policy("Default Edge", "macOS", instances,
                                            guid="22222222-0000-0000-0000-000000000002")]),
                          id_map)
        before, after = keyed(original), keyed(copied)
        self.assertEqual(len(before), 3)
        self.assertEqual(set(before) & set(after), set(), "a row survived by name")
        self.assertEqual({r["id"] for r in before.values()} &
                         {r["id"] for r in after.values()}, set(), "an id was carried over")
        self.assertEqual(
            [(r["setting_id"], r["required_value"]) for r in original["rows"]],
            [(r["setting_id"], r["required_value"]) for r in copied["rows"]],
            "the copy should be identical in everything but its object id")
        for row in before.values():
            self.assertEqual(id_map[row["row_key"]], row["id"], "a retired id was freed")
        self.assertEqual(len(id_map), 6)

    def test_a_repeated_definition_id_is_identified_by_position(self):
        """Reordering repeated items swaps their values between stable ids; removing the
        first makes `id` take the second's value and `id#2` read as removed."""
        def run(values, id_map):
            dump = mini_dump([policy("P", "windows10",
                                     [choice("same_id", v) for v in values])])
            return {r["setting_id"]: (r["id"], r["required_value"])
                    for r in settings(generate(dump, id_map)["rows"])}

        id_map = {}
        first = run(["value_a", "value_b"], id_map)
        swapped = run(["value_b", "value_a"], id_map)
        self.assertEqual(first, {"same_id": ("BP-WIN-0002", "value_a"),
                                 "same_id#2": ("BP-WIN-0003", "value_b")})
        self.assertEqual(swapped, {"same_id": ("BP-WIN-0002", "value_b"),
                                   "same_id#2": ("BP-WIN-0003", "value_a")})
        dropped_first = run(["value_b"], id_map)
        self.assertEqual(dropped_first, {"same_id": ("BP-WIN-0002", "value_b")})


# ------------------------------------------------------------------ real dump (opt-in)

REAL_DUMP = os.environ.get("BASELINE_REAL_DUMP")


@unittest.skipUnless(REAL_DUMP and Path(REAL_DUMP).is_file(),
                     "set BASELINE_REAL_DUMP to a real intune-config-export.json")
class RealDump(unittest.TestCase):
    """The verified figures of the cycle 1 dump (2026-09-27; its raw file is byte-identical
    to the retired 2026-09-24 one). Opt-in: the dump lives in the restricted repo."""

    @classmethod
    def setUpClass(cls):
        cls.dump = json.loads(Path(REAL_DUMP).read_text(encoding="utf-8-sig"))
        cls.id_map = {}
        cls.doc = generate(cls.dump, cls.id_map)

    def test_row_totals(self):
        rows = self.doc["rows"]
        names = [r for r in rows if r["mode"] == "identity"]
        self.assertEqual(len(rows) - len(names), 478)
        self.assertEqual(len(names), 44)
        self.assertEqual(sum(1 for r in settings(rows) if r["platform"] == "iOS"), 226)
        leaf = self.doc["meta"]["scope"]["leaf_counts"]
        self.assertEqual([leaf[p]["scalar"] for p in ("windows10", "macOS", "iOS")],
                         [84, 56, 2])

    def test_renaming_a_real_policy_on_a_copy_moves_no_id(self):
        renamed = copy.deepcopy(self.dump)
        target = [p for p in renamed["configurationPolicies"] if p.get("isAssigned")][0]
        target["name"] = target["name"] + " (renamed)"
        after = generate(renamed, dict(self.id_map))
        before_rows, after_rows = keyed(self.doc), keyed(after)
        self.assertEqual({k: r["id"] for k, r in before_rows.items()},
                         {k: r["id"] for k, r in after_rows.items()})
        changed = [k for k in before_rows
                   if before_rows[k]["required_value"] != after_rows[k]["required_value"]]
        self.assertEqual(changed, ["configurationPolicies|%s|@displayname"
                                   % target["id"].lower()])

    def test_the_real_dump_passes_the_count_gate(self):
        """36 policies, every one counted, none truncated -- so the gate is not so strict
        that it would refuse the dump the figures above were verified against."""
        check = self.doc["meta"]["setting_count_check"]
        self.assertEqual((check["policies"], check["counted"]), (36, 36))
        self.assertEqual((check["mismatches"], check["uncounted"], check["allowed_by"]),
                         ([], [], None))


if __name__ == "__main__":
    unittest.main(verbosity=2)
