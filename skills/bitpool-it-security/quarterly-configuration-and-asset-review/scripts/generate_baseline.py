#!/usr/bin/env python3
"""Turn a raw Intune config dump into the canonical hardening-standard baseline rows.

WHY THIS EXISTS
---------------
The hardening standards (windows/macos/ios endpoints) have to say what is ACTUALLY
enforced, with an id per setting that survives across quarters. Typing that by hand from
the Intune blades is how a standard drifts from the tenant within one cycle. This reads
the dump instead, so the standard is derived rather than remembered.

The output is the join target for the quarterly diff. That is the whole design
constraint: a row has to be findable NEXT quarter even though its position in the dump
and its display name may both have moved.

IDENTITY IS THE INTUNE OBJECT ID, NEVER THE NAME  (contract v2)
---------------------------------------------------------------

    row_key = collection|object_id|setting_id        (object_id, setting_id lowercased)

No name and no platform in the key. v1 keyed on the normalised display name and folded
the two live 'Default' typos (Defualt / Defult) so that fixing one in the Intune UI would
not read as a whole policy deleted and re-added. That only ever covered the renames
someone had anticipated: promoting "TESTING Default OneDrive Settings" to "Default
OneDrive Settings" still retired every id in the policy and issued new ones. The object
id is the one field Graph keeps stable for the life of the object, so identity is that,
and every rename -- typo fix or otherwise -- leaves every id where it was.

THE NAME IS ITSELF A DIFFED SETTING
-----------------------------------
With the name out of the key, a rename would otherwise be invisible. So every in-scope
object carries ONE synthetic row:

    setting_id     @displayName        ('@' cannot begin a settingDefinitionId, and
                                        '@'-prefixed property-bag keys are Graph
                                        annotations that are skipped -- so no real
                                        setting can collide with it)
    setting_name   Policy name
    required_value the display name, verbatim
    mode           identity

A rename is then exactly one CHANGED value on that row and no other row's identity moves.
It always sorts FIRST within its object, whatever its setting ids happen to sort as.

ids (BP-WIN-0001 etc.) are looked up FROM row_key via a persisted id-map, never recomputed
from position. Renumbering a standard silently invalidates every prior review, every
ticket that cites a row, and every auditor note. So: never renumber, never reuse a
retired number. Entries are only ever ADDED to the id-map -- a row that disappears keeps
its entry, which is exactly what reserves its number. A v1 map (name-keyed) is REFUSED,
never migrated: none of its keys can be carried across, and a silent migration would
renumber everything while looking as though it had not.

HUMAN-READABLE LABELS ARE FOR DISPLAY ONLY
------------------------------------------
Given --definitions (the exporter's setting-definitions.json), Settings Catalog rows get
setting_name = the definition's displayName and display_value = the chosen option's
displayName. required_value stays the RAW Graph value and is the only thing the differ
compares, so a Microsoft relabel of an option never creates a phantom difference. Any
miss falls back to the raw value and is COUNTED -- never guessed. deviceConfigurations
and compliance rows keep their property name: no label is ever invented.

LEAF COUNTS -- READ THIS BEFORE "FIXING" A COUNT MISMATCH
---------------------------------------------------------
Settings Catalog policies (configurationPolicies) carry a RECURSIVE tree, not a flat
bag. A node earns a row when it carries a value of its own; a group node is a container
and earns none, though we keep walking through it.

Verified against the 2026-09-24 dump, assigned policies only:

    platform    policies   scalar leaves   collection leaves   rows
    windows10         14              84                   4     88
    macOS              6              56                   3     59
    iOS                2               2                   0      2

The 84 / 56 / 2 figures are the SCALAR leaves -- choiceSettingValue and
simpleSettingValue. They are reported verbatim in meta.scope.leaf_counts so any run can
be checked against them. The name rows are NOT in these figures; they are counted in
meta.counts, which always sums to meta.row_count.

The extra 7 rows are the collection-valued leaves: simpleSettingCollectionValue and
choiceSettingCollectionValue. They are NOT dropped to make a total match 84, because
those 7 are among the most security-relevant settings in the tenant -- the local
Administrators group membership, the Edge force-install extension list, the Platform SSO
URLs. A hardening standard that omits who is a local admin is worse than no standard.

If your scalar counts are not 84 / 56 / 2 on that dump, your flattening IS wrong. Do not
adjust the expectation.

BASE64 PAYLOADS ARE HASHED, NEVER INLINED
------------------------------------------
macOSCustomConfiguration carries a base64 plist in `payload`. The largest in this dump is
12,604 characters. Inlined, one row would be longer than the rest of the standard
combined and the markdown would be unusable. We emit sha256:<digest> instead, so the diff
still fires on any payload change while the page stays readable. Measured on this dump, a
256-character threshold catches exactly the 11 payload fields and nothing else.

SETTINGCOUNT IS THE ACCEPTANCE TEST, AND IT IS ENFORCED HERE
-------------------------------------------------------------
Every configurationPolicies entry declares `settingCount`, and the export must have
fetched exactly that many entries into `settings`. Until 2026-09-18 the exporter threw
away @odata.nextLink inside batched sub-responses: four policies came back with 25
settings against 306, 287, 65 and 64 declared, and nothing else in the export looked
wrong. A truncated dump generates a truncated baseline, and diffed against another one it
reports NO CHANGE -- the most dangerous output this pipeline can give.

So the check is not left to someone reading the docs. build_rows refuses such a dump,
naming every offending policy with both numbers, and the CLI exits 1 having written
nothing. It checks every entry, assigned or not, and the whole dump whatever --platform
says: one truncated policy means the export is broken, not just that policy or platform.
The one way past it is --allow-truncated, and that override is written into
meta.setting_count_check, the cycle record and the markdown preview, so a baseline
generated from a truncated dump always says so.

A policy with NO settingCount cannot be counted. That is a warning, not a refusal -- a
Graph response always carries the field, so a missing one points to a foreign or
hand-built dump rather than truncation -- and every such policy is listed in
meta.setting_count_check.uncounted rather than treated as passing.

KNOWN LIMITS -- BOTH DELIBERATE, BOTH PINNED BY TESTS
-----------------------------------------------------
1. Duplicate-then-delete is an add plus a remove, not a rename. Intune's Duplicate
   creates a NEW object with a NEW object id. If the original is then deleted, every row
   of the old object disappears (its ids stay reserved in the map, never reissued) and
   every row of the copy arrives with fresh ids -- even when the name and settings are
   identical. That is correct. They are two objects, and carrying ids across would mean
   guessing identity from the name or the settings, which is exactly what contract v2
   removed. The diff shows a whole-object removal plus a whole-object addition. If it
   was a duplicate, the reviewer says so in the review.

2. A settingDefinitionId repeated inside ONE policy is disambiguated by position: the
   first occurrence in tree-walk order is `id`, the next `id#2`, then `id#3`. Identity
   for those items is therefore positional. If Graph returns them in a different order,
   their values swap between ids and the diff reports value changes on both. If the
   first is removed, `id` takes the second's value and `id#2` reads as removed, although
   it was really the first item that went. There are zero repeated ids in the 2026-09-24
   dump. The tree permits them, and the alternative, keying on the value, would turn
   every value change into a remove plus an add.

DETERMINISM IS A HARD REQUIREMENT
----------------------------------
Same inputs, byte-identical baseline-rows.json, markdown and cycle record out --
otherwise every cycle produces a git diff full of reordering and the real change is
invisible. So: rows are sorted on an explicit key, timestamps are PASSED IN rather than
read from the clock, and nothing depends on dict iteration order of the source.

Pure stdlib. Run through WSL.

Usage:
    generate_baseline.py --dump dumps/2026-09-24/intune-config-export.json \\
                         --out dumps/2026-09-24/baseline-rows.json \\
                         --id-map dumps/id-map.json \\
                         --generated-at 2026-09-24T00:00:00Z \\
                         [--definitions dumps/2026-09-24/setting-definitions.json] \\
                         [--cycle-record dumps/2026-09-24/README.md] \\
                         [--allow-truncated]     # only to generate from a truncated
                                                 # dump knowingly; it is recorded

    # a PREVIEW of one platform's rows for review. NOT the block ratify injects --
    # `run_config_cycle.py ratify` renders that itself -- and it writes nothing but
    # --out: the id-map is never touched, so ids for rows not yet in it are marked
    # provisional.
    generate_baseline.py ... --platform windows --format markdown --out win.md
"""

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

GENERATOR_VERSION = "2.0"
ID_MAP_SCHEMA = 2

# The three collections a hardening standard is written from. The dump carries more
# (mobileApps, scripts, enrollment restrictions) but those are inventory, not settings.
# The ORDER is the contract's sort order.
COLLECTIONS = ["configurationPolicies", "deviceConfigurations", "deviceCompliancePolicies"]
COLLECTION_RANK = {name: rank for rank, name in enumerate(COLLECTIONS)}

# configurationPolicies rows do not carry an @odata.type in the dump -- the Graph beta
# list response omits it. The type is still fixed and known, and the row contract wants
# it, so it is stated here rather than left null.
CONFIG_POLICY_TYPE = "#microsoft.graph.deviceManagementConfigurationPolicy"

# The synthetic identity row. See the module docstring.
NAME_SETTING_ID = "@displayName"
NAME_SETTING_LABEL = "Policy name"

