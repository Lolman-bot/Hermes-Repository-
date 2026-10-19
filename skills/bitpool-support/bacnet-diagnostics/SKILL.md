---
name: bacnet-diagnostics
description: "Use when diagnosing BACnet alerts or MS/TP and IP faults."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, bacnet, bms, building-automation, diagnostics, mstp, hvac]
    category: bitpool
    related_skills: [bitpool-hvac-schematics]
---

# BACnet Diagnostics — Bitpool Reference

A structured reference for diagnosing and remediating BACnet network issues on building automation (BAS) and operational technology (OT) networks. Covers 32 commonly-seen diagnostic alerts plus the formal ASHRAE 135-2008 protocol errata.

The reference ships with this skill in `references/`. Nothing is fetched at run time.

## When to Use

- The user names a BACnet diagnostic alert: Lost Tokens, Checksum Errors, Duplicate BBMD, Excessive COV/Read/Write Rate, Excessive Token Hold Time, Slow Response Time, Detected Circular Networks, Duplicate Device Address, Gap in MSTP Addressing, Unreachable Devices, Router Rejecting Messages, etc.
- They are troubleshooting MS/TP or BACnet/IP issues, or describe symptoms like broadcast storms, duplicate instances, controllers dropping off, router backpressure, or excessive traffic.
- They mention BBMDs, MS/TP token passing, `max_master`, `max_info_frame`, Who-Is/I-Am, WHO-HAS, COV or TrendLogs, or ask "what does this BACnet error mean".
- They ask about ASHRAE 135-2008 errata, a BACnet clause number, or ASN.1 productions.
- Trigger on partial matches — don't answer from memory, the reference has specific vendor-confirmed remediation steps worth consulting every time.

Don't use for:
- Drawing a plant or HVAC graphic: use `/bitpool-hvac-schematics`.
- Building Bitpool Cloud dashboards or reports on top of BACnet data: use `/bitpool-dashboard-builder` or `/bitpool-report-builder`.

## Procedure

1. **Identify the diagnostic or symptom** in the user's question. A named alert goes straight to its family (see Reference files); a described symptom ("controllers keep dropping off") maps to one or more. Done when you can name the diagnostic(s) and the file that holds each.
2. **Read the entry** from `references/` with `read_file`, naming the diagnostic and the page. Never answer from memory — the entries carry vendor-confirmed root causes and steps. Read the whole file you reach for; skimming for the line you expect is how a threshold or a flag gets missed. Done when every diagnostic in the answer traces to a file read this run.
3. **Check related diagnostics** (rule 3 below) and read their entries too when they plausibly share the cause. Done when the cross-references are named.
4. **Answer with both halves**: *What Happened?* and *How to Fix It*. A diagnosis without a fix, or a fix without the mechanism, is half an answer. Structure: one-line plain-English explanation → likely causes (tight bullets) → remediation steps → related diagnostics to check. Done when all four parts are present.

## Errata vs diagnostics

They are different kinds of thing. **Diagnostics** are runtime alerts about a real network. **Errata** are errors in the published standard itself. Reach for errata when the question names a specific BACnet clause number (e.g. "Clause 12.11.28", "Annex C"), asks about ASN.1 productions, `BACnetPropertyIdentifier`, `BACnetPropertyStates` or other formal protocol structures, or is interpreting unexpected device behaviour that may stem from a known specification ambiguity. `references/bacnet-ashrae-135-2008-errata.md` is 27 KB: use `search_files` for the clause number, then `read_file` with an offset.

## Load-bearing rules

Restated here because they shape every answer.

1. **Don't answer from memory.** Trigger on partial matches and open the reference file — the thresholds (one COV per device per five minutes, token hold >500ms, round trip >2s against an 85ms target, >32 MS/TP masters) are specific and worth getting right.
2. **Always give both halves** — the mechanism and the remediation.
3. **Cross-reference related diagnostics.** Lost Tokens, Checksum Errors and Excessive MS/TP Round Trip Token Time commonly share one wiring fault; discovery floods and unreachable devices feed each other. Say so.
4. **A high rate is not automatically a fault.** COV, read and write rate alerts are advisory — the question is whether the rate is deliberate.
5. **Keep it concrete.** BAS engineers want the wiring, the setting, or the device that needs attention — not protocol theory.

## Pitfalls

- **Quoting a threshold from memory.** The numbers in rule 1 are the ones most often misremembered; read them from the file every time.
- **Treating one physical-layer alert in isolation.** Lost Tokens, Checksum Errors and slow round trips are usually one cabling or termination fault seen three ways.
- **Calling an advisory rate alert a fault.** A deliberate high COV or read rate may be fine; ask or explain rather than prescribing a fix.
- **Mixing errata into a runtime diagnosis** (or vice versa) without saying which kind of thing it is.

## Verification

- Every diagnostic named in the answer was read from a `references/` file this run.
- The answer has the explanation, likely causes, remediation steps and related diagnostics.
- Any threshold quoted matches the reference text exactly.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/bacnet-addressing-and-topology.md` | BACnet diagnostics caused by address collisions, network numbering, BBMD overlap, routing loops and MS/TP segment sizing. |
| `references/bacnet-ashrae-135-2008-errata.md` | The 85 formal protocol-level errata from ANSI/ASHRAE Standard 135-2008 — misspellings, enumeration errors, algorithmic corrections and conformance fixes in the BACnet standard itself, distinct from runtime network diagnostics. |
| `references/bacnet-discovery-and-reachability.md` | BACnet diagnostics about devices that cannot be found, respond slowly, or are being searched for too aggressively — Who-Is/I-Am, WHO-HAS, and unreachable devices. |
| `references/bacnet-physical-layer.md` | The three BACnet diagnostics that point at cabling, terminations or hardware faults: Checksum Errors, Lost Tokens, and Excessive MS/TP Round Trip Token Time. |
| `references/bacnet-traffic-and-rates.md` | BACnet diagnostics driven by traffic volume — retries, router backpressure, broadcast floods, and excessive COV, read, write and token-hold rates. |
| `references/bacnet-trendlogs-and-error-classes.md` | TrendLog buffer diagnostics, plus the four error-message classifications: interoperability, operational, programming and unknown. |

Diagnostic entries, thresholds, remediation steps and errata are edited in the matching file in `references/`.
