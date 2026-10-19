#!/usr/bin/env python3
"""Build ONE consolidated reconciliation workbook from every dump in a cycle folder.

WHY THIS EXISTS
---------------
The review has seven registers behind it -- AWS, Azure, GitHub, the wiki hardware page,
Intune, Entra and Drata vendors -- and the findings that matter are the ones that only
appear when two of them are laid side by side. A device is only "in Intune and on no
register" if you hold both at once. A holder only has two endpoints if you have grouped the
whole export. An account is only in no register at all if you have the directory AND the
sync group.

Run five separate reconciliations and each one produces its own little report, in its own
shape, at its own moment. The human then has five documents to hold in their head, no single
place to write a decision, and no way to see that the same person appears in three of them.
One workbook, one row per asset, one Notes column beats that -- not because it is tidier,
but because the judgement calls land in one place where they can be read together.

THE NOTES COLUMN IS THE POINT
-----------------------------
This script decides nothing. It flags, and a human dispositions. Every row ships with an
EMPTY `Notes` cell and that is deliberate -- it is the only column in the workbook that
carries judgement, and it is the only one a machine must never pre-fill.

Two kinds of note come back, and they are NOT the same thing:

  1. A DISPOSITION -- "device retired and wiped", "returned to IT stock", "vendor no longer
     used". It resolves this row, this cycle. It goes in the evidence and it is done.

  2. A SCOPE CHANGE -- "this resource type should be excluded", "this section is not an
     asset class". It resolves this row AND changes what the next cycle collects. A scope
     change left only in the workbook is lost the moment the cycle closes: the next run
     re-collects the same thing and re-flags it, and the person who decided is not in the
     room. A scope-change note MUST be carried back into `scripts/snapshot.py`'s allow-list
     and into the wiki page it concerns.

See `references/reconciliation-workbook.md` for how a human works the column.

WHEN TO RUN IT
--------------
After EVERY dump is in the cycle folder, never before. A workbook built from four of seven
dumps looks complete and reports a clean estate for the three registers it never read.
Which is why this script prints what it found AND what it did not, and refuses to be quiet
about a missing input -- but still builds, because a partial workbook over the dumps that
exist is useful and a crash is not.

Pure Python 3 standard library. Run through WSL -- the native Windows python/python3 are
broken Microsoft Store stubs and exit without running:

    wsl -e bash -lc 'python3 build_reconciliation.py \
        --cycle-folder "/mnt/c/.../Asset register review - 2026 09" \
        -o "/mnt/c/.../reconciliation_2026-09.csv"'
"""

import argparse
import collections
import csv
import datetime
import glob
import json
import os
import re
import sys

# --------------------------------------------------------------------------------------
# Every read in this file goes through here, and every read uses utf-8-sig.
#
# PowerShell redirection (`... > file.json`) writes a UTF-8 BOM. So does Intune's export and
# so does Entra's. Plain utf-8 does not strip it: json.load then fails on a stray
# before the opening brace, and csv.DictReader silently names the first column
# "﻿Device ID" so every lookup of "Device ID" returns None. This has cost two runs.
# utf-8-sig reads BOM and no-BOM files identically, so there is no case where it is wrong.
# --------------------------------------------------------------------------------------
ENC = "utf-8-sig"

REQUIRED_KEYS = ["OwnerGroup", "Purpose", "Criticality", "DataClassification",
                 "IsPersonalData"]

COLUMNS = ["Register", "AssetID", "Name", "Type", "Owner", "Criticality",
           "DataClassification", "IsPersonalData", "Status", "Flag", "FlagDetail", "Notes"]

# The flag vocabulary. Short machine-ish tokens so the workbook can be filtered and so two
# cycles' workbooks can be compared; the human-readable specifics go in FlagDetail.
F_MISSING_KEYS = "MISSING_REQUIRED_KEYS"
F_NO_TAGS = "NO_GOVERNANCE_TAGS"
F_IN_INTUNE = "IN_INTUNE_NOT_ON_REGISTER"
F_ON_REGISTER = "ON_REGISTER_NOT_IN_INTUNE"
F_TWO_ENDPOINTS = "TWO_ENDPOINTS_SAME_HOLDER"
F_USER_DISABLED = "PRIMARY_USER_DISABLED"
F_OUTSIDE_SYNC = "OUTSIDE_DRATA_SYNC_GROUP"
F_VENDOR_NO_OWNER = "VENDOR_NO_OWNER"
F_VENDOR_REVIEW = "VENDOR_REVIEW_DUE"
F_EXCLUDED_TYPE = "EXCLUDED_TYPE_SEEN"