# Ordered, and the order matters: a node carries exactly one of these. groupSetting-
# CollectionValue is deliberately ABSENT -- it is a container, it holds no value of its
# own, and treating it as a leaf would invent rows with an empty required_value.
VALUE_KEYS = [
    ("choice", "choiceSettingValue"),
    ("simple", "simpleSettingValue"),
    ("simple_collection", "simpleSettingCollectionValue"),
    ("choice_collection", "choiceSettingCollectionValue"),
]
SCALAR_KINDS = {"choice", "simple"}

# Every key on a setting instance that holds a value or a container, and the JSON shape
# Graph gives it. Checked on every instance before a value is read: a wrong shape either
# crashed half-way through the run or -- worse -- rendered something plausible from the
# wrong thing (a dict where a list belongs is iterated as its KEYS). Measured on the
# 2026-09-24 dump: 1,420 instances, every one of these shapes, no exceptions.
VALUE_SHAPES = [
    ("choiceSettingValue", dict, "an object"),
    ("simpleSettingValue", dict, "an object"),
    ("simpleSettingCollectionValue", list, "an array of objects"),
    ("choiceSettingCollectionValue", list, "an array of objects"),
    ("groupSettingValue", dict, "an object"),
    ("groupSettingCollectionValue", list, "an array of objects"),
]

# Housekeeping fields on the property-bag collections. None of these describe what the
# device is made to do, so none belongs in a hardening standard as a setting.
# displayName / name are excluded HERE because they are carried by the synthetic
# @displayName row instead -- emitting them twice would double-report every rename.
METADATA_KEYS = {
    "id", "createdDateTime", "lastModifiedDateTime", "version", "@odata.type",
    "roleScopeTagIds", "supportsScopeTags", "assignments", "displayName", "description",
    # Present on configurationPolicies, same reasoning.
    "name", "settings", "settingCount", "isAssigned", "platforms", "technologies",
    "templateReference", "priorityMetaData", "creationSource",
}

PLATFORM_PREFIX = {
    "windows10": "WIN", "windows": "WIN", "windows11": "WIN",
    "macos": "MAC",
    "ios": "IOS", "ipados": "IOS", "ios/ipados": "IOS",
}

# Contract sort order: windows10, macOS, iOS, then everything else.
PREFIX_RANK = {"WIN": 0, "MAC": 1, "IOS": 2}

# --platform argument -> id prefix. One vocabulary for the filter, whatever the dump
# happens to spell the platform as.
PLATFORM_FILTER = {"windows": "WIN", "macos": "MAC", "ios": "IOS"}

# @odata.type prefix -> the platform vocabulary used by configurationPolicies, so all
# three collections sort and group together instead of forming three parallel worlds.
# LONGEST PREFIX FIRST: windows10CompliancePolicy must not be read as bare "windows".
ODATA_PLATFORM = [
    ("windows10", "windows10"),
    ("windows81", "windows10"),
    ("windows", "windows10"),
    ("macos", "macOS"),
    ("ios", "iOS"),
    ("androidwork", "android"),
    ("android", "android"),
]

FIELD_ORDER = ["row_key", "id", "platform", "collection", "object_type", "object_id",
               "object_name", "setting_id", "setting_name", "required_value",
               "display_value", "mode", "enforced_at", "verify"]

