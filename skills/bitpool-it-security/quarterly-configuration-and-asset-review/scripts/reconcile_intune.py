#!/usr/bin/env python3
"""Reconcile the Intune device export against account state and the wiki register.

Python 3 standard library only. Run through WSL:

    wsl -e bash -lc 'python3 reconcile_intune.py --devices intune.csv --users entra.csv'

Inputs
  --devices          Intune admin centre -> Devices -> All devices -> Export -> Export all data
  --users            Entra ID -> Users -> Download users, WITH the "Account enabled" column added
                     to the list view before exporting. Without that column the file cannot answer
                     the leaver question and this script will say so rather than guess.
  --register-labels  Optional. A text file of the device labels currently on the wiki register,
                     one per line, blank lines and '#' comments ignored. Enables the
                     in-register-not-in-Intune direction of the comparison.

Everything is printed to stdout as Markdown, ready to adapt into the Jira evidence comment.
"""

import argparse
import collections
import csv
import sys

# Intune writes these as sentinels meaning "no value", not as real timestamps.
NULL_DATES = {"0001-01-01 00:00:00.0000000", "9999-12-31 23:59:59.0000000"}

OS_CLASS = {"Windows": "Windows", "MacOS": "macOS", "iOS/iPadOS": "iOS"}


def read_csv(path):
    """Read a CSV, tolerating the UTF-8 BOM both exports carry."""
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def require_columns(rows, needed, label, path):
    if not rows:
        sys.exit("ERROR: %s (%s) has no data rows." % (label, path))
    missing = [c for c in needed if c not in rows[0]]
    if missing:
        sys.exit(
            "ERROR: %s (%s) is missing required column(s): %s\nColumns present: %s"
            % (label, path, ", ".join(missing), ", ".join(rows[0].keys()))
        )


def truthy(value):
    """accountEnabled is written True/False with a leading capital. Never compare raw."""
    return str(value).strip().lower() == "true"


def clean(value):
    v = (value or "").strip()
    return "" if v in NULL_DATES else v


def norm_label(name):
    """Key a device label for comparison. Report the original; compare on this.

    macOS names a device after its owner using a CURLY apostrophe (U+2019) -- "David's
    MacBook Pro" -- while the wiki register is typed with a straight one. Comparing the raw
    strings reports every MacBook as missing from the register AND unaccounted for in
    Intune simultaneously: six phantom findings from one character, and the shape of it
    reads exactly like a real register failure.
    """
    s = (name or "").strip()
    for curly in ("’", "‘", "ʼ", "´"):
        s = s.replace(curly, "'")
    return " ".join(s.split()).casefold()