# Wiki sections that ARE the physical register. First column is the label -- the asset label,
# the card number for access cards, or the physical label written on a USB drive or other
# portable storage media.
WIKI_SECTIONS = [
    "## Current Windows fleet",
    "### Windows endpoints with no Intune record",
    "## Current MacBook fleet",
    "## Current iPhone fleet",
    "### IT stock",
    "## Printers, AV and other office equipment",
    "## Other computing equipment",
    "## Network equipment",
    "## Access cards",
    # A physical register section, NOT an Intune endpoint section: a USB drive has no Intune
    # record, so it must never be added to WIKI_ENDPOINT_SECTIONS -- every row would flag as
    # ON_REGISTER_NOT_IN_INTUNE. It is confirmed by the physical walk, like a monitor.
    "## Portable storage media",
]
# Only these four have an Intune counterpart. A monitor or a USB drive absent from Intune is not
# a finding -- there is no live system behind it at all; it is confirmed by the physical walk.
WIKI_ENDPOINT_SECTIONS = {
    "## Current Windows fleet",
    "### Windows endpoints with no Intune record",
    "## Current MacBook fleet",
    "## Current iPhone fleet",
}
HEADING_RE = re.compile(r"^#{1,6} ")

# Intune sentinel values meaning "no date", not real timestamps.
NULL_DATES = {"0001-01-01 00:00:00.0000000", "9999-12-31 23:59:59.0000000"}
OS_CLASS = {"Windows": "Windows", "MacOS": "macOS", "iOS/iPadOS": "iOS"}

# Drata's dynamic sync group excludes jobTitle == "Service Account" by rule, so a service
# account outside the group is the rule working, not a finding.
SERVICE_ACCOUNT_TITLE = "service account"


# =======================================================================================
# normalisation
# =======================================================================================

def norm(value):
    """Key a name for cross-register comparison. Compare on this; REPORT the original.

    macOS names a device after its owner using a CURLY apostrophe, U+2019 -- `David's
    MacBook Pro` -- and the wiki page is typed with a straight U+0027. Comparing the raw
    strings reports every MacBook as missing from the register AND unaccounted for in Intune
    at the same time: six phantom findings out of one character, in a shape that reads
    exactly like a real register collapse. Whoever chases it spends a morning on nothing.

    Also collapses whitespace (the wiki is hand-typed and double spaces happen) and
    casefolds. Nothing here is written back -- the CSV always carries the original string,
    because "your register says X and Intune says Y" is only actionable if both are shown.
    """
    s = (value or "").strip()
    for curly in ("’", "‘", "ʼ", "´"):
        s = s.replace(curly, "'")
    return " ".join(s.split()).casefold()


HANDSET_RE = re.compile(r"^IT-MOB-APP-(.+)$", re.I)


def to_intune_label(label):
    """Rewrite a wiki handset label into the form Intune enrols it under.

    The register labels a handset `IT-MOB-APP-<serial>` per the naming convention; Intune
    enrols it as `iPhone-<serial>`. Same device, two schemes. Without this rewrite every
    legacy-enrolled handset is reported missing from both sides simultaneously -- the same
    double-phantom shape as the apostrophe, and just as convincing.
    """
    m = HANDSET_RE.match(label or "")
    return "iPhone-%s" % m.group(1) if m else label


def clean(value):
    v = (value or "").strip()
    return "" if v in NULL_DATES else v


# =======================================================================================
# discovery
# =======================================================================================

