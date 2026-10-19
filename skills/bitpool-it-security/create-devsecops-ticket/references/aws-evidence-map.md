# AWS Evidence Map

Shared reference for the compliance skills that look at live infrastructure — chiefly
**`/drive-iso27001`** (deep-diving a control, sizing a change) and **`/drata-control-insights`**
(single-control snapshots). It is duplicated on purpose, byte-identical, in `aws-query`,
`create-devsecops-ticket`, `drata-control-insights` and `drive-iso27001`: **edit every copy**, per
the shared-reference rule in `/update-hermes-skill`'s house rules.

This file answers **"what should I ask AWS for this control?"** only. It deliberately carries **no CLI
syntax, no profile names, and no account IDs** — that is the `/aws-query` skill's job, and duplicating
it here is how the two drift apart. The division is:

| Question | Skill |
|---|---|
| Is the environment signed in and is it the *right* identity? | `/aws-context` (once per session) |
| How do I phrase the call, loop every account in the Organization, avoid JMESPath traps? | `/aws-query` |
| Which call actually evidences *this* ISO 27001 control? | **this file** |

**Invoke those skills — never inline their content.** If you find yourself about to write an
`aws.exe` command with a `--profile` flag into a compliance skill, stop and call `/aws-query` instead.

---

## 1 — Preflight, every time

1. **Session check.** If `aws sts get-caller-identity` hasn't succeeded yet this session, run
   `/aws-context` first. Do not re-check before every subsequent call.
2. **No session and the user doesn't want to sign in?** Carry on without AWS. Every AWS finding below
   is an *enrichment* — a control review must still complete from Drata + Jira + GitBook alone. Say
   "infrastructure not checked this session" rather than silently omitting the row.
3. **Mid-session expiry is normal.** The SSO session is 12h; a query that worked earlier can fail
   later. That's an `/aws-context` problem, not a query problem.

---

## 2 — Is this control even infrastructure-relevant?

Run the map only when at least one of these is true. Otherwise skip AWS entirely — fishing for
resources on an HR or physical-security control burns time and produces noise.

**Signals in the Drata control / CSIP description:** encryption, key management, backup, restore,
retention, deletion, logging, audit trail, monitoring, alerting, network, firewall, segmentation,
public exposure, IAM, MFA, privileged access, access keys, vulnerability, patching, malware,
baseline, hardening, configuration, asset inventory, secrets, availability, DR, capacity,
clock/time sync, cloud, AWS, production environment.

**ISO 27001:2022 Annex A families that are usually infra-shaped:** A.5.9, A.5.15–5.18, A.5.19–5.22
(cloud-side supplier exposure), A.5.23, A.5.29–5.30, A.7.10, and most of **A.8** — especially
A.8.1–8.3, A.8.5, A.8.7–8.13, A.8.15–8.17, A.8.20–8.24, A.8.32.

**Highest value case — prioritise it.** A control where Drata's `isMonitored` is `false` (no automated
test) *and* the domain is infra-shaped is exactly where a live query earns its keep: Drata has no
opinion on the current state, so without a query the only input is someone's recollection.
`hasEvidence: false` on an infra control is the second-best case.

**Not verifiable from AWS — don't try:** people/HR controls (A.6.x), physical and environmental
controls (A.7.1–7.9, A.7.11–7.14), policy existence and approval, awareness training, supplier
*contracts* (as opposed to their cloud access), management review, internal audit. Say "not an AWS
question" and move on.

---

## 3 — The map

Each row: what to ask, which read-only API surface answers it, and what a healthy answer looks like.
Ask `/aws-query` to construct the actual calls. `service operation` below is the AWS CLI
`<service> <operation>` pair, not a full command.

### Logging and audit trail — A.8.15

| Ask | Read-only calls | Reads as in-place when |
|---|---|---|
| Is CloudTrail on, org-wide, and tamper-evident? | `cloudtrail describe-trails`, `cloudtrail get-trail-status`, `cloudtrail get-event-selectors` | A multi-region trail exists per account (or one org trail), `IsLogging: true`, `LogFileValidationEnabled: true` |
| Do log groups retain long enough? | `logs describe-log-groups` | `retentionInDays` is set — **`null` means never expires**, which is a real finding either way (cost *and* retention-policy conflict) |

