# Bitpool Documentation Index

What supporting documentation exists, by control domain. Use it to answer *"is this control
documented?"* without querying the wiki.

> **Warning**
> **This is a point-in-time snapshot, taken 2026-08-21.** A live wiki search would notice a page
> added yesterday; this file will not. So:
>
> - A page **listed here** — safe to cite as existing documentation.
> - A domain **not listed here** — report it as *"no documentation found in the index (snapshot
>   2026-08-21)"*, **never** as *"no documentation exists"*. The difference matters: the first is a
>   lookup result, the second is a compliance claim you cannot support from a snapshot.
> - If the user says a page exists that isn't here, believe them and say the index needs refreshing.
>
> Refresh it by re-listing the wiki's policy and procedure pages and updating this file. Doing that
> is a deliberate maintenance task, not something to attempt mid-run.

All paths are relative to `https://private-wiki.bitpool.com`.

## ISMS policies

The controlled policy set. These are the documents an auditor asks for by name.

| Domain | Pages |
|---|---|
| Access control | `/isms/system-access-control-policy`, `/isms/password-policy`, `/isms/acceptable-use-policy`, `/isms/separation-of-duties-policy`, `/isms/network-security-policy`, `/isms/information-security-policy` |
| Incident response | `/isms/incident-response-plan` |
| Logging and monitoring | `/isms/logging-and-monitoring-policy` — includes the **Clock Synchronisation** section, which is the documented time-source standard (A.8.17) |
| Vulnerability management | `/isms/vulnerability-management-policy`, `/isms/responsible-disclosure-policy` |
| Change management | `/isms/change-management-policy`, `/isms/software-development-life-cycle-policy`, `/isms/risk-assessment-policy`, `/isms/isms-exemption-policy`, `/isms/information-security-management-system-plan-iso-iec-27001-2022` |
| HR / personnel | `/isms/employee-handbook`, `/isms/contractor-handbook` |
| Business continuity | `/isms/business-continuity-plan`, `/isms/disaster-recovery-plan`, `/isms/backup-policy` |
| Data protection | `/isms/data-protection-policy`, `/isms/data-classification-policy`, `/isms/data-retention-policy`, `/isms/gdpr-privacy-policy` |
| Supplier / vendor | `/isms/vendor-management-policy` |
| Physical / device security | `/isms/physical-security-policy`, `/isms/byod-policy`, `/isms/personal-apps-and-sims-on-company-owned-devices-policy` |
| Asset management | `/isms/asset-management-policy` |
| Cryptography | `/isms/encryption-policy` |

ISMS meta: `/isms/_meta/commit-convention`, `/isms/_meta/policy-change-banner`.

## HR controlled policies — People, Culture & Talent

A **second controlled-document set**, owned by People, Culture & Talent rather than Information
Security, and held only as `.docx` in a synced SharePoint library — not in any git repo, and not on
the wiki. It is nonetheless controlled documented information: every document carries a Document
Version Control table with a named approver, and every one is published in Drata's Policy Centre.

Location: `%USERPROFILE%\Bitpool Pty Ltd\GRC - Bitpool - Documents\General\Company Policies\HR\HR - Prod`

Read one by extracting the `.docx`. **Never conclude a domain is undocumented because it is absent
from the ISMS repo** — a control whose subject touches conduct, disciplinary process, employment
terms, harassment, privacy or whistleblowing is usually covered here rather than there.

> **If the path does not resolve, the library is not synced on this machine.** Ask the user to sync
> it; never report the documents as non-existent. Same failure mode, same answer, as the logging
> library in `/log-skill-divergence`.

**The table below is a snapshot taken 2026-08-28** and carries the same staleness caveat as the ISMS
table above. `Drata_listPolicies` is the authoritative live index of this set and the two reconcile
— resolve the current list from there rather than trusting this one.

| Domain | Documents |
|---|---|
| Whistleblowing / speak-up | `Whistleblower Policy`, `Whistleblower Procedure` |
| Conduct and ethics | `Code of Conduct Policy`, `Conflict of Interest Policy`, `Anti-Bribery and Corruption Policy` |
| Workplace conduct | `Procedure for Handling Harassment, Discrimination and Bullying`, `Employee Relations Policy`, `Drugs and Alcohol Policy` |
| Safety | `Safety Incident Reporting Procedure`, `Workplace Health and Safety Policy`, `Family & Domestic Violence Policy` |
| Working arrangements | `Working From Home Policy`, `Flexible Working Arrangements Policy`, `Right-to-Disconnect Policy`, `Leave Policy` |
| Corporate responsibility | `Modern Slavery Policy`, `Modern Slavery Statement`, `Environmental, Social and Governace Policy`, `Corporate-Social Responsibility Policy`, `Diversity, Equity and Inclusion Policy`, `Indigenous Rights Statement`, `Universal Decleration of Human Rights Statement` |
| Other | `Social Media Policy`, `Travel and General Expenses Policy`, `Privacy Policy`, `Functions and Social Events Policy` |

**Two filenames carry typos at source** — `Governace` and `Decleration`. They are reproduced verbatim
because that is what a filesystem search has to match; do not "correct" them when searching.

## Operational procedures and runbooks

The "how it's actually done" layer. A control can have a policy and no procedure, or the reverse —
say which is missing rather than collapsing them into one answer.

| Topic | Pages |
|---|---|
| IT runbooks | `/it/runbooks/runbooks`, `/it/runbooks/troubleshoot-onedrive` |
| Onboarding / device setup | `/it/onboarding/device-setup-checklist`, `/it/endpoints/endpoints` |
| Identity, credentials, tokens | `/it/identity-and-access/password-reset-creation`, `/it/identity-and-access/api-secrets-token-refresh`, `/it/identity-and-access/admin-overview` (1Password admin), `/it/microsoft-365/entra-groups-inventory` |
| Security operations | `/it/security/sentinel`, `/it/security/security`, `/it/security/cyber-security-overview`, `/it/automation/get-mailbox-rules` |
| Application control | `/it/security/generate-policy-audit-mode-app` (WDAC audit-mode policy) |
| Code signing | `/it/automation/bitpool-code-signing` |
| Data platform | `/it/data-platform/finance-data-warehouse-iam` |
| Incident response | `/security/incident-response/incident-response` |
| Procedures index | `/security/procedures/procedures`, `/security/notes/procedures` |
| OT security | `/security/ot-security/ot-security` |
| Compliance | `/security/compliance/rto-rpo-objectives`, `/security/compliance/drata-controls-register` |
| Questionnaires | `/security/questionnaires/security-operations-and-incident-response` |

## Domains with no documentation in this snapshot

Worth flagging as candidate gaps when a control lands in one of them — subject to the staleness
caveat above, and **check the HR controlled policies table as well as the ISMS one before concluding
a domain is undocumented.** Conduct, disciplinary, privacy and speak-up topics are documented in that
set, not in the ISMS repo, and a control whose subject touches personnel behaviour will usually be
covered there:

> **Corrected 2026-08-24.** *Clock synchronisation / time source* was listed here and was wrong: it is documented in the Logging and Monitoring Policy, § Clock Synchronisation — a policy already listed in the table above. **Before trusting a bullet in this list, check whether a policy listed above already covers the domain.** A topic-level heading is not the only place a requirement gets documented, and a section inside an existing policy counts. Reading this list without that check is how a met control gets reported as an undocumented gap.

- Secure development training / awareness training records
- Supplier security review records (the policy exists; per-supplier reviews aren't documented here)
- Cryptographic key management procedure (the Encryption Policy exists; no key-handling runbook)
- Capacity management