# Each input: key -> (glob, human description, whether several files are merged).
INPUTS = [
    ("aws", "aws-snapshot_*.json", "AWS snapshot (scripts/snapshot.py aws)", False),
    ("azure", "azure-snapshot_*.json", "Azure snapshot (scripts/snapshot.py azure)", False),
    ("github", "github-snapshot_*.json", "GitHub snapshot (scripts/snapshot.py github)", False),
    ("intune", "DevicesWithInventory_*.csv", "Intune 'Export all data'", False),
    ("entra_users", "entra-users_*.json", "Graph /users", False),
    ("sync_group", "entra-drata-sync-group-members_*.json", "Graph Drata Sync Group members", False),
    ("wiki", "bpw-hardware-asset-inventory_*.md", "BPW hardware asset inventory page", False),
    # Vendors are globbed loosely ON PURPOSE. Drata's list endpoint pages at 50 and the
    # second page is conventionally saved as `drata-vendors-page2_<date>.json`, which a
    # strict `drata-vendors_*.json` glob does NOT match. Reading only page one reviews 50
    # of 82 vendors and reports a tidy register that is 39% unread -- exactly the
    # under-reading `references/drata-vendor-register.md` warns about. Merged by id below,
    # and checked against pagination.totalCount.
    ("vendors", "drata-vendors*.json", "Drata vendor list (all pages)", True),
]


def discover(folder):
    """Find every input by pattern. Report what is missing; never fail on it."""
    found, missing = {}, []
    for key, pattern, desc, multi in INPUTS:
        hits = sorted(glob.glob(os.path.join(folder, pattern)))
        if not hits:
            missing.append((key, pattern, desc))
            continue
        found[key] = hits if multi else hits[-1]
        if not multi and len(hits) > 1:
            print("  NOTE  %d files match %s -- using the last by name: %s"
                  % (len(hits), pattern, os.path.basename(hits[-1])))
    return found, missing


def load_json(path):
    with open(path, encoding=ENC) as fh:
        return json.load(fh)


def load_csv(path):
    with open(path, newline="", encoding=ENC) as fh:
        return list(csv.DictReader(fh))


# =======================================================================================
# row helpers
# =======================================================================================

def row(register, asset_id, name="", rtype="", owner="", crit="", dataclass="",
        personal="", status="", flags=(), detail=""):
    """Build one workbook row. `Notes` is ALWAYS empty -- it is the human's column."""
    return {
        "Register": register,
        "AssetID": asset_id,
        "Name": name,
        "Type": rtype,
        "Owner": owner,
        "Criticality": crit,
        "DataClassification": dataclass,
        "IsPersonalData": personal,
        "Status": status,
        "Flag": ";".join(f for f in flags if f),
        "FlagDetail": detail,
        "Notes": "",
    }


# =======================================================================================
# cloud registers
# =======================================================================================

def cloud_rows(snap, label):
    """One row per snapshot item, with the required-key check applied where it applies."""
    rows = []
    for asset_id, item in sorted(snap.get("items", {}).items()):
        attrs = item.get("attrs") or {}
        unit = item.get("unit", "")

        # Azure tags at RESOURCE GROUP level. Its `resource` items are tracked for
        # existence only and are not expected to carry governance keys -- flagging them
        # would invent a 34-item shortfall that does not exist and drown the 8 groups that
        # genuinely are the Azure register. AWS and GitHub tag the item itself.
        checked = not (label == "Azure" and unit == "resource")

        present = [k for k in REQUIRED_KEYS if str(attrs.get(k, "")).strip()]
        missing = [k for k in REQUIRED_KEYS if k not in present]

        flags, detail = [], ""
        if checked and missing:
            if not present:
                flags.append(F_NO_TAGS)
                detail = ("none of the five required governance keys is set (%s)"
                          % ", ".join(REQUIRED_KEYS))
            else:
                flags.append(F_MISSING_KEYS)
                detail = "missing: %s (has: %s)" % (", ".join(missing), ", ".join(present))

        rows.append(row(
            label, asset_id,
            name=item.get("name", ""), rtype=item.get("type", ""),
            owner=attrs.get("OwnerGroup", ""),
            crit=attrs.get("Criticality", ""),
            dataclass=attrs.get("DataClassification", ""),
            personal=attrs.get("IsPersonalData", ""),
            status=unit, flags=flags, detail=detail,
        ))
    return rows