### Monitoring, alerting and threat detection — A.8.16

| Ask | Read-only calls | Reads as in-place when |
|---|---|---|
| Is GuardDuty enabled everywhere? | `guardduty list-detectors`, `guardduty get-detector` | A detector exists and is enabled in every account/region in scope |
| Is Security Hub / Config aggregating? | `securityhub describe-hub`, `securityhub get-enabled-standards`, `configservice describe-configuration-recorders`, `configservice describe-configuration-recorder-status` | Recorder exists **and** is recording; standards enabled |
| Are there alarms on the things that matter? | `cloudwatch describe-alarms` | Alarms exist in `OK`/`ALARM` (not `INSUFFICIENT_DATA` across the board — that usually means nothing is reporting) |

### Malware protection — A.8.7

| Ask | Read-only calls | Reads as in-place when |
|---|---|---|
| Is runtime/malware protection on? | `guardduty get-detector` (feature list) | Malware Protection features enabled where applicable |

### Encryption at rest — A.8.24

| Ask | Read-only calls | Reads as in-place when |
|---|---|---|
| Are buckets encrypted by default? | `s3api get-bucket-encryption` per bucket | Every bucket returns a rule; a `ServerSideEncryptionConfigurationNotFoundError` is the finding |
| Is EBS encrypted by default? | `ec2 get-ebs-encryption-by-default`, `ec2 describe-volumes` | Account default is `true` **and** no unencrypted volumes linger from before it was set |
| Are databases encrypted? | `rds describe-db-instances`, `rds describe-db-clusters` | `StorageEncrypted: true` |
| Are keys managed and rotating? | `kms list-keys`, `kms get-key-rotation-status` | Customer-managed keys have rotation enabled |

### Secrets and credentials — A.5.17, A.8.24

| Ask | Read-only calls | Reads as in-place when |
|---|---|---|
| Are secrets centralised and rotating? | `secretsmanager list-secrets`, `ssm describe-parameters` | Secrets exist in Secrets Manager with `RotationEnabled: true`; note stale `LastRotatedDate` |

> **By design you cannot read a secret's value** (`ViewOnlyAccess` blocks `GetSecretValue`). Metadata
> only. An access-denied on a value read is the control working, not a blocker to route around.

### Network security, exposure and segmentation — A.8.20, A.8.21, A.8.22, A.8.23

| Ask | Read-only calls | Reads as in-place when |
|---|---|---|
| What's reachable from the internet? | `ec2 describe-security-groups`, `ec2 describe-network-acls` | No `0.0.0.0/0` ingress on admin ports (22, 3389, 3306, 5432, 1433, 6379, 27017) |
| Are buckets public? | `s3api get-public-access-block`, `s3api get-bucket-policy-status` | Block-public-access all-true at account and bucket level; `IsPublic: false` |
| Is TLS enforced at the edge? | `elbv2 describe-listeners`, `elbv2 describe-load-balancers`, `cloudfront list-distributions` | HTTPS listeners with a current TLS policy; no viewer HTTP-allowed distributions |
| Is the network segmented, and is traffic observable? | `ec2 describe-vpcs`, `ec2 describe-subnets`, `ec2 describe-flow-logs`, `ec2 describe-vpc-peering-connections`, `ec2 describe-transit-gateways` | Non-default VPCs in use, flow logs enabled, peering/TGW attachments all intentional |

### Identity, access control and privileged access — A.5.15, A.5.16, A.5.18, A.8.2, A.8.3, A.8.5

| Ask | Read-only calls | Reads as in-place when |
|---|---|---|
| Is access via SSO rather than long-lived IAM users? | `iam list-users`, `iam list-access-keys`, `sso-admin list-instances`, `sso-admin list-permission-sets`, `identitystore list-users` | Few/no IAM users with active keys; access arrives through Identity Center |
| Are there stale access keys? | `iam list-access-keys` (check `CreateDate`), `iam get-access-key-last-used` | No active key older than the rotation policy; no key unused for months |
| Is MFA enforced? | `iam list-mfa-devices`, `iam get-account-summary` (`AccountMFAEnabled` for root) | Root has MFA; any remaining IAM users have MFA |
| Is anything over-privileged? | `iam list-policies --scope Local`, `iam list-attached-role-policies`, `iam list-roles` | No local policy granting `*:*`; admin reachable only through reviewed permission sets |
| Is the password policy set? | `iam get-account-password-policy` | A policy exists (a `NoSuchEntity` error *is* the finding) |