def load_register_labels(path):
    labels = set()
    with open(path, encoding="utf-8-sig") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                labels.add(line)
    return labels


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--devices", required=True, help="Intune 'Export all data' CSV")
    ap.add_argument("--users", help="Entra 'Download users' CSV, with accountEnabled")
    ap.add_argument("--register-labels", help="Text file of labels on the wiki register")
    args = ap.parse_args()

    devices = read_csv(args.devices)
    require_columns(
        devices,
        ["Device name", "Serial number", "OS", "Primary user UPN",
         "Primary user display name", "Enrollment date", "Last check-in",
         "Compliance", "Ownership"],
        "device export", args.devices,
    )

    print("# Intune endpoint reconciliation\n")

    # ---------------------------------------------------------------- scope
    print("## Scope of the extract\n")
    print("%d devices in the export.\n" % len(devices))
    by_os = collections.Counter(OS_CLASS.get(r["OS"], r["OS"] or "unknown") for r in devices)
    print("| Class | Count |")
    print("|---|---|")
    for k in sorted(by_os):
        print("| %s | %d |" % (k, by_os[k]))
    print()
    for col in ("Ownership", "Compliance", "Managed by", "Device state"):
        if col in devices[0]:
            counts = collections.Counter(clean(r[col]) or "(blank)" for r in devices)
            print("- **%s** — %s" % (col, ", ".join(
                "%s: %d" % (k, v) for k, v in sorted(counts.items()))))
    print()

    # ---------------------------------------------- check 1: primary user present
    print("## Check 1 — every enrolled device has a primary user\n")
    no_user = [r for r in devices if not clean(r["Primary user UPN"])]
    if no_user:
        print("**%d of %d devices have NO primary user — each has no recorded owner:**\n"
              % (len(no_user), len(devices)))
        for r in no_user:
            print("- `%s` (%s, serial `%s`)"
                  % (r["Device name"], r["OS"], r["Serial number"]))
    else:
        print("Populated on **%d of %d**. No device is without a recorded owner."
              % (len(devices), len(devices)))
    print()

    # ------------------------------------------- check 2: resolve account state
    print("## Check 2 — every primary user resolved against account state\n")
    holders = {}
    for r in devices:
        upn = clean(r["Primary user UPN"]).lower()
        if upn:
            holders.setdefault(upn, clean(r["Primary user display name"]))

    if not args.users:
        print("**NOT RUN — no `--users` export supplied.**\n")
        print("This check cannot be answered from the device export: it carries no account-state")
        print("column and no variant of it does. Supply an Entra users export that includes")
        print("`accountEnabled`, or resolve the %d distinct primary users below against Drata"
              % len(holders))
        print("Personnel.\n")
        for upn in sorted(holders):
            print("- %s — %s" % (upn, holders[upn]))
    else:
        users = read_csv(args.users)
        require_columns(users, ["userPrincipalName"], "users export", args.users)
        if "accountEnabled" not in users[0]:
            print("**CANNOT ANSWER — the users export has no `accountEnabled` column.**\n")
            print("Entra's *Download users* exports only the columns visible in the Users list")
            print("view. Add the **Account enabled** column to that view, re-export, and run again.")
            print("Columns found: %s\n" % ", ".join(users[0].keys()))
            print("Leavers remain in the directory as disabled accounts, so presence in this file")
            print("does not mean the account is active. Do not treat this file as an answer.")
        else:
            state = {}
            for r in users:
                state[clean(r["userPrincipalName"]).lower()] = truthy(r.get("accountEnabled"))
            enabled_n = sum(1 for v in state.values() if v)
            print("Directory: %d objects, %d enabled, %d disabled.\n"
                  % (len(state), enabled_n, len(state) - enabled_n))
            print("| Primary user | Name | Devices | accountEnabled |")
            print("|---|---|---|---|")
            problems = []
            for upn in sorted(holders):
                owned = [r["Device name"] for r in devices
                         if clean(r["Primary user UPN"]).lower() == upn]
                if upn not in state:
                    verdict = "**NOT IN DIRECTORY**"
                    problems.append((upn, verdict))
                elif not state[upn]:
                    verdict = "**DISABLED**"
                    problems.append((upn, verdict))
                else:
                    verdict = "True"
                print("| %s | %s | %s | %s |"
                      % (upn, holders[upn], ", ".join("`%s`" % d for d in owned), verdict))
            print()
            if problems:
                print("**%d finding(s): endpoints belonging to accounts that are disabled or absent.**"
                      % len(problems))
            else:
                print("**No findings — all %d primary users hold an enabled account.** "
                      "Confirm any service accounts among them are declared as such."
                      % len(holders))
    print()

    # -------------------------------------- check 3: register, both directions
    print("## Check 3 — reconcile against the wiki register\n")
    intune_labels = {r["Device name"] for r in devices}
    if not args.register_labels:
        print("**Register side not supplied** (`--register-labels`), so only one direction was")
        print("checked. Supply the register's labels to catch devices on the register with no")
        print("Intune record — that is the only way an unenrolled device is ever found.\n")
        print("Devices in Intune (%d), to compare by hand:\n" % len(intune_labels))
        for name in sorted(intune_labels):
            print("- `%s`" % name)
    else:
        reg = load_register_labels(args.register_labels)
        i_by_key = {norm_label(n): n for n in intune_labels}
        r_by_key = {norm_label(n): n for n in reg}
        only_intune = sorted(i_by_key[k] for k in set(i_by_key) - set(r_by_key))
        only_reg = sorted(r_by_key[k] for k in set(r_by_key) - set(i_by_key))
        matched = set(i_by_key) & set(r_by_key)
        print("Intune: %d. Register: %d. Matched: %d.\n"
              % (len(intune_labels), len(reg), len(matched)))

        cosmetic = sorted((r_by_key[k], i_by_key[k]) for k in matched
                          if r_by_key[k] != i_by_key[k])
        if cosmetic:
            print("Matched across a cosmetic difference — same device, different spelling.")
            print("**Not findings.**\n")
            for reg_name, intune_name in cosmetic:
                print("- register `%s` = Intune `%s`" % (reg_name, intune_name))
            print()

        print("### In Intune, not on the register — add these (Intune wins on existence)\n")
        if only_intune:
            for name in only_intune:
                r = next(d for d in devices if d["Device name"] == name)
                print("- `%s` — %s, serial `%s`, primary user %s, enrolled %s"
                      % (name, r.get("Model", "?"), r["Serial number"],
                         clean(r["Primary user display name"]) or "(none)",
                         clean(r["Enrollment date"])[:10]))
        else:
            print("None.")
        print("\n### On the register, not in Intune — confirm, do NOT delete\n")
        if only_reg:
            print("A row with no Intune record may be a device that was never enrolled, or one")
            print("retired with no evidence of disposal. Mark and confirm each.\n")
            for name in only_reg:
                print("- `%s`" % name)
        else:
            print("None.")
    print()

    # ----------------------------------------- check 4: duplicate holders
    print("## Check 4 — one person holding two endpoints\n")
    print("The only signal that a replaced device is still enrolled. A replaced laptop reports")
    print("compliant, encrypted and checking in, identical to one in active use.\n")
    computers = [r for r in devices if OS_CLASS.get(r["OS"]) in ("Windows", "macOS")]
    by_holder = collections.defaultdict(list)
    for r in computers:
        upn = clean(r["Primary user UPN"]).lower()
        if upn:
            by_holder[upn].append(r)
    dupes = {u: rs for u, rs in by_holder.items() if len(rs) > 1}
    if not dupes:
        print("**No findings** — no primary user holds more than one laptop or desktop.")
    else:
        for upn, rs in sorted(dupes.items()):
            rs.sort(key=lambda r: clean(r["Enrollment date"]))
            print("- **%s** (%s) holds %d:" % (clean(rs[0]["Primary user display name"]),
                                               upn, len(rs)))
            for r in rs:
                print("    - `%s` (%s) enrolled %s, last check-in %s, %s"
                      % (r["Device name"], OS_CLASS.get(r["OS"], r["OS"]),
                         clean(r["Enrollment date"])[:10],
                         clean(r["Last check-in"])[:10], clean(r["Compliance"])))
            # A replacement is same-platform. A Windows laptop and a MacBook held by one
            # person is a two-device issue, not a supersession, and must not be reported
            # as one -- that would send someone to wipe a machine still in use.
            per_class = collections.defaultdict(list)
            for r in rs:
                per_class[OS_CLASS.get(r["OS"], r["OS"])].append(r)
            flagged = False
            for cls, group in sorted(per_class.items()):
                if len(group) > 1:
                    flagged = True
                    # Name the pair; do NOT assert which way round it goes. Enrolment date
                    # is not a supersession signal -- a device that is re-enrolled gets a
                    # fresh enrolment date, so the OLDER machine can carry the LATER one.
                    # Observed 2026-09-17: LAPTOP-D3321J8L (an HP ENVY bought 05/2024, being
                    # retired) re-enrolled 2026-09-03, against LAPTOP-PW0NHYX4 (its 2026
                    # replacement) enrolled 2026-07-06. Ordering on enrolment names the
                    # replacement as the machine to wipe. Purchase date settles it, and
                    # purchase date lives on the wiki register, not in Intune.
                    print("    - Same-platform pair (%s): `%s` and `%s`. One is likely "
                          "`Replaced — pending retirement`."
                          % (cls, group[0]["Device name"], group[-1]["Device name"]))
                    print("      **Which one is decided by the register's purchase dates, "
                          "not by enrolment date** — a re-enrolled device carries a newer "
                          "enrolment date than its own replacement. Confirm against the "
                          "wiki register before wiping anything.")
            if not flagged:
                print("    - One device per platform, so this is **not** a replacement overlap. "
                      "Confirm both are genuinely issued to this holder.")
    print()

    print("---\n")
    print("Limits of this extract: it lists only Intune-managed records, so a device that is")
    print("Entra-joined but never enrolled does not appear here at all. That case is caught only")
    print("from the register side — see check 3.")


if __name__ == "__main__":
    main()