def scope_rows(aws_snap):
    """One SCOPE row per AWS resource type the allow-list dropped.

    `snapshot.py` scopes AWS with an ALLOW-LIST of primary asset types. An allow-list cannot
    drop a type by accident -- that is the whole reason it was chosen over a deny-list. But
    it CAN drop a genuinely new primary type silently: a new managed data store appears,
    nobody adds it to the list, and it is simply absent from the register with nothing
    anywhere saying so. Absence leaves no trace to notice.

    These rows are that trace. Each distinct excluded type gets a row a human can write
    "this should be included" against, and that note is a SCOPE CHANGE -- it has to be
    carried back into AWS_INCLUDED_TYPES in scripts/snapshot.py, or the next cycle drops it
    again and the decision evaporates.
    """
    seen = (aws_snap.get("scope") or {}).get("excluded_types_seen") or {}
    rows = []
    for rtype, count in sorted(seen.items(), key=lambda kv: (-kv[1], kv[0])):
        rows.append(row(
            "SCOPE", rtype, name=rtype, rtype="aws resource type",
            status="%d seen" % count, flags=[F_EXCLUDED_TYPE],
            detail=("%d AWS resource(s) of this type were excluded from the register by the "
                    "primary-type allow-list. Note 'include' here only if this type holds or "
                    "runs something in its own right -- doing so is a scope change and must "
                    "also be added to AWS_INCLUDED_TYPES in scripts/snapshot.py" % count),
        ))
    return rows


# =======================================================================================
# the wiki register
# =======================================================================================

def parse_wiki(text):
    """Pull every pipe table under the register's section headings.

    Returns (rows, unlisted) where `unlisted` names any other section in the page that
    carries a pipe table. A heading rename or a new section would otherwise take its whole
    table out of the workbook with no symptom -- the run just gets quietly smaller.
    """
    rows, unlisted = [], []
    section, header, in_table = None, None, False
    other_section, other_rows, other_header = None, 0, None

    def flush_other():
        # Only worth reporting if it looks like an asset table: a ## or ### heading (the
        # same depth as the real register sections) and a header row whose first column is
        # named. A `| | |` two-column prose table under the H1, and the lifecycle-status
        # legend, are formatting -- reporting them trains the reader to skip this block,
        # which is the one place a renamed register heading would show up.
        if (other_section and other_rows and other_header
                and other_header[0] and other_section.startswith("##")):
            unlisted.append((other_section, other_rows))

    for line in text.splitlines():
        s = line.strip()

        if HEADING_RE.match(s):
            flush_other()
            section = s if s in WIKI_SECTIONS else None
            other_section = None if s in WIKI_SECTIONS else s
            other_rows, other_header = 0, None
            header, in_table = None, False
            continue

        if not s.startswith("|"):
            in_table = False
            continue

        cells = [c.strip() for c in s.strip("|").split("|")]

        if section is None:
            # Count rows under an unlisted heading so the omission is visible.
            if other_section:
                if other_header is None:
                    other_header = cells
                elif not (cells and cells[0] and set(cells[0]) <= {"-", ":"}):
                    other_rows += 1
            continue

        # Header row, then the |---|---| separator beneath it.
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if cells and cells[0] and set(cells[0]) <= {"-", ":"}:
            in_table = True
            continue
        if not in_table:
            continue

        def col(*names):
            for n in names:
                if n in header:
                    i = header.index(n)
                    if i < len(cells):
                        return cells[i].replace("`", "").replace("**", "").strip()
            return ""

        label = cells[0].replace("`", "").replace("**", "").strip()
        rows.append({
            "section": section,
            "label": label,
            "owner": col("owner", "holder"),
            "item": col("item", "device", "card"),
            "model": col("model"),
            "status": col("status"),
            "notes": col("notes"),
        })

    flush_other()
    return rows, unlisted


def wiki_rows(entries, intune_by_key):
    rows, unlabelled = [], 0
    for e in entries:
        label = e["label"]
        flags, detail = [], ""

        if not label:
            # A blank label is a REAL state on this page, not a parse failure: an asset
            # Bitpool owns that was never labelled (an unlabelled iPhone 17e, the mesh AP
            # record, a card number never recorded). Dropping them silently shrinks the
            # register by exactly the rows that most need attention.
            unlabelled += 1
        elif e["section"] in WIKI_ENDPOINT_SECTIONS:
            if norm(to_intune_label(label)) not in intune_by_key:
                flags.append(F_ON_REGISTER)
                detail = ("no Intune record under `%s`. NOT automatically a deletion -- it "
                          "may be a device never enrolled, or one retired with no evidence "
                          "of disposal. Confirm it" % to_intune_label(label))

        rows.append(row(
            "Wiki", label or "(unlabelled)",
            name=e["item"] or e["model"],
            rtype=e["section"].lstrip("# "),
            owner=e["owner"], status=e["status"],
            flags=flags, detail=detail,
        ))
    return rows, unlabelled