### Third-party / supplier access into our cloud — A.5.19–A.5.22

| Ask | Read-only calls | Reads as in-place when |
|---|---|---|
| Which external principals can get in? | `iam list-roles` (inspect `AssumeRolePolicyDocument` for foreign account IDs), `s3api get-bucket-policy`, `ram list-resources` | Every external trust maps to a known, reviewed vendor — an unrecognised account ID in a trust policy is a high-value finding for vendor-management controls |

### Backup, restore and continuity — A.8.13, A.5.29, A.5.30

| Ask | Read-only calls | Reads as in-place when |
|---|---|---|
| Are backups actually running? | `backup list-backup-plans`, `backup list-backup-vaults`, `backup list-backup-jobs`, `backup list-protected-resources` | Plans cover the real resources **and** recent jobs show `COMPLETED`, not just a plan on paper |
| Do databases retain backups? | `rds describe-db-instances` (`BackupRetentionPeriod`), `rds describe-db-snapshots` | Retention > 0 and matching the stated RPO |
| Is object data recoverable? | `s3api get-bucket-versioning`, `s3api get-bucket-replication`, `dlm get-lifecycle-policies` | Versioning enabled on data buckets; snapshot lifecycle policies present |

### Vulnerability and patch management — A.8.8

| Ask | Read-only calls | Reads as in-place when |
|---|---|---|
| Is scanning on, and what's outstanding? | `inspector2 batch-get-account-status`, `inspector2 list-coverage`, `inspector2 list-findings` | Inspector enabled with coverage over EC2/ECR/Lambda; findings triaged not accumulating |
| Are instances patched? | `ssm describe-instance-patch-states`, `ssm describe-instance-information` | Instances SSM-managed and reporting compliant patch states |
| Any end-of-life runtimes? | `lambda list-functions` (runtimes), `ec2 describe-instances` (AMI age), `rds describe-db-instances` (engine versions) | Nothing on a deprecated runtime/engine — **check current deprecation dates via the AWS Knowledge MCP, never from memory** |

### Secure configuration and baseline — A.8.9

| Ask | Read-only calls | Reads as in-place when |
|---|---|---|
| Is there a baseline, and does it hold? | `configservice describe-config-rules`, `configservice describe-compliance-by-config-rule`, `securityhub get-enabled-standards`, `securityhub get-findings` | Rules exist and compliance is measured, not just recorded |
| Is infrastructure deployed as code? | `cloudformation list-stacks`, `cloudformation list-stack-sets`, `cloudformation describe-stack-set` | Resources trace to stacks/StackSets rather than console-built one-offs |

### Asset inventory and ownership — A.5.9

| Ask | Read-only calls | Reads as in-place when |
|---|---|---|
| What do we actually run? | `resourcegroupstaggingapi get-resources`, `ec2 describe-instances`, `rds describe-db-instances`, `lambda list-functions`, `s3api list-buckets`, `eks list-clusters`, `ecs list-clusters` | Counts reconcile with whatever asset register the control claims |
| Is ownership recorded? | `resourcegroupstaggingapi get-resources` (tag coverage) | Owner/environment tags present — **tag coverage is the strongest AWS-side evidence for asset-ownership controls** |
| What's the account structure? | `organizations list-accounts`, `organizations describe-organization`, `organizations list-policies` | Account list matches the documented structure; SCPs where expected |

### Data retention and deletion — A.8.10, A.7.10

| Ask | Read-only calls | Reads as in-place when |
|---|---|---|
| Does data age out per policy? | `s3api get-bucket-lifecycle-configuration`, `logs describe-log-groups`, `rds describe-db-snapshots`, `ec2 describe-snapshots` | Lifecycle rules and retention settings match the stated retention policy |

### Change management — A.8.32

| Ask | Read-only calls | Reads as in-place when |
|---|---|---|
| Do changes go through a controlled path? | `cloudformation list-stacks` + `describe-stacks` (`LastUpdatedTime`), `cloudtrail lookup-events` (write events by principal) | Changes arrive via IaC/pipeline principals, not humans in the console |