ID_PATTERN = re.compile(r"^BP-([A-Z]{3})-(\d{4})$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Files in a dated folder that are produced AFTER the cycle record, from it or from the
# baseline. They carry their own input hashes; listing them in the record would make the
# record change every time a report is re-run, and the pack hashing the record while the
# record hashes the pack would never settle.
DOWNSTREAM_FILES = re.compile(r"^(diff-vs-.+\.(md|json)|evidence-pack\.html)$")
CYCLE_RECORD_NAME = "README.md"
MANIFEST_NAME = "collection-manifest.json"


class GeneratorError(Exception):
    """A refusal the CLI turns into a clean message and exit 1, never a traceback."""


# ------------------------------------------------------------------------ shape checks

def json_kind(value):
    """The JSON name of a value's type, for a refusal message a reader can act on."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "a boolean"
    if isinstance(value, (int, float)):
        return "a number"
    if isinstance(value, str):
        return "a string"
    if isinstance(value, list):
        return "an array"
    if isinstance(value, dict):
        return "an object"
    return type(value).__name__


def expect(value, kinds, path, wanted, required=False):
    """Refuse a shape the contract does not know, naming its JSON path. -> value.

    null / absent passes unless `required`: an optional field Graph leaves out is
    normal. Anything else of the wrong type is a malformed or foreign export, and the
    run stops with a clean message rather than a traceback or a plausible wrong row.
    """
    if value is None and not required:
        return value
    if not isinstance(value, kinds):
        raise GeneratorError(
            "%s is %s, expected %s. This is not the shape an Intune configuration export "
            "has -- the export is malformed or truncated. Re-run it." % (path,
                                                                        json_kind(value),
                                                                        wanted))
    return value


def collection_objects(dump, collection):
    """The objects of one collection, shape-checked. Absent or null reads as empty."""
    objects = expect(dump.get(collection), list, "$.%s" % collection,
                     "an array of objects") or []
    for index, obj in enumerate(objects):
        expect(obj, dict, "$.%s[%d]" % (collection, index), "an object", required=True)
    return objects


def check_object_fields(obj, collection, index, name_key, platform_key):
    """The fields every row of an object is built from. Checked before any is read."""
    base = "$.%s[%d]" % (collection, index)
    expect(obj.get(name_key), str, "%s.%s" % (base, name_key), "a string")
    expect(obj.get(platform_key), str, "%s.%s" % (base, platform_key), "a string")
    expect(obj.get("assignments"), list, base + ".assignments", "an array")
    expect(obj.get("isAssigned"), bool, base + ".isAssigned", "a boolean")


def check_instance(node, path):
    """A node carrying settingDefinitionId: the id is a non-empty string, and every
    value or container key on it has the shape Graph gives it (see VALUE_SHAPES)."""
    definition_id = node.get("settingDefinitionId")
    if not isinstance(definition_id, str) or not definition_id.strip():
        raise GeneratorError(
            "%s.settingDefinitionId is %s, expected a non-empty string. A setting with no "
            "definition id cannot be keyed -- the export is malformed. Re-run it."
            % (path, "empty" if isinstance(definition_id, str) else
               json_kind(definition_id)))
    for key, kind, wanted in VALUE_SHAPES:
        value = expect(node.get(key), kind, "%s.%s" % (path, key), wanted)
        if isinstance(value, list):
            for index, item in enumerate(value):
                expect(item, dict, "%s.%s[%d]" % (path, key, index), "an object",
                       required=True)


# --------------------------------------------------------------------------- helpers

def platform_prefix(platform):
    """Id prefix for a platform string.

    `platforms` on a configurationPolicy is COMMA-SEPARATED -- single-valued throughout
    this dump, but the field is a list in Graph's data model and a future multi-platform
    policy must not silently take the first token's prefix. A policy spanning two
    families gets GEN, because its id cannot honestly claim to be a Windows id.
    """
    tokens = [t.strip().lower() for t in (platform or "").split(",") if t.strip()]
    prefixes = {PLATFORM_PREFIX.get(t) for t in tokens}
    prefixes.discard(None)
    if len(prefixes) == 1:
        return prefixes.pop()
    return "GEN"


def platform_rank(platform):
    return (PREFIX_RANK.get(platform_prefix(platform), len(PREFIX_RANK)),
            (platform or "").casefold())


def platform_from_odata(odata_type):
    """Derive the platform from '#microsoft.graph.macOSCustomConfiguration' etc."""
    bare = (odata_type or "").split(".")[-1].lower()
    for prefix, platform in ODATA_PLATFORM:
        if bare.startswith(prefix):
            return platform
    return "unknown"


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def render_scalar(value, max_inline):
    """One source value -> the string that goes in required_value.

    Booleans render as JSON true/false rather than Python True/False: the standard is
    read next to the Graph payload, and a reviewer comparing the two should not have to
    translate. Dicts and lists are compact JSON with SORTED keys -- sorted because an
    unsorted dict would let a Graph reordering masquerade as a settings change.
    """
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        # Long strings are base64 plists in practice. Hash rather than inline -- the diff
        # still fires, the page stays readable. See the module docstring.
        if len(value) > max_inline:
            return "sha256:" + sha256_text(value)
        return value
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def render_collection(values, max_inline):
    """A collection leaf -> a compact JSON array, order PRESERVED.

    Order is preserved rather than sorted because it is sometimes meaningful -- the
    Windows logon message is three elements that are three lines of one message. Sorting
    would rewrite the message.
    """
    return json.dumps([render_scalar(v, max_inline) for v in values],
                      separators=(",", ":"))


# ------------------------------------------------------------------- settings catalog

def walk_setting_instance(node, path, out):
    """Flatten a Settings Catalog tree to (setting_id, kind, value, json_path) leaves.

    Recurses THROUGH a leaf as well as recording it: choiceSettingValue carries a
    `children` list, and those children are settings in their own right. The local
    administrators policy is four levels of that -- group > group > choice > children >
    simpleSettingCollection. Stopping at the first value would lose the membership list.
    """
    if isinstance(node, dict):
        if "settingDefinitionId" in node:
            check_instance(node, path)
            definition_id = node["settingDefinitionId"]
            for kind, key in VALUE_KEYS:
                if node.get(key) is not None:
                    out.append((definition_id, kind, node[key], path + "." + key))
                    break
        for key in node:
            walk_setting_instance(node[key], path + "." + key, out)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            walk_setting_instance(item, "%s[%d]" % (path, index), out)


def raw_values(kind, raw):
    """The raw Graph value(s) of a leaf: one value for scalars, a list for collections."""
    if kind in SCALAR_KINDS:
        return raw.get("value")
    # Every element is an object -- check_instance refused anything else upstream.
    return [v.get("value") for v in raw]


def leaf_value(kind, raw, max_inline):
    if kind in SCALAR_KINDS:
        return render_scalar(raw_values(kind, raw), max_inline)
    return render_collection(raw_values(kind, raw), max_inline)


# ---------------------------------------------------------------- display resolution

class Definitions:
    """Index over setting-definitions.json: {settingDefinitionId: Graph body, "_...": ...}.

    Keys beginning with '_' are reserved for the file's own bookkeeping (`_unresolved`,
    the ids the exporter could not fetch) and are never treated as definitions. Lookup
    is exact first, then case-insensitive: the file keeps Graph's casing verbatim, and a
    settingDefinitionId that differs only by case is the same setting.
    """

    def __init__(self, document):
        if not isinstance(document, dict):
            raise GeneratorError("setting definitions must be a JSON object keyed by "
                                 "settingDefinitionId, got %s" % type(document).__name__)
        unresolved = document.get("_unresolved") or []
        if not isinstance(unresolved, list):
            raise GeneratorError("setting definitions `_unresolved` must be a list")
        self.unfetched = sorted(str(item) for item in unresolved)
        self.exact = {key: value for key, value in document.items()
                      if not key.startswith("_") and isinstance(value, dict)}
        self.folded = {}
        for key in sorted(self.exact):
            self.folded.setdefault(key.casefold(), self.exact[key])

    def lookup(self, definition_id):
        found = self.exact.get(definition_id)
        if found is None:
            found = self.folded.get((definition_id or "").casefold())
        return found


def option_label(definition, value):
    """displayName of the option whose itemId equals the raw choice value, or None."""
    if not isinstance(value, str):
        return None
    options = [o for o in (definition.get("options") or []) if isinstance(o, dict)]
    for matcher in (lambda o: o.get("itemId") == value,
                    lambda o: isinstance(o.get("itemId"), str)
                    and o["itemId"].casefold() == value.casefold()):
        for option in options:
            label = option.get("displayName")
            if matcher(option) and isinstance(label, str) and label:
                return label
    return None


def resolve_display(definitions, definition_id, occurrence, kind, raw, required_value,
                    max_inline, misses):
    """-> (setting_name, display_value, hit). hit is None when resolution is off.

    Never touches required_value. A miss of ANY part falls back to the raw value for
    that part and makes the row unresolved -- a half-labelled collection would read as
    though every element had been checked.
    """
    setting_id = definition_id if occurrence == 1 else "%s#%d" % (definition_id,
                                                                  occurrence)
    if definitions is None:
        return setting_id, required_value, None

    definition = definitions.lookup(definition_id)
    if definition is None or not isinstance(definition.get("displayName"), str) \
            or not definition["displayName"]:
        misses["definitions"].add(definition_id)
        return setting_id, required_value, False

    label = definition["displayName"]
    if occurrence != 1:
        label = "%s #%d" % (label, occurrence)

    values = raw_values(kind, raw)
    if kind == "simple":
        return label, required_value, True
    if kind == "simple_collection":
        return label, "; ".join(render_scalar(v, max_inline) for v in values), True

    choices = [values] if kind == "choice" else list(values)
    labels = []
    for value in choices:
        found = option_label(definition, value)
        if found is None:
            misses["options"].add("%s = %s" % (definition_id, value))
        labels.append(found)
    if any(found is None for found in labels):
        return label, required_value, False
    return label, "; ".join(labels), True


# --------------------------------------------------------------------- row extraction

def is_assigned(obj):
    """(assigned, disagreement_or_None).

    isAssigned is present and authoritative on configurationPolicies. The other two
    collections do not carry it, so assignments is the fallback. Where both exist and
    DISAGREE we take assigned -- over-documenting a setting is a smaller failure than a
    hardening standard omitting one that is live -- and the disagreement is recorded as a
    finding rather than resolved silently.
    """
    flag = obj.get("isAssigned")
    has_assignments = bool(obj.get("assignments"))
    if flag is None:
        return has_assignments, None
    if bool(flag) != has_assignments:
        return True, {"isAssigned": bool(flag),
                      "assignments": len(obj.get("assignments") or [])}
    return bool(flag), None


def require_object_id(obj, collection, index):
    """The object id IS the identity. An object without one cannot be keyed at all."""
    object_id = obj.get("id")
    if not isinstance(object_id, str) or not object_id.strip():
        raise GeneratorError(
            "%s[%d] (%r) carries no object id. Row identity is the Intune object id, so "
            "this object cannot be keyed -- the export is malformed. Re-run it."
            % (collection, index, obj.get("displayName") or obj.get("name")))
    return object_id


def object_ref(collection, object_id, name, platform):
    return {"collection": collection, "object_id": object_id, "name": name,
            "platform": platform}


def name_row(base, name, verify):
    value = "" if name is None else str(name)
    return dict(base, setting_id=NAME_SETTING_ID, setting_name=NAME_SETTING_LABEL,
                required_value=value, display_value=value, mode="identity",
                verify=verify, _kind=None, _hit=None)


def config_policy_rows(dump, max_inline, definitions, misses, excluded, disagreements):
    rows = []
    for index, policy in enumerate(collection_objects(dump, "configurationPolicies")):
        check_object_fields(policy, "configurationPolicies", index, "name", "platforms")
        name = policy.get("name")
        object_id = require_object_id(policy, "configurationPolicies", index)
        platform = policy.get("platforms") or "unknown"
        ref = object_ref("configurationPolicies", object_id, name, platform)
        assigned, disagreement = is_assigned(policy)
        if disagreement:
            disagreements.append(dict(ref, **disagreement))
        if not assigned:
            excluded.append(dict(ref, reason="unassigned"))
            continue

        base = {"platform": platform, "collection": "configurationPolicies",
                "object_type": CONFIG_POLICY_TYPE, "object_id": object_id,
                "object_name": name}
        rows.append(name_row(base, name, "$.configurationPolicies[%d].name" % index))

        leaves = []
        settings_path = "$.configurationPolicies[%d].settings" % index
        policy_settings = expect(policy.get("settings"), list, settings_path,
                                 "an array of settings") or []
        for setting_index, setting in enumerate(policy_settings):
            setting_path = "%s[%d]" % (settings_path, setting_index)
            expect(setting, dict, setting_path, "an object", required=True)
            # Required: a setting entry with no instance cannot be read, and skipping it
            # would drop a live setting from the standard without a word.
            instance = expect(setting.get("settingInstance"), dict,
                              setting_path + ".settingInstance", "an object",
                              required=True)
            walk_setting_instance(instance, setting_path + ".settingInstance", leaves)

        # Two leaves in one policy sharing a settingDefinitionId would collide on row_key
        # and silently become one row. Zero occurrences in this dump, but the tree permits
        # it -- so disambiguate deterministically by occurrence order rather than leaving
        # a data-shape change to corrupt the id-map later.
        seen = {}
        for definition_id, kind, raw, json_path in leaves:
            seen[definition_id] = seen.get(definition_id, 0) + 1
            occurrence = seen[definition_id]
            setting_id = definition_id if occurrence == 1 \
                else "%s#%d" % (definition_id, occurrence)
            required = leaf_value(kind, raw, max_inline)
            setting_name, display_value, hit = resolve_display(
                definitions, definition_id, occurrence, kind, raw, required, max_inline,
                misses)
            rows.append(dict(base, setting_id=setting_id, setting_name=setting_name,
                             required_value=required, display_value=display_value,
                             mode="enforced", verify=json_path,
                             _kind="scalar" if kind in SCALAR_KINDS else "collection",
                             _hit=hit))
    return rows


def property_bag_rows(dump, collection, max_inline, excluded, disagreements):
    """deviceConfigurations and deviceCompliancePolicies -- flat property bags.

    One row per meaningful non-null property. 'Meaningful' excludes METADATA_KEYS, any
    '@'-prefixed Graph annotation and any `<field>@odata.type` companion key, nulls, and
    EMPTY lists/dicts. Empty containers are dropped because in Graph they mean 'not
    configured' -- 20 of them in this dump, every one a row that would say nothing and
    then churn the moment Graph changed how it renders an unset collection.

    mode is 'compliance' for deviceCompliancePolicies: a compliance policy does not
    configure the device, it gates access on what the device reports. Rendering both as
    'enforced' would tell a reader a setting is imposed when it is merely measured.

    setting_name is the property name, never a label: there is no definitions catalog
    for these collections, and a hand-written label would be an invented one.
    """
    rows = []
    mode = "compliance" if collection == "deviceCompliancePolicies" else "enforced"
    for index, obj in enumerate(collection_objects(dump, collection)):
        name_key = "displayName" if obj.get("displayName") is not None else "name"
        check_object_fields(obj, collection, index, name_key, "@odata.type")
        name = obj.get(name_key)
        object_id = require_object_id(obj, collection, index)
        odata_type = obj.get("@odata.type")
        platform = platform_from_odata(odata_type)
        ref = object_ref(collection, object_id, name, platform)
        assigned, disagreement = is_assigned(obj)
        if disagreement:
            disagreements.append(dict(ref, **disagreement))
        if not assigned:
            excluded.append(dict(ref, reason="unassigned"))
            continue

        base = {"platform": platform, "collection": collection,
                "object_type": odata_type, "object_id": object_id, "object_name": name}
        rows.append(name_row(base, name, "$.%s[%d].%s" % (collection, index, name_key)))
        for key in sorted(obj):
            if key in METADATA_KEYS or key.startswith("@") or key.endswith("@odata.type"):
                continue
            value = obj[key]
            if value is None:
                continue
            if isinstance(value, (list, dict)) and not value:
                continue
            required = render_scalar(value, max_inline)
            rows.append(dict(base, setting_id=key, setting_name=key,
                             required_value=required, display_value=required,
                             mode=mode, verify="$.%s[%d].%s" % (collection, index, key),
                             _kind=None, _hit=None))
    return rows


# ------------------------------------------------------------------ export completeness

TRUNCATED_OVERRIDE = "--allow-truncated"


def setting_count_check(dump):
    """The acceptance test: each configurationPolicies entry's settingCount must equal the
    number of settings the export fetched. Pure; the refusal is build_rows' decision.

    -> {"policies", "counted", "mismatches", "uncounted", "allowed_by"}. Every entry is
    checked, assigned or not -- see the module docstring. Run AFTER row extraction, so
    the id, name and platform it reports have already passed their shape checks.
    """
    mismatches, uncounted = [], []
    policies = collection_objects(dump, "configurationPolicies")
    for index, policy in enumerate(policies):
        base = "$.configurationPolicies[%d]" % index
        fetched = expect(policy.get("settings"), list, base + ".settings",
                         "an array of settings") or []
        declared = policy.get("settingCount")
        # bool is an int in Python; `"settingCount": true` is not a count.
        if declared is not None and (isinstance(declared, bool)
                                     or not isinstance(declared, int)):
            raise GeneratorError(
                "%s.settingCount is %s, expected an integer. This is not the shape an "
                "Intune configuration export has -- the export is malformed or "
                "truncated. Re-run it." % (base, json_kind(declared)))
        ref = object_ref("configurationPolicies", policy.get("id"), policy.get("name"),
                         policy.get("platforms") or "unknown")
        if declared is None:
            uncounted.append(ref)
        elif declared != len(fetched):
            mismatches.append(dict(ref, setting_count=declared,
                                   settings_fetched=len(fetched)))
    return {"policies": len(policies),
            "counted": len(policies) - len(uncounted),
            "mismatches": sorted(mismatches, key=object_sort_key),
            "uncounted": sorted(uncounted, key=object_sort_key),
            "allowed_by": None}


def describe_mismatch(entry):
    return "%r (object id %s): settingCount %d, settings fetched %d" % (
        entry["name"], entry["object_id"], entry["setting_count"],
        entry["settings_fetched"])


def truncation_refusal(mismatches):
    n = len(mismatches)
    lines = ["%d Settings Catalog %s a settingCount that disagrees with the settings the "
             "export fetched -- the export is truncated:"
             % (n, "policy declares" if n == 1 else "policies declare")]
    lines += ["  " + describe_mismatch(entry) for entry in mismatches]
    lines += [
        "  A truncated dump generates a truncated baseline, and a diff against it reports",
        "  NO CHANGE. Re-run the export. Pass %s only to generate from this dump"
        % TRUNCATED_OVERRIDE,
        "  knowingly: the override is recorded in meta.setting_count_check, the cycle",
        "  record and the preview, so the result can never pass for a complete baseline."]
    return "\n".join(lines)


# -------------------------------------------------------------------------- assembly

def sort_key(row):
    """The contract order: platform, collection, object name, object id, name row first,
    then setting id. Explicit ranks rather than string sorting, and case-folded, so that
    neither ASCII order nor a platform respelt 'IOS' can reshuffle the file.

    The name row's first place is its own key component rather than a consequence of
    '@' sorting early -- '#', '!' and every digit sort before '@' in ASCII.
    """
    return (platform_rank(row["platform"]),
            COLLECTION_RANK.get(row["collection"], len(COLLECTION_RANK)),
            row["collection"],
            (row["object_name"] or "").casefold(),
            (row["object_id"] or "").lower(),
            0 if row["setting_id"] == NAME_SETTING_ID else 1,
            row["setting_id"].casefold(),
            row["setting_id"])


def object_sort_key(ref):
    return (platform_rank(ref["platform"]),
            COLLECTION_RANK.get(ref["collection"], len(COLLECTION_RANK)),
            ref["collection"], (ref["name"] or "").casefold(),
            (ref["object_id"] or "").lower())


def build_rows(dump, generated_at, source_sha256, source_name,
               platform_filter="all", max_inline=256, definitions=None,
               definitions_sha256=None, allow_truncated=False):
    """Pure transform: dump -> the full baseline document. No clock, no filesystem.

    Kept free of datetime.now() and of file IO on purpose -- it is the part that has to be
    testable and reproducible, and a function that reads the clock is neither.

    `definitions` is the parsed setting-definitions.json document, or None to turn
    display resolution off. Raises GeneratorError on data the contract cannot key, and on
    a truncated dump (settingCount != len(settings)) unless `allow_truncated`.
    """
    index = Definitions(definitions) if definitions is not None else None
    misses = {"definitions": set(), "options": set()}
    excluded, disagreements = [], []

    rows = config_policy_rows(dump, max_inline, index, misses, excluded, disagreements)
    for collection in ("deviceConfigurations", "deviceCompliancePolicies"):
        rows += property_bag_rows(dump, collection, max_inline, excluded, disagreements)

    for row in rows:
        row["row_key"] = "|".join([row["collection"], row["object_id"].lower(),
                                   row["setting_id"].lower()])
        row["enforced_at"] = "Intune > %s > %s" % (row["collection"],
                                                   row["object_name"] or "")

    # A duplicate key means two settings would share one id and the diff would silently
    # drop one. It can only come from a duplicated object id or two property names that
    # differ by case alone -- neither exists in Graph, so this is a malformed export.
    seen, duplicates = set(), set()
    for row in rows:
        (duplicates if row["row_key"] in seen else seen).add(row["row_key"])
    if duplicates:
        raise GeneratorError(
            "%d duplicate row_key(s), e.g. %s. Two rows cannot share an identity -- the "
            "export repeats an object id. Refusing rather than merging them."
            % (len(duplicates), sorted(duplicates)[0]))

    # Whole dump, before the platform filter: a truncated export is broken everywhere.
    count_check = setting_count_check(dump)
    if count_check["mismatches"]:
        if not allow_truncated:
            raise GeneratorError(truncation_refusal(count_check["mismatches"]))
        # Recorded only when the override actually let something through, so passing the
        # flag on a complete dump cannot change a byte of the output.
        count_check["allowed_by"] = TRUNCATED_OVERRIDE

    wanted = PLATFORM_FILTER.get(platform_filter)
    if wanted:
        rows = [r for r in rows if platform_prefix(r["platform"]) == wanted]
        excluded = [e for e in excluded if platform_prefix(e["platform"]) == wanted]
        disagreements = [d for d in disagreements
                         if platform_prefix(d["platform"]) == wanted]

    rows.sort(key=sort_key)

    counts, objects, leaf_counts = {}, {}, {}
    resolved = unresolved = 0
    for row in rows:
        per = counts.setdefault(row["platform"], {})
        per[row["collection"]] = per.get(row["collection"], 0) + 1
        is_name = row["setting_id"] == NAME_SETTING_ID
        if is_name:
            per = objects.setdefault(row["platform"], {})
            per[row["collection"]] = per.get(row["collection"], 0) + 1
        if row["collection"] == "configurationPolicies":
            leaf = leaf_counts.setdefault(row["platform"], {"policies": 0, "scalar": 0,
                                                            "collection": 0, "rows": 0})
            if is_name:
                leaf["policies"] += 1
            else:
                leaf[row["_kind"]] += 1
                leaf["rows"] += 1
        if row["_hit"] is True:
            resolved += 1
        elif row["_hit"] is False:
            unresolved += 1
        del row["_kind"], row["_hit"]

    # Only the misses on rows that survived the platform filter are reported.
    kept = {r["setting_id"].split("#")[0] for r in rows}
    display_resolution = {
        "mode": "catalog" if index is not None else "none",
        "resolved": resolved,
        "unresolved": unresolved,
        "missing_definitions": sorted(d for d in misses["definitions"] if d in kept),
        "missing_options": sorted(o for o in misses["options"]
                                  if o.split(" = ")[0] in kept),
        "unfetched_at_export": index.unfetched if index is not None else [],
    }

    return {
        "meta": {
            "generator_version": GENERATOR_VERSION,
            "generated_from": source_name,
            "generated_at": generated_at,
            "source_sha256": source_sha256,
            "definitions_sha256": definitions_sha256,
            "display_resolution": display_resolution,
            # The acceptance test on the whole dump, unfiltered by --platform.
            "setting_count_check": count_check,
            "row_count": len(rows),
            "counts": counts,
            "scope": {
                "assigned_only": True,
                "excluded_objects": sorted(excluded, key=object_sort_key),
                "assignment_disagreements": sorted(disagreements, key=object_sort_key),
                "collections": COLLECTIONS,
                "platform_filter": platform_filter,
                "in_scope_objects": objects,
                # The verified 84 / 56 / 2 scalar figures, so a run can be checked without
                # re-deriving them. Name rows are not leaves and are not counted here.
                "leaf_counts": leaf_counts,
            },
        },
        "rows": rows,
    }


# ---------------------------------------------------------------------------- id map

def load_id_map(path):
    """-> the {row_key: id} dict inside a schema-2 map. {} if the file does not exist.

    Refuses -- never repairs -- anything else. Starting from {} over a damaged map would
    hand every row a brand-new id and break id permanence, the one thing the map exists
    to protect, while the output looked perfectly normal.
    """
    path = Path(path)
    if not path.is_file():
        return {}
    try:
        document = json.loads(path.read_text(encoding="utf-8-sig"))
    except ValueError as exc:
        raise GeneratorError(
            "id map %s is not valid JSON: %s\n"
            "  Refusing to continue: starting from an empty map would renumber every row\n"
            "  and invalidate every id already cited in a ticket or exemption. Restore it\n"
            "  from git history." % (path, exc))
    if not isinstance(document, dict):
        raise GeneratorError("id map %s must be a JSON object, got %s"
                             % (path, type(document).__name__))
    if "schema" not in document:
        raise GeneratorError(
            "id map %s is a v1 map (a flat {row_key: id} object with no \"schema\").\n"
            "  v1 keys carry the policy NAME; v2 keys carry the Intune object id, so no v1\n"
            "  key can be carried across, and migrating it would renumber every row while\n"
            "  looking as though nothing had changed. Refusing.\n"
            "  Delete %s and regenerate: the first v2 run issues fresh ids in reading\n"
            "  order, and from then on they are permanent." % (path, path))
    if document.get("schema") != ID_MAP_SCHEMA:
        raise GeneratorError("id map %s declares schema %r; this generator reads schema %d "
                             "only." % (path, document.get("schema"), ID_MAP_SCHEMA))
    ids = document.get("ids")
    if not isinstance(ids, dict):
        raise GeneratorError("id map %s has no \"ids\" object." % path)
    bad = sorted(k for k, v in ids.items()
                 if not isinstance(v, str) or not ID_PATTERN.match(v))
    if bad:
        raise GeneratorError("id map %s holds %d malformed id(s), e.g. %s -> %r."
                             % (path, len(bad), bad[0], ids[bad[0]]))
    owners = {}
    for key in sorted(ids):
        owners.setdefault(ids[key], []).append(key)
    shared = sorted(i for i, keys in owners.items() if len(keys) > 1)
    if shared:
        raise GeneratorError(
            "id map %s issues %s to %d different rows. One id, one setting, forever -- "
            "fix the map from git history before generating." % (path, shared[0],
                                                               len(owners[shared[0]])))
    return dict(ids)


def id_map_text(ids):
    """schema first, ids sorted -- so the file diffs as a pure append between cycles."""
    return json.dumps({"schema": ID_MAP_SCHEMA, "ids": {k: ids[k] for k in sorted(ids)}},
                      indent=2, ensure_ascii=False) + "\n"


def assign_ids(rows, id_map):
    """Attach a permanent BP-XXX-nnnn to every row. Mutates id_map with NEW keys only.

    The high-water mark is taken from the WHOLE map, not from the rows in play, which is
    what reserves a retired row's number: its entry is never deleted, so its number can
    never be handed out again. That also makes --platform safe -- generating only Windows
    cannot renumber macOS, because the macOS entries are still in the map. Rows arrive in
    sort order, so a fresh map numbers each prefix in reading order.
    """
    high = {}
    for existing in id_map.values():
        match = ID_PATTERN.match(existing)
        if match:
            prefix, number = match.group(1), int(match.group(2))
            high[prefix] = max(high.get(prefix, 0), number)

    for row in rows:
        key = row["row_key"]
        if key not in id_map:
            prefix = platform_prefix(row["platform"])
            high[prefix] = high.get(prefix, 0) + 1
            if high[prefix] > 9999:
                raise GeneratorError("id prefix %s is exhausted (four digits)." % prefix)
            id_map[key] = "BP-%s-%04d" % (prefix, high[prefix])
        row["id"] = id_map[key]


def ordered(row):
    return {field: row[field] for field in FIELD_ORDER}


# -------------------------------------------------------------------------- markdown
# Policy names and setting values are untrusted text: anyone who can edit an Intune
# policy name can put markdown or HTML in it. Everything is escaped on the way out.

def md_text(text):
    """Plain inline text, safe inside a table cell or a heading.

    '<' and '&' are entity-escaped because they are the only characters that can open
    HTML or an entity. A bare '>' mid-cell is inert in GFM and is left alone, so
    'Intune > deviceConfigurations > X' stays readable in the source.
    """
    text = "" if text is None else str(text)
    text = text.replace("&", "&amp;").replace("<", "&lt;")
    for char in "\\`*_[]|":
        text = text.replace(char, "\\" + char)
    return text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")


def md_code(text):
    """An inline code span that no backtick, pipe or newline in the value can break.

    Table cells are split BEFORE inline parsing, so a pipe needs escaping even inside
    backticks -- and a backslash run right before a pipe is doubled, or a value ending in
    a backslash turns the escape into an escaped backslash followed by a live cell
    delimiter (which is how micromark, GitBook's parser, reads it).
    """
    text = "" if text is None else str(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\\n")
    if text == "":
        return "*(empty)*"
    runs = [len(run) for run in re.findall(r"`+", text)]
    fence = "`" * ((max(runs) + 1) if runs else 1)
    body = re.sub(r"(\\*)\|", lambda m: m.group(1) * 2 + "\\|", text)
    if body.startswith("`") or body.endswith("`") or \
            (body.startswith(" ") and body.endswith(" ")):
        body = " " + body + " "
    return fence + body + fence


def md_heading(text):
    """Heading text. A trailing '#' run would be read as a closing sequence and eaten."""
    body = md_text(text) or "(unnamed object)"
    return re.sub(r"#+$", lambda m: "\\#" * len(m.group(0)), body)


MD_HEADER = ("| ID | Setting | Required value | Authority | Mode | Enforced at "
             "| Deviation | Verify |\n"
             "| --- | --- | --- | --- | --- | --- | --- | --- |")


def default_ratified_date(dump_path, generated_at):
    """The dated folder's own name -- the date `ratify <date>` names -- else the date of
    generated_at. Either way deterministic: never today's date."""
    folder = Path(dump_path).parent.name
    if DATE_PATTERN.match(folder):
        return folder
    return (generated_at or "")[:10]


def md_row(row, authority, provisional=frozenset()):
    setting = md_text(row["setting_name"]) if row["setting_name"] != row["setting_id"] \
        else md_code(row["setting_id"])
    value = md_text(row["display_value"]) if row["display_value"] != row["required_value"] \
        else md_code(row["required_value"])
    row_id = row["id"] + (" (provisional)" if row["id"] in provisional else "")
    return "| %s | %s | %s | %s | %s | %s | none | %s |" % (
        row_id, setting, value, md_text(authority), row["mode"],
        md_text(row["enforced_at"]),
        md_code("%s = %s" % (row["setting_id"], row["required_value"])))


def to_markdown(doc, ratified_date=None, provisional=frozenset()):
    """A reviewer's PREVIEW of the rows as a standard would show them. Not the standard.

    It is NOT the block the ratify step injects: `run_config_cycle.py ratify` renders
    the authoritative block between the GENERATED markers itself, from baseline-rows.json,
    with its own provenance comment and tables. The two carry the same rows and the same
    8 columns, but they are not byte-identical and nothing may treat this output as the
    page. One renderer owns the page; this is for looking at a dump before ratifying it.

    In-scope table, excluded-and-why table, then one ### section per object, each
    opening with the object id. Setting and Required value show the human label where
    one was resolved (plain text) and the raw Graph value otherwise (code) -- so a reader
    can always tell which they are looking at. Verify always carries the raw pair the
    diff actually compares.

    `provisional` is the set of ids that are not in the persisted id-map. The CLI never
    writes the map in this mode, so those numbers are shown marked, not promised.
    """
    meta = doc["meta"]
    if ratified_date is None:
        ratified_date = (meta.get("generated_at") or "")[:10]
    authority = "bitpool:ratified %s" % ratified_date
    rows = doc["rows"]
    scope = meta["scope"]
    n_provisional = sum(1 for r in rows if r["id"] in provisional)

    lines = [
        "*Preview rendered by `generate_baseline.py` %s from %s (sha256 %s). This is not "
        "the standard: `run_config_cycle.py ratify` renders the authoritative block "
        "between the GENERATED markers, and this preview is not byte-identical to it.*"
        % (md_text(meta["generator_version"]), md_code(meta["generated_from"]),
           md_code((meta["source_sha256"] or "")[:16])),
        "",
    ]
    if n_provisional:
        lines += [
            "*%d id(s) marked (provisional) are not yet in `id-map.json`. A preview never "
            "writes the map, so those numbers are fixed only when `baseline-rows.json` is "
            "generated.*" % n_provisional,
            "",
        ]
    truncated = (meta.get("setting_count_check") or {}).get("mismatches") or []
    if truncated:
        lines += [
            "**INCOMPLETE: generated under %s.** %d Settings Catalog %s the export fetched "
            "a different number of settings than `settingCount` declares, so these rows "
            "are not the whole tenant: %s." % (
                md_code(TRUNCATED_OVERRIDE), len(truncated),
                "policy, for which" if len(truncated) == 1 else "policies, for which",
                "; ".join(md_text(describe_mismatch(entry)) for entry in truncated)),
            "",
        ]
    lines += [
        "### In scope",
        "",
        "| Collection | Objects | Setting instances |",
        "| --- | --- | --- |",
    ]
    total_objects = total_settings = 0
    for collection in COLLECTIONS:
        n_objects = sum(1 for r in rows if r["collection"] == collection
                        and r["setting_id"] == NAME_SETTING_ID)
        n_settings = sum(1 for r in rows if r["collection"] == collection
                         and r["setting_id"] != NAME_SETTING_ID)
        total_objects += n_objects
        total_settings += n_settings
        lines.append("| `%s` | %d | %d |" % (collection, n_objects, n_settings))
    lines.append("| **Total** | **%d** | **%d** |" % (total_objects, total_settings))
    lines += [
        "",
        "Each object also carries one `identity` row holding its display name, so a "
        "rename is one visible change: %d rows in all." % len(rows),
        "",
        "### Excluded, and why",
        "",
        "| Object | Object ID | Collection | Reason |",
        "| --- | --- | --- | --- |",
    ]
    if scope["excluded_objects"]:
        for ref in scope["excluded_objects"]:
            lines.append("| %s | %s | `%s` | %s |" % (
                md_text(ref["name"]), md_code(ref["object_id"]), ref["collection"],
                md_text(ref["reason"])))
    else:
        lines.append("| *(none)* | — | — | — |")

    current = None
    for row in rows:
        if (row["collection"], row["object_id"]) != current:
            current = (row["collection"], row["object_id"])
            lines += [
                "",
                "### %s" % md_heading(row["object_name"]),
                "",
                "Object ID %s · %s · %s · platform %s" % (
                    md_code(row["object_id"]), md_code(row["collection"]),
                    md_code(row["object_type"]), md_code(row["platform"])),
                "",
                MD_HEADER,
            ]
        lines.append(md_row(row, authority, provisional))
    return "\n".join(lines).strip() + "\n"


# ---------------------------------------------------------------------- cycle record

def folder_files(folder, record_path):
    """Every file in the dated folder the record vouches for, sorted, with its hash.

    Excluded: the record itself, dotfiles, and the downstream products (see
    DOWNSTREAM_FILES) -- they are generated after the record and hash their own inputs.
    """
    record = Path(record_path).resolve() if record_path else None
    files = []
    for entry in sorted(Path(folder).iterdir(), key=lambda p: p.name):
        name = entry.name
        if not entry.is_file() or name.startswith(".") or name == CYCLE_RECORD_NAME \
                or DOWNSTREAM_FILES.match(name):
            continue
        if record is not None and entry.resolve() == record:
            continue
        data = entry.read_bytes()
        files.append({"name": name, "bytes": len(data), "sha256": sha256_bytes(data)})
    return files


def manifest_value(manifest, *path):
    node = manifest
    for part in path:
        if not isinstance(node, dict):
            return None
        node = node.get(part)
    return node


def git_dirty_cell(manifest, warnings):
    """tool.git_dirty: a commit id alone vouches for code that may not be what ran.

    Absent (an older manifest) and null (the exporter could not tell) are different
    facts and are stated differently -- neither is ever read as 'clean'."""
    tool = manifest.get("tool")
    if not isinstance(tool, dict) or "git_dirty" not in tool:
        return "not recorded (no `tool.git_dirty` in the manifest)"
    dirty = tool["git_dirty"]
    if dirty is True:
        warnings.append("the exporter ran with uncommitted changes (tool.git_dirty is "
                        "true in %s)" % MANIFEST_NAME)
        return "**dirty** — the exporter differed from that commit when it ran"
    if dirty is False:
        return "clean"
    if dirty is None:
        return "**not determined** — `null` in the manifest"
    warnings.append("tool.git_dirty in %s is %s, not a boolean"
                    % (MANIFEST_NAME, json_kind(dirty)))
    return "**unreadable** — %s, not a boolean" % json_kind(dirty)


def incidents_cell(manifest, warnings):
    """incidents: what the collection run itself recorded as going wrong.

    The exporter refuses to place a dump with incidents unless --accept-incomplete, so
    a non-empty list here means someone accepted an incomplete collection. That has to
    be as visible in the record as the collector, or an accepted-incomplete dump reads
    exactly like a clean one."""
    if "incidents" not in manifest:
        return "not recorded — the manifest has no `incidents` field"
    incidents = manifest["incidents"]
    if incidents is None:
        warnings.append("incidents is null in %s -- completeness not determined"
                        % MANIFEST_NAME)
        return "**not determined** — `null` in the manifest"
    if not isinstance(incidents, list):
        warnings.append("incidents in %s is %s, not a list"
                        % (MANIFEST_NAME, json_kind(incidents)))
        return "**unreadable** — %s, not a list" % json_kind(incidents)
    if not incidents:
        return "none recorded"
    warnings.append("%d incident(s) recorded in %s -- this collection is incomplete"
                    % (len(incidents), MANIFEST_NAME))
    items = "<br>".join(
        "%d. %s" % (number, md_text(item if isinstance(item, str)
                                    else json.dumps(item, sort_keys=True)))
        for number, item in enumerate(incidents, 1))
    return ("**%d recorded** — this collection is INCOMPLETE; the exporter places such a "
            "dump only under `--accept-incomplete`:<br>%s" % (len(incidents), items))


def completeness_section(check):
    """The cycle record's statement of the settingCount acceptance test. A baseline
    generated under --allow-truncated must read as incomplete here, not just on stderr."""
    mismatches, uncounted = check["mismatches"], check["uncounted"]
    lines = [
        "",
        "## Export completeness",
        "",
        "Every `configurationPolicies` entry, assigned or not, declares `settingCount`, and "
        "the export must have fetched exactly that many settings. A truncated export "
        "generates a truncated baseline, and a diff against it reports no change, so "
        "`generate_baseline.py` refuses one unless %s is passed."
        % md_code(TRUNCATED_OVERRIDE),
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Policies checked | %d |" % check["policies"],
        "| Carrying a `settingCount` | %d |" % check["counted"],
        "| Count mismatches | %s |" % (
            "none" if not mismatches else
            "**%d — generated under %s; this baseline is INCOMPLETE**"
            % (len(mismatches), md_code(check["allowed_by"] or TRUNCATED_OVERRIDE))),
        "| No `settingCount` | %s |" % (
            "none" if not uncounted else
            "**%d — completeness of these cannot be counted**" % len(uncounted)),
    ]
    if mismatches:
        lines += ["", "| Policy | Object ID | Platform | settingCount | Settings fetched |",
                  "| --- | --- | --- | ---: | ---: |"]
        for entry in mismatches:
            lines.append("| %s | %s | %s | %d | %d |" % (
                md_text(entry["name"]), md_code(entry["object_id"]),
                md_code(entry["platform"]), entry["setting_count"],
                entry["settings_fetched"]))
    if uncounted:
        lines += ["", "Policies with no `settingCount`:", "",
                  "| Policy | Object ID | Platform |", "| --- | --- | --- |"]
        for entry in uncounted:
            lines.append("| %s | %s | %s |" % (md_text(entry["name"]),
                                               md_code(entry["object_id"]),
                                               md_code(entry["platform"])))
    return lines


def render_cycle_record(doc, folder_name, files, manifest, baseline_sha256=None):
    """The dated folder's README.md. Pure: every input is passed in.

    Descriptive only. It deliberately never says whether this folder is the ratified
    baseline -- that would make the record change on ratification, and ratification has
    exactly two homes: the standards' approval headers and ../RATIFIED.
    """
    meta = doc["meta"]
    scope = meta["scope"]
    resolution = meta["display_resolution"]
    warnings = []

    if manifest is not None and manifest_value(manifest, "collection_date"):
        collection_date = str(manifest["collection_date"])
        date_source = "`%s`" % MANIFEST_NAME
    elif DATE_PATTERN.match(folder_name or ""):
        collection_date = folder_name
        date_source = "the folder name; no `%s` in this folder" % MANIFEST_NAME
    else:
        collection_date = (meta["generated_at"] or "")[:10]
        date_source = "`generated_at`; no manifest and the folder name is not a date"

    title = "Intune configuration dump %s" % collection_date
    lines = [
        "---",
        "type: Record",
        "title: %s" % title,
        "description: Generated record of the %s Intune configuration export — collection "
        "provenance, file hashes, row counts, scope exclusions and display resolution."
        % collection_date,
        "audience:",
        "  - security-team",
        "  - auditors",
        "  - ai-agents",
        "last_reviewed: %s" % collection_date,
        "status: active",
        "doc_type: record",
        "sources:",
        "  - internal",
        "  - drata:DCF-12",
        "keywords:",
        "  - configuration-hardening",
        "  - intune",
        "  - baseline",
        "  - cycle-record",
        "related:",
        "  - ../../hardening-standard-windows-endpoints.md",
        "  - ../../hardening-standard-macos-endpoints.md",
        "  - ../../hardening-standard-ios-endpoints.md",
        "iso27001_controls:",
        "  - \"8.9\"",
        "drata_controls:",
        "  - DCF-12",
        "risk_level: high",
        "requires_admin: false",
        "---",
        "",
        "# %s" % title,
        "",
        "Generated cycle record for one Intune configuration export. It is **descriptive**: "
        "it states what was collected, when, by whom, and what was derived from it. It is "
        "not a standard and approves nothing. Do not edit it by hand; regenerate it with "
        "%s." % md_code("run_config_cycle.py generate %s" % folder_name),
        "",
        "## Ratification is not recorded here",
        "",
        "This record never states whether this dump is the approved baseline. Ratification "
        "is a deliberate, reviewed act, recorded in the approval header of each hardening "
        "standard (`Ratified from`) and in `../RATIFIED`, not here.",
        "",
        "## Collection",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Collection date | %s (from %s) |" % (md_text(collection_date), date_source),
    ]
    if manifest is None:
        not_recorded = ("not recorded — no `%s` in this folder, and deliberately not "
                        "inferred from file times" % MANIFEST_NAME)
        lines += ["| Collected at (UTC) | %s |" % not_recorded,
                  "| Collector | %s |" % not_recorded,
                  "| Tenant ID | not recorded |",
                  "| Client ID | not recorded |",
                  "| Tool | not recorded |",
                  "| Incidents | not recorded — no `%s` in this folder |" % MANIFEST_NAME]
    else:
        def cell(value, missing="**not determined** — `null` in the manifest"):
            return md_code(value) if value not in (None, "") else missing
        upn = manifest_value(manifest, "collector", "upn")
        oid = manifest_value(manifest, "collector", "object_id")
        source = manifest_value(manifest, "collector", "source")
        collector = cell(upn)
        if oid:
            collector += " · object id %s" % md_code(oid)
        if source:
            collector += " · from %s" % md_text(source)
        if not upn:
            warnings.append("collector identity is null in %s" % MANIFEST_NAME)
        tool = cell(manifest_value(manifest, "tool", "name"))
        tool += " · git commit %s" % cell(manifest_value(manifest, "tool", "git_commit"),
                                          "not recorded")
        tool += " · working tree %s" % git_dirty_cell(manifest, warnings)
        lines += ["| Collected at (UTC) | %s |"
                  % cell(manifest_value(manifest, "collected_at_utc")),
                  "| Collector | %s |" % collector,
                  "| Tenant ID | %s |" % cell(manifest_value(manifest, "tenant_id")),
                  "| Client ID | %s |" % cell(manifest_value(manifest, "client_id")),
                  "| Tool | %s |" % tool,
                  "| Incidents | %s |" % incidents_cell(manifest, warnings),
                  "| Manifest schema | %s |" % cell(manifest_value(manifest, "schema"))]

    recorded = manifest_value(manifest, "files") if manifest is not None else None
    recorded = recorded if isinstance(recorded, dict) else {}
    lines += [
        "",
        "## Files",
        "",
        "| File | Bytes | SHA-256 | Check |",
        "| --- | ---: | --- | --- |",
    ]
    on_disk = {f["name"] for f in files}
    for entry in files:
        name = entry["name"]
        checks = []
        if name in recorded:
            want = recorded[name] if isinstance(recorded[name], dict) else {}
            if want.get("sha256") == entry["sha256"] and \
                    want.get("bytes") in (None, entry["bytes"]):
                checks.append("matches the manifest")
            else:
                checks.append("**MISMATCH** — the manifest records sha256 %s"
                              % md_code(want.get("sha256")))
                warnings.append("%s does not match its manifest hash" % name)
        if name == meta["generated_from"]:
            checks.append("source of `baseline-rows.json` — %s"
                          % ("matches `source_sha256`"
                             if entry["sha256"] == meta["source_sha256"]
                             else "**does not match** `source_sha256`"))
        if name == "baseline-rows.json" and baseline_sha256 is not None:
            if entry["sha256"] == baseline_sha256:
                checks.append("written by this run")
            else:
                checks.append("**stale** — not the output of this run")
                warnings.append("baseline-rows.json in the folder is not this run's output")
        if not checks:
            checks.append("not listed in the manifest" if manifest is not None
                          else "no manifest to check against")
        lines.append("| %s | %d | %s | %s |" % (md_code(name), entry["bytes"],
                                              md_code(entry["sha256"]), "; ".join(checks)))
    for name in sorted(set(recorded) - on_disk):
        lines.append("| %s | — | %s | **MISSING** — listed in the manifest, absent here |"
                     % (md_code(name), md_code(manifest_value(recorded, name, "sha256"))))
        warnings.append("%s is listed in the manifest but absent" % name)
    lines += [
        "",
        "`diff-vs-*.md`, `diff-vs-*.json` and `evidence-pack.html` are not listed: they are "
        "generated after this record and carry their own input hashes.",
    ]
    lines += completeness_section(meta["setting_count_check"])
    lines += [
        "",
        "## Rows derived",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Generator | `generate_baseline.py` %s |" % md_text(meta["generator_version"]),
        "| Generated at | %s |" % md_code(meta["generated_at"]),
        "| Source | %s · sha256 %s |" % (md_code(meta["generated_from"]),
                                         md_code(meta["source_sha256"])),
        "| Rows | %d |" % meta["row_count"],
        "",
        "| Platform | Collection | Objects | Setting rows | Name rows | Total rows |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    totals = [0, 0, 0]
    for platform, per in meta["counts"].items():
        for collection, total in per.items():
            objects = scope["in_scope_objects"].get(platform, {}).get(collection, 0)
            totals[0] += objects
            totals[1] += total - objects
            totals[2] += total
            lines.append("| %s | %s | %d | %d | %d | %d |" % (
                md_code(platform), md_code(collection), objects, total - objects,
                objects, total))
    lines.append("| **Total** | | **%d** | **%d** | **%d** | **%d** |"
                 % (totals[0], totals[1], totals[0], totals[2]))
    lines += [
        "",
        "Every in-scope object carries exactly one name row (`@displayName`, mode "
        "`identity`), so a rename is a single visible change and no other row's identity "
        "moves.",
        "",
        "Settings Catalog leaves (`configurationPolicies`), scalar versus collection-valued:",
        "",
        "| Platform | Policies | Scalar leaves | Collection leaves | Setting rows |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for platform, leaf in scope["leaf_counts"].items():
        lines.append("| %s | %d | %d | %d | %d |" % (
            md_code(platform), leaf["policies"], leaf["scalar"], leaf["collection"],
            leaf["rows"]))
    if not scope["leaf_counts"]:
        lines.append("| *(none)* | 0 | 0 | 0 | 0 |")

    lines += [
        "",
        "## Scope exclusions",
        "",
        "Only assigned objects are in scope: an unassigned object enforces nothing. %d "
        "object(s) were excluded." % len(scope["excluded_objects"]),
        "",
        "| Object | Object ID | Collection | Platform | Reason |",
        "| --- | --- | --- | --- | --- |",
    ]
    for ref in scope["excluded_objects"]:
        lines.append("| %s | %s | %s | %s | %s |" % (
            md_text(ref["name"]), md_code(ref["object_id"]), md_code(ref["collection"]),
            md_code(ref["platform"]), md_text(ref["reason"])))
    if not scope["excluded_objects"]:
        lines.append("| *(none)* | — | — | — | — |")
    disagreements = scope["assignment_disagreements"]
    lines += ["", "Assignment disagreements (`isAssigned` versus `assignments`): %s"
              % ("none." if not disagreements else
                 "%d — each treated as assigned, and a finding." % len(disagreements))]
    if disagreements:
        lines += ["", "| Object | Object ID | Collection | isAssigned | Assignments |",
                  "| --- | --- | --- | --- | ---: |"]
        for ref in disagreements:
            lines.append("| %s | %s | %s | %s | %d |" % (
                md_text(ref["name"]), md_code(ref["object_id"]),
                md_code(ref["collection"]), md_code(render_scalar(ref["isAssigned"], 256)),
                ref["assignments"]))

    lines += ["", "## Display resolution", "", "| Field | Value |", "| --- | --- |"]
    if resolution["mode"] == "none":
        lines += ["| Mode | `none` — no setting definitions were supplied. Every Setting "
                  "and Required value shows the raw Graph identifier. |",
                  "| Resolved | 0 |", "| Unresolved | 0 |",
                  "| Definitions sha256 | not applicable |"]
    else:
        lines += ["| Mode | `catalog` — labels from the Settings Catalog definitions |",
                  "| Resolved | %d |" % resolution["resolved"],
                  "| Unresolved | %d |" % resolution["unresolved"],
                  "| Definitions sha256 | %s |" % md_code(meta["definitions_sha256"]),
                  "| Definitions missing | %d |" % len(resolution["missing_definitions"]),
                  "| Choice values with no matching option | %d |"
                  % len(resolution["missing_options"]),
                  "| Definitions the exporter could not fetch | %d |"
                  % len(resolution["unfetched_at_export"])]
    lines += ["",
              "Labels are for display only. The diff compares the raw `required_value`, so "
              "a Microsoft relabel never creates a difference, and every miss falls back to "
              "the raw value rather than a guessed label."]
    return "\n".join(lines).strip() + "\n", warnings


# ------------------------------------------------------------------------------ main

def write_atomic(path, text):
    """Write via a sibling temp file, so an interrupted run never leaves half a file --
    for the id map, half a file is a renumbering waiting to happen."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(str(temp), str(path))


def read_json(path, label):
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise GeneratorError("cannot read %s %s: %s" % (label, path, exc))
    try:
        return raw, json.loads(raw.decode("utf-8-sig"))
    except ValueError as exc:
        raise GeneratorError("%s %s is not valid JSON: %s" % (label, path, exc))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate canonical hardening-standard baseline rows (contract v2) "
                    "from an Intune configuration dump.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Ids are permanent and come from --id-map (schema 2). Never delete "
               "entries from it; a v1 map is refused.")
    parser.add_argument("--dump", required=True, help="raw intune-config-export.json")
    parser.add_argument("--out", required=True,
                        help="baseline-rows.json, or the preview .md with --format markdown")
    parser.add_argument("--id-map", required=True,
                        help="persistent row_key -> id map (schema 2); created if absent. "
                             "Lives at the dumps/ root, NOT inside a dated folder -- it "
                             "spans cycles.")
    parser.add_argument("--generated-at", required=True,
                        help="ISO8601 UTC, e.g. 2026-09-24T00:00:00Z. Passed in, not read "
                             "from the clock, so output is reproducible.")
    parser.add_argument("--definitions",
                        help="setting-definitions.json from the exporter. Turns on "
                             "display resolution (labels only -- never the diffed value).")
    # --readme is an alias: run_config_cycle.py probes --help for that spelling.
    parser.add_argument("--cycle-record", "--readme", metavar="PATH", dest="cycle_record",
                        help="also write the dated folder's README.md cycle record")
    parser.add_argument("--manifest",
                        help="collection-manifest.json for the cycle record (default: "
                             "the one beside --dump, if present)")
    parser.add_argument("--platform", default="all",
                        choices=["windows", "macos", "ios", "all"],
                        help="emit one platform or everything (default: all)")
    parser.add_argument("--format", default="json", choices=["json", "markdown"],
                        dest="fmt",
                        help="json baseline (default), or markdown: a PREVIEW for "
                             "review. Not the block ratify injects (ratify renders its "
                             "own), and it never writes the id-map -- ids for rows not "
                             "yet in the map are marked provisional")
    parser.add_argument("--ratified-date", metavar="YYYY-MM-DD",
                        help="date for the markdown Authority column (default: the dated "
                             "folder name of --dump, else the date of --generated-at)")
    parser.add_argument("--max-inline", type=int, default=256,
                        help="strings longer than this become sha256:<digest> (default: "
                             "256 -- catches the base64 plists, nothing else)")
    parser.add_argument("--allow-empty", action="store_true",
                        help="permit a dump whose three collections are absent or hold "
                             "zero objects (refused by default -- that is what a failed "
                             "export looks like)")
    parser.add_argument(TRUNCATED_OVERRIDE, action="store_true", dest="allow_truncated",
                        help="generate even though a configurationPolicies entry's "
                             "settingCount disagrees with the settings the export fetched "
                             "(refused by default -- a truncated export diffs as NO "
                             "CHANGE). The override is recorded in "
                             "meta.setting_count_check, the cycle record and the preview")
    args = parser.parse_args(argv)

    try:
        return run(args)
    except GeneratorError as exc:
        sys.exit("error: %s" % exc)


def run(args):
    dump_path = Path(args.dump)
    if not dump_path.is_file():
        raise GeneratorError("dump not found: %s" % dump_path)
    if args.cycle_record and args.platform != "all":
        raise GeneratorError("--cycle-record describes the whole dump; it cannot be "
                             "combined with --platform %s." % args.platform)
    if args.cycle_record and args.fmt == "markdown":
        raise GeneratorError("--format markdown is a preview and writes nothing but --out; "
                             "it cannot be combined with --cycle-record. The cycle record "
                             "is written with the json baseline.")
    if args.ratified_date and not DATE_PATTERN.match(args.ratified_date):
        raise GeneratorError("--ratified-date must be YYYY-MM-DD, got %r"
                             % args.ratified_date)

    raw, dump = read_json(dump_path, "dump")
    source_sha256 = sha256_bytes(raw)

    # A dump that parses but carries none of the three collections is what a truncated
    # or failed export looks like. Left unguarded the run emits a 0-row baseline and
    # exits 0, i.e. it manufactures an authoritative-looking EMPTY hardening standard
    # out of a broken export. Refuse by default; --allow-empty keeps it testable.
    #
    # A dump whose collections are all present but EMPTY is the same failure one step
    # later -- an export that signed in but read nothing -- so the refusal counts
    # OBJECTS, not keys. Shapes are checked first, so a collection that is not an array
    # is refused by name instead of being counted as empty.
    if not isinstance(dump, dict):
        raise GeneratorError("dump %s is not a JSON object" % dump_path.name)
    present = [c for c in COLLECTIONS if dump.get(c) is not None]
    held = {c: len(collection_objects(dump, c)) for c in present}
    if not present and not args.allow_empty:
        raise GeneratorError(
            "dump %s carries none of the expected collections (%s).\n"
            "  That is what a truncated or failed export looks like, and generating from\n"
            "  it would write an EMPTY hardening standard that reports success.\n"
            "  Re-run the export, or pass --allow-empty if an empty baseline is genuinely\n"
            "  what you want." % (dump_path.name, ", ".join(COLLECTIONS)))
    if present and not sum(held.values()) and not args.allow_empty:
        raise GeneratorError(
            "dump %s holds zero objects across the expected collections (%s).\n"
            "  That is what an export that signed in but read nothing looks like, and\n"
            "  generating from it would write an EMPTY hardening standard that reports\n"
            "  success. Re-run the export, or pass --allow-empty if an empty baseline is\n"
            "  genuinely what you want."
            % (dump_path.name, ", ".join("%s %s" % (c, held[c] if c in held else "absent")
                                         for c in COLLECTIONS)))

    definitions = definitions_sha256 = None
    if args.definitions:
        definitions_raw, definitions = read_json(args.definitions, "setting definitions")
        definitions_sha256 = sha256_bytes(definitions_raw)

    manifest = None
    manifest_path = Path(args.manifest) if args.manifest \
        else dump_path.parent / MANIFEST_NAME
    if args.cycle_record and (args.manifest or manifest_path.is_file()):
        _, manifest = read_json(manifest_path, "collection manifest")
        if not isinstance(manifest, dict):
            raise GeneratorError("collection manifest %s is not a JSON object"
                                 % manifest_path)

    # Load the map BEFORE generating so a refused map leaves nothing half-written.
    id_map_path = Path(args.id_map)
    id_map = load_id_map(id_map_path)
    before = id_map_text(id_map) if id_map_path.is_file() else None

    doc = build_rows(dump, args.generated_at, source_sha256, dump_path.name,
                     args.platform, args.max_inline, definitions, definitions_sha256,
                     allow_truncated=args.allow_truncated)
    # A markdown preview numbers new rows on a COPY of the map and never writes it. The
    # id-map is permanent, so a look at a dump must not be able to reserve numbers in it.
    preview = args.fmt == "markdown"
    working = dict(id_map) if preview else id_map
    assign_ids(doc["rows"], working)
    provisional = frozenset(working[k] for k in working if k not in id_map) \
        if preview else frozenset()
    doc["rows"] = [ordered(r) for r in doc["rows"]]

    after = id_map_text(id_map)
    if not preview and after != before:
        write_atomic(id_map_path, after)

    out_path = Path(args.out)
    if args.fmt == "markdown":
        ratified = args.ratified_date or default_ratified_date(dump_path,
                                                               args.generated_at)
        out_text = to_markdown(doc, ratified, provisional)
    else:
        out_text = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
    write_atomic(out_path, out_text)

    warnings = []
    if args.cycle_record:
        record_path = Path(args.cycle_record)
        files = folder_files(dump_path.parent, record_path)
        baseline_sha = sha256_text(out_text) if args.fmt == "json" else None
        record, warnings = render_cycle_record(doc, dump_path.parent.name, files,
                                               manifest, baseline_sha)
        write_atomic(record_path, record)

    meta, scope = doc["meta"], doc["meta"]["scope"]
    names = sum(sum(per.values()) for per in scope["in_scope_objects"].values())
    print("rows          %d  (%d setting rows + %d name rows)"
          % (meta["row_count"], meta["row_count"] - names, names))
    print("source sha256 %s" % source_sha256)
    if preview:
        print("id-map        %d keys in %s -- NOT written (markdown preview); %d "
              "provisional id(s)" % (len(id_map), id_map_path, len(provisional)))
    else:
        print("id-map        %d keys -> %s%s" % (len(id_map), id_map_path,
                                                 "" if after != before else " (unchanged)"))
    for platform, per in meta["counts"].items():
        for collection, total in per.items():
            objects = scope["in_scope_objects"].get(platform, {}).get(collection, 0)
            print("  %-10s %-25s %2d objects  %3d rows" % (platform, collection, objects,
                                                          total))
    for platform, leaf in scope["leaf_counts"].items():
        print("  %-10s leaves: scalar %3d  collection %2d" % (platform, leaf["scalar"],
                                                              leaf["collection"]))
    print("excluded      %d unassigned objects" % len(scope["excluded_objects"]))
    check = meta["setting_count_check"]
    print("settingCount  %d of %d policies counted, %d mismatch(es)%s"
          % (check["counted"], check["policies"], len(check["mismatches"]),
             " -- ALLOWED by %s, baseline INCOMPLETE" % check["allowed_by"]
             if check["mismatches"] else ""))
    for entry in check["mismatches"]:
        print("WARNING       truncated under %s: %s"
              % (check["allowed_by"], describe_mismatch(entry)), file=sys.stderr)
    if check["uncounted"]:
        print("WARNING       %d Settings Catalog policies carry no settingCount; their "
              "completeness cannot be counted: %s"
              % (len(check["uncounted"]),
                 "; ".join("%r (object id %s)" % (e["name"], e["object_id"])
                           for e in check["uncounted"])), file=sys.stderr)
    resolution = meta["display_resolution"]
    print("display       mode %s  resolved %d  unresolved %d"
          % (resolution["mode"], resolution["resolved"], resolution["unresolved"]))
    if scope["assignment_disagreements"]:
        print("WARNING       %d objects disagree between isAssigned and assignments"
              % len(scope["assignment_disagreements"]))
    if not meta["row_count"]:
        print("WARNING       0 rows in scope (%d object(s) excluded as unassigned)"
              % len(scope["excluded_objects"]), file=sys.stderr)
    for warning in warnings:
        print("WARNING       %s" % warning, file=sys.stderr)
    print("wrote         %s" % out_path)
    if args.cycle_record:
        print("wrote         %s" % args.cycle_record)
    return 0


if __name__ == "__main__":
    sys.exit(main())