# =======================================================================================
# Intune + Entra
# =======================================================================================

def intune_rows(devices, register_keys, account_state):
    rows = []
    by_name = {}
    for d in devices:
        by_name[d.get("Device name", "")] = d

    # Two endpoints held by one person is the ONLY signal that a replaced laptop is still
    # enrolled -- a replaced device reports compliant, encrypted and checking in, identical
    # to one in daily use, and no Intune view flags it.
    computers = [d for d in devices
                 if OS_CLASS.get(d.get("OS", "")) in ("Windows", "macOS")]
    by_holder = collections.defaultdict(list)
    for d in computers:
        upn = clean(d.get("Primary user UPN")).lower()
        if upn:
            by_holder[upn].append(d)

    pair_detail = {}
    for upn, held in by_holder.items():
        if len(held) < 2:
            continue
        per_class = collections.defaultdict(list)
        for d in held:
            per_class[OS_CLASS.get(d.get("OS", ""), d.get("OS", ""))].append(d)
        for cls, group in per_class.items():
            if len(group) > 1:
                # Name the PAIR. Never assert which superseded which from enrolment date:
                # a re-enrolled device carries a NEWER enrolment date than its own
                # replacement. Observed 2026-09-17 -- LAPTOP-D3321J8L, an HP ENVY bought
                # 05/2024 and being retired, was re-enrolled 2026-09-03, against its 2026
                # replacement LAPTOP-PW0NHYX4 enrolled 2026-07-06. Ordering on enrolment
                # names the NEW machine as the one to wipe. Purchase date settles it and
                # purchase date lives on the wiki register, not in Intune.
                names = [d.get("Device name", "") for d in group]
                for d in group:
                    others = [n for n in names if n != d.get("Device name", "")]
                    pair_detail[d.get("Device name", "")] = (
                        "same-platform pair (%s) with %s, both held by %s. One is likely "
                        "'Replaced - pending retirement'. WHICH ONE is decided by the "
                        "purchase dates on the wiki register, NOT by enrolment date -- a "
                        "re-enrolled device carries a newer enrolment date than its own "
                        "replacement. Confirm before wiping anything"
                        % (cls, ", ".join("`%s`" % n for n in others), upn))
        if len(per_class) > 1:
            # A Windows laptop and a MacBook held by one person is a two-device issue, not
            # a supersession. Reporting it as one sends someone to wipe a live machine.
            classes = sorted(per_class)
            for d in held:
                pair_detail.setdefault(d.get("Device name", ""), (
                    "holds %d endpoints across different platforms (%s) -- this is NOT a "
                    "supersession, only same-platform devices replace each other. Confirm "
                    "both are genuinely issued to %s"
                    % (len(held), ", ".join(classes), upn)))

    for d in devices:
        name = d.get("Device name", "")
        upn = clean(d.get("Primary user UPN")).lower()
        flags, details = [], []

        if register_keys is not None and norm(name) not in register_keys:
            flags.append(F_IN_INTUNE)
            details.append("enrolled in Intune with no row on the wiki register. Intune "
                           "wins on existence -- add it")

        if account_state is not None and upn:
            enabled = account_state.get(upn)
            if enabled is None:
                flags.append(F_USER_DISABLED)
                details.append("primary user `%s` is not in the directory export at all -- "
                               "resolve before treating the device as owned" % upn)
            elif not enabled:
                flags.append(F_USER_DISABLED)
                details.append("primary user `%s` holds a DISABLED account -- a live, "
                               "encrypted, compliant endpoint belonging to a leaver" % upn)

        if not upn:
            details.append("no primary user recorded, so the device has no recorded owner")

        if name in pair_detail:
            flags.append(F_TWO_ENDPOINTS)
            details.append(pair_detail[name])

        rows.append(row(
            "Intune", name,
            name=("%s %s" % (d.get("Manufacturer", ""), d.get("Model", ""))).strip(),
            rtype=OS_CLASS.get(d.get("OS", ""), d.get("OS", "")),
            owner=clean(d.get("Primary user display name")) or upn,
            status=clean(d.get("Compliance")),
            flags=flags, detail=" | ".join(details),
        ))
    return rows