### Clock synchronisation — A.8.17

Genuinely hard to prove with metadata-only calls. Best available: `ssm describe-instance-information`
plus SSM inventory if collected. If it isn't, **say it's not verifiable from AWS view-only access**
rather than implying a pass — this control is usually evidenced by configuration management instead.

---

## 4 — Budget the calls

Unbounded fan-out across every account in the Organization is the failure mode here. Hard limits:

- **`/drata-control-insights`** (single-control snapshot): **≤2 domains, ≤6 calls.** Prefer one account
  unless the control is inherently org-wide (CloudTrail, Organizations, Identity Center, SCPs).
- **`/drive-iso27001`** (per deep-dived control): **≤12 calls**, and only for controls the user
  approved for AWS enrichment.
- **Account order when you must choose:** production first, then the account that owns the resource
  class in question, then org-wide accounts for org-wide controls. Only loop every account when the
  control is genuinely about every account — and when you do, use the single loop pattern from
  `/aws-query`, not one command per account.
- **Large result sets:** save to a temp file and parse, per `/aws-query` — never read a full JSON dump
  into context.
- **One failure, one diagnosis.** `/aws-query` splits failures into session vs query-construction —
  classify before retrying, and never retry the same failing call more than once.

---

## 5 — What an AWS finding is, and isn't

**It is a current-state observation. It is not Drata evidence and it is not a control assessment.**

- Never present a CLI result as satisfying a control in Drata. Drata stays **read-only** — a human
  attaches evidence in the Drata UI. The query tells them *what* to attach and *whether it's worth
  attaching yet*.
- Report the observation and its date, then the implication. In chat, a worklog or a dated comment,
  "GuardDuty enabled in `<n>` of `<m>` accounts (missing in `<account>`), observed `<date>` —
  control claims org-wide coverage" is useful. "GuardDuty control satisfied" is not, and isn't yours
  to say.
- **Distinguish three outcomes and label them plainly:** *in place* (queried, healthy), *gap*
  (queried, not healthy — the valuable one), and *not checked* (no session, out of budget, or not an
  AWS question). Never let the third quietly read as the first.
- **Don't over-collect, and mind where the observation lands.** Counts, account names and resource
  identifiers are fine in chat, a worklog or a dated comment; don't paste large inventories into the
  state files — reference the query and the count, per State File Schemas (see the
  `/drive-iso27001` skill). A CSIP or IRT summary or description, or a Drata field, is durable text
  under `/bitpool-writing-standard`: it describes the population and names the query, and the count
  goes in a dated comment.

---

## 6 — Risk, cost and effort advisory

When the question is *"should we do this, and what will it take?"* rather than *"where are we?"*,
answer in this shape. Ground every number in something you actually queried; mark anything else as an
assumption.

**Effort — T-shirt size from real counts, not vibes:**

| Size | Looks like |
|---|---|
| **S** | 1 account, ≤2 resources, reversible, no data-plane impact |
| **M** | 2–3 accounts, ≤15 resources, or a config change needing a verification pass |
| **L** | All accounts, >15 resources, or any change to the production data plane / identity path |

**Blast radius:** name the accounts affected and say explicitly whether production is one of them. A
production data-plane change means a change window and a `/change-request` ticket — say so.

**Risk — both directions, or it's not advice:** the risk of making the change (what breaks, what's
hard to reverse, what needs a rollback plan) *and* the risk of leaving it (the exposure the control
exists to prevent, plus audit consequence if the control stays unevidenced).

**Cost — qualitative by default:**
- Default to a **directional** answer grounded in counts and resource classes: "adds a flow-log
  destination per VPC across 3 accounts — small ongoing storage cost, no compute change."
- Attempt real dollars **only when the user explicitly asks for them**. Cost Explorer
  (`ce get-cost-and-usage`, `ce get-cost-forecast`) is management-account-scoped and may be denied
  under `ViewOnlyAccess`. If it's denied, **say it was denied** — do not substitute an invented
  figure or a list-price estimate dressed up as an observation.
- Prefer honest bounds ("under $50/mo at this volume, unverified") over false precision.

**Then commit to a recommendation.** One preferred course, one sentence of why, and the cheapest next
step that de-risks it. A survey of options is not advice. If the honest answer is "don't do this
yet," say that.