def entra_rows(users, members):
    """Exception rows only -- people are not an asset class.

    `references/drata-vendor-register.md` is explicit: personnel are not assets under A.5.9.
    The directory earns its place in this workbook for exactly one reason: an account that
    sits outside the Drata Sync Group appears in NO register at all -- not Drata personnel,
    not anywhere -- so nothing else in the cycle would ever surface it. Emitting all ~100
    accounts as clean asset rows would misstate what the workbook is counting.
    """
    member_ids = {m.get("id") for m in members if m.get("id")}
    member_upns = {(m.get("userPrincipalName") or "").lower() for m in members}

    rows, service_accounts = [], 0
    for u in users:
        # accountEnabled comes back as True/False with a leading capital in some exports and
        # as a JSON bool in others. Compare case-insensitively on the string form -- a
        # lowercase "true" test silently matches nothing and reports the whole directory.
        enabled = str(u.get("accountEnabled", "")).strip().lower() == "true"
        if not enabled:
            continue
        upn = (u.get("userPrincipalName") or "")
        if u.get("id") in member_ids or upn.lower() in member_upns:
            continue

        title = (u.get("jobTitle") or "").strip()
        if title.lower() == SERVICE_ACCOUNT_TITLE:
            # The sync group is a dynamic group that excludes jobTitle = "Service Account"
            # by rule. A service account outside it is the rule working, not a finding.
            service_accounts += 1
            rows.append(row("Entra", upn, name=u.get("displayName", ""), rtype="account",
                            owner=title,
                            status="enabled; outside sync group by rule (Service Account)"))
            continue

        rows.append(row(
            "Entra", upn, name=u.get("displayName", ""), rtype="account",
            owner=title, status="enabled",
            flags=[F_OUTSIDE_SYNC],
            detail=("enabled account outside the Drata Sync Group, and its jobTitle is not "
                    "'Service Account' so the dynamic group's exclusion does not explain it. "
                    "This account is in NO register -- either correct the attribute that "
                    "keeps it out, or record why it is excluded"),
        ))
    return rows, service_accounts


# =======================================================================================
# Drata vendors
# =======================================================================================

# Field names Drata has used for the Bitpool-side security owner. Checked tolerantly,
# because the list endpoint and the per-vendor endpoint do not return the same shape.
OWNER_FIELDS = ("owner", "securityOwner", "ownerEmail", "userOwners", "vendorOwner")


def vendor_rows(payloads, as_of):
    merged, total_claimed = {}, 0
    for p in payloads:
        data = p.get("data") if isinstance(p, dict) else p
        for v in data or []:
            merged[v.get("id")] = v
        pag = (p.get("pagination") or {}) if isinstance(p, dict) else {}
        total_claimed = max(total_claimed, pag.get("totalCount") or 0)

    owner_field_present = any(f in v for v in merged.values() for f in OWNER_FIELDS)

    rows = []
    for vid, v in sorted(merged.items(), key=lambda kv: (kv[1].get("name") or "")):
        # `archivedAt` is NOT a reliable archive signal. Observed 2026-09-17: 46 vendors
        # carry status ARCHIVED and only 27 of them have archivedAt set -- the older
        # archivings never stamped the timestamp. Testing archivedAt alone flags 19
        # long-archived vendors as review-overdue, which buries the ones that genuinely
        # are. Treat either as archived; `/ask-drata` covers status flags that lie.
        archived = bool(v.get("archivedAt")) or (v.get("status") or "").upper() == "ARCHIVED"
        flags, details = [], []

        owner = ""
        for f in OWNER_FIELDS:
            if v.get(f):
                owner = str(v[f])
                break
        if owner_field_present and not owner and not archived:
            flags.append(F_VENDOR_NO_OWNER)
            details.append("no security owner recorded. A vendor with no owner has nobody "
                           "accountable for its review")

        renewal = (v.get("renewalDate") or "")[:10]
        if not archived:
            if not renewal:
                flags.append(F_VENDOR_REVIEW)
                details.append("no renewal or review date set, so nothing ever falls due")
            elif renewal < as_of:
                flags.append(F_VENDOR_REVIEW)
                details.append("renewal/review date %s is in the past as at %s"
                               % (renewal, as_of))

        status = v.get("status") or ""
        if archived and v.get("archivedAt"):
            status = "ARCHIVED (%s)" % v["archivedAt"][:10]

        rows.append(row(
            "Drata", str(vid), name=v.get("name", ""),
            rtype=v.get("category", "") or v.get("type", ""),
            owner=owner,
            crit=v.get("risk", "") or ("Critical" if v.get("critical") else ""),
            personal=str(v.get("hasPii", "")),
            status=status, flags=flags, detail=" | ".join(details),
        ))
    return rows, merged, total_claimed, owner_field_present


# =======================================================================================
# main
# =======================================================================================

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cycle-folder", required=True,
                    help="the evidence folder holding this cycle's dumps")
    ap.add_argument("-o", "--out", required=True, help="the workbook CSV to write")
    ap.add_argument("--as-of", default=datetime.date.today().isoformat(),
                    help="date used for 'review due' tests (default: today)")
    a = ap.parse_args()

    if not os.path.isdir(a.cycle_folder):
        sys.exit("ERROR: no such cycle folder: %s" % a.cycle_folder)

    print("Cycle folder : %s" % a.cycle_folder)
    print("As at        : %s\n" % a.as_of)

    print("Inputs discovered")
    print("-----------------")
    found, missing = discover(a.cycle_folder)
    for key, pattern, desc, multi in INPUTS:
        if key in found:
            hits = found[key] if multi else [found[key]]
            for h in hits:
                print("  found    %-14s %s" % (key, os.path.basename(h)))
    if missing:
        print()
        for key, pattern, desc in missing:
            # Report, never fail. A partial workbook over the dumps that exist is useful.
            # But say it loudly: a missing dump means that register was NOT reviewed, and a
            # workbook that stays quiet about it reads as a clean result for it.
            print("  MISSING  %-14s no file matching %s  (%s)" % (key, pattern, desc))
        print("\n  These registers were NOT reviewed. A row absent from this workbook because")
        print("  its dump is absent is not a clean row -- it is an unchecked register.")
    print()

    rows = []
    counts_note = []

    # ------------------------------------------------------------------ cloud
    aws_snap = load_json(found["aws"]) if "aws" in found else None
    for key, label in (("aws", "AWS"), ("azure", "Azure"), ("github", "GitHub")):
        if key in found:
            snap = aws_snap if key == "aws" else load_json(found[key])
            rows.extend(cloud_rows(snap, label))

    # ------------------------------------------------------------------ wiki
    register_keys, unlabelled = None, 0
    wiki_entries, unlisted = [], []
    if "wiki" in found:
        with open(found["wiki"], encoding=ENC) as fh:
            wiki_entries, unlisted = parse_wiki(fh.read())
        if not wiki_entries:
            print("  WARNING  the wiki page parsed to zero rows. Have the section headings")
            print("           been renamed? Expected:\n             %s\n"
                  % "\n             ".join(WIKI_SECTIONS))
        register_keys = {norm(to_intune_label(e["label"]))
                         for e in wiki_entries if e["label"]}

    # ------------------------------------------------------------------ entra
    account_state = None
    if "entra_users" in found:
        users = load_json(found["entra_users"]).get("value", [])
        account_state = {(u.get("userPrincipalName") or "").lower():
                         str(u.get("accountEnabled", "")).strip().lower() == "true"
                         for u in users}
        if "sync_group" in found:
            members = load_json(found["sync_group"]).get("value", [])
            e_rows, svc = entra_rows(users, members)
            rows.extend(e_rows)
            counts_note.append("Entra rows are exceptions only -- accounts outside the Drata "
                               "Sync Group (%d service accounts among them, excluded by the "
                               "group's own rule). People are not an asset class; the "
                               "directory is here to catch an account that is in no register "
                               "at all." % svc)
        else:
            counts_note.append("Sync-group dump absent, so OUTSIDE_DRATA_SYNC_GROUP was not "
                               "evaluated.")

    # ------------------------------------------------------------------ intune
    devices = load_csv(found["intune"]) if "intune" in found else []
    if devices:
        rows.extend(intune_rows(devices, register_keys, account_state))
        if register_keys is None:
            counts_note.append("Wiki page absent, so the Intune<->register comparison ran in "
                               "neither direction.")
        if account_state is None:
            counts_note.append("Entra users dump absent, so PRIMARY_USER_DISABLED was not "
                               "evaluated -- the Intune export carries no account-state "
                               "column and no variant of it does.")

    # wiki rows go in AFTER Intune is known, so the register->Intune direction can run
    if wiki_entries:
        intune_keys = {norm(d.get("Device name", "")) for d in devices}
        w_rows, unlabelled = wiki_rows(wiki_entries, intune_keys)
        if not intune_keys:
            # Without the Intune side every register row would flag as missing. Suppress.
            for r in w_rows:
                if r["Flag"] == F_ON_REGISTER:
                    r["Flag"], r["FlagDetail"] = "", ""
            counts_note.append("Intune export absent, so ON_REGISTER_NOT_IN_INTUNE was "
                               "suppressed rather than flagging the whole register.")
        rows.extend(w_rows)

    # ------------------------------------------------------------------ vendors
    if "vendors" in found:
        payloads = [load_json(p) for p in found["vendors"]]
        v_rows, merged, claimed, owner_present = vendor_rows(payloads, a.as_of)
        rows.extend(v_rows)
        if claimed and len(merged) < claimed:
            counts_note.append("VENDOR PAGINATION SHORTFALL: %d vendor records read, but "
                               "pagination.totalCount says %d. %d vendors were NOT reviewed "
                               "-- fetch the remaining page(s) and rerun."
                               % (len(merged), claimed, claimed - len(merged)))
        if not owner_present:
            counts_note.append("No security-owner field is present on any vendor record in "
                               "this dump, so VENDOR_NO_OWNER was NOT evaluated -- not "
                               "'every vendor has an owner'. The list endpoint does not "
                               "return one; Drata_getVendor per vendor does.")

    # ------------------------------------------------------------------ scope
    if aws_snap:
        rows.extend(scope_rows(aws_snap))

    # ------------------------------------------------------------------ write
    # utf-8-sig on the way out too, so Excel opens it as UTF-8 rather than mangling the
    # curly apostrophes and em dashes this workbook is full of.
    with open(a.out, "w", newline="", encoding=ENC) as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # ------------------------------------------------------------------ summary
    print("Rows by register")
    print("----------------")
    by_reg = collections.Counter(r["Register"] for r in rows)
    for reg in sorted(by_reg):
        flagged = sum(1 for r in rows if r["Register"] == reg and r["Flag"])
        print("  %-8s %5d rows   %5d flagged   %5d clean"
              % (reg, by_reg[reg], flagged, by_reg[reg] - flagged))
    print("  %-8s %5d" % ("TOTAL", len(rows)))
    print()

    print("Rows by flag")
    print("------------")
    by_flag = collections.Counter()
    for r in rows:
        for f in r["Flag"].split(";"):
            if f:
                by_flag[f] += 1
    if by_flag:
        for f, n in by_flag.most_common():
            print("  %-28s %5d" % (f, n))
    else:
        print("  none")
    clean_rows = sum(1 for r in rows if not r["Flag"])
    print()
    print("  %d of %d rows carry no flag." % (clean_rows, len(rows)))
    print("  A clean row is a RESULT, not an absence of one: the asset was read from a dump")
    print("  taken this cycle and tested against every check that applies to it, and it")
    print("  passed. Record the clean count in the evidence -- it is the coverage claim.")
    print()

    if unlabelled:
        print("  %d wiki row(s) carry no label at all. These are real assets Bitpool owns"
              % unlabelled)
        print("  that were never labelled -- they are in the workbook as `(unlabelled)`,")
        print("  counted, not dropped.")
        print()

    if unlisted:
        print("Wiki sections with a table that this script does NOT parse")
        print("----------------------------------------------------------")
        for heading, n in unlisted:
            print("  %-52s %d row(s)" % (heading, n))
        print("  Their assets are not in the workbook. Either the heading was renamed (fix")
        print("  WIKI_SECTIONS), or the section's first column is not a label so it needs a")
        print("  parse rule of its own. Do not assume it is out of scope.")
        print()

    for n in counts_note:
        print("  NOTE: %s" % n)
    if counts_note:
        print()

    print("written: %s  (%d rows, %d columns)" % (a.out, len(rows), len(COLUMNS)))
    print()
    print("The `Notes` column is empty by design. A human fills it, and a note is one of two")
    print("things: a DISPOSITION, which resolves the row this cycle, or a SCOPE CHANGE, which")
    print("also has to be carried into scripts/snapshot.py's allow-list and the wiki page it")
    print("concerns. A scope change left only in this file is lost when the cycle closes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
