# AWS asset tag coverage — the register check

AWS resource **tags are the asset register**. This file is the check that they are actually applied,
and the exclusion rule that keeps ephemeral Kubernetes objects out of it.

Counts quoted are from 2026-08-27 and will drift — re-read them, never restate them from here.

Assumes a live SSO session. If `aws sts get-caller-identity` has not been verified this session, run
`/aws-context` first.

---

## 1 — The exclusion rule

The rule is **by resource type first**, not by tag. This is the correction that matters: the volume
in Bitpool's estate is Kubernetes **pods**, not EC2 nodes.

| Excluded | Mechanism | Why |
|---|---|---|
| `eks:pod` | ARN resource type | Individual Kubernetes pods. **96% of all tagged resources in aws-prod.** The most ephemeral object in the estate; represented by its cluster |
| `ec2:fleet`, `ec2:spot-instances-request` | ARN resource type | Karpenter provisioning artefacts, not assets |
| EC2 instances carrying `aws:eks:cluster-name` | Tag presence | EKS node capacity. The tag is **AWS-managed** — it cannot be edited or omitted, which makes it a reliable discriminator |
| Volumes and snapshots carrying `CSIVolumeName` or `CSIVolumeSnapshotName` | Tag presence | Kubernetes persistent-volume churn |

**The cluster is the asset; its components are not.** An EKS cluster belongs in the register. Its
pods, nodes, provisioning requests and CSI volumes are runtime capacity of that cluster and do not.
A row with a lifetime measured in hours supports no accountability and dilutes the rows that do.

### Why the rule is not "exclude by tag alone"

Two reasons worth knowing:

1. **Pods dominate and are excluded by type**, so a tag-only rule would miss the bulk entirely.
2. **AWS Config cannot filter by tag at all** — its three recording strategies
   (`ALL_SUPPORTED_RESOURCE_TYPES`, `INCLUSION_BY_RESOURCE_TYPES`, `EXCLUSION_BY_RESOURCE_TYPES`)
   are all by resource type, with a per-type Continuous/Daily frequency. So Config cannot separate
   durable EC2 instances from EKS nodes. Config is the right tool for drift detection and the
   `required-tags` rule; it is not the register.

---

## 2 — Tag key convention

**PascalCase**, no separators. This is what the estate already uses, and it is the standard for both
AWS and Azure.

Established empirically 2026-08-27: of the Bitpool-authored tag keys in use, the governance set is
uniformly PascalCase — `Owner`, `OwnerGroup`, `OwnerContact`, `Criticality`, `Environment`,
`Purpose`, `WorkloadType`, `IsPersonalData`, `HasPublicAccess`, `DataType`, `Department`, `Tier`,
`ManagedBy`, `BackupPolicy`, `DecommissionDate`, `NeedsReview`.

There is **no camel-snake convention** in the estate and none documented on the Bitpool Private Wiki
(searched 2026-08-27, connection live, no tagging-convention page exists). Keys containing
underscores are application configuration rather than governance tags, and one of them carries a
typo and a trailing space — a reminder that free-text tag keys need an enforced allowed set.

Lowercase keys (`app`, `chart`, `release`, `heritage`, `component`) are Kubernetes and Helm generated.
Slash-bearing keys (`app.kubernetes.io/*`, `eks.amazonaws.com/*`, `stackgres.io/*`) are
platform-generated. Neither is Bitpool's to standardise; both are filtered out of coverage reporting.

---

## 3 — What the required tag set is

**Not yet decided.** The owner-tag decision and the required set belong to `DCF-777`, not here. Until
that lands, the script below **reports coverage** rather than asserting pass or fail — which is
useful now and becomes a compliance check the moment the standard exists.

The Azure side has a standard already (`Owner`, `Purpose`, `Criticality` at resource-group level,
`OwnerContact` recommended). AWS is expected to mirror it, applied at resource level.

---

## 4 — The check

`scripts/aws-tag-coverage.sh` in this skill. It runs per account, applies the exclusions above, and
reports:

- Total tagged resources, and how many survive the exclusions
- The surviving set broken down by `service:resource-type`
- Coverage of each candidate governance tag key across the surviving set
- Resources in the surviving set carrying **no** ownership tag at all

Run it across every account, not one:

```bash
for p in aws-aggregator aws-deployments aws-it aws-master aws-prod aws-test aws-cloudtrail-admin; do
  bash scripts/aws-tag-coverage.sh "$p"
done
```

### Reading the output

- **A large surviving count is not a failure** — it means the scope has not been narrowed to
  business-meaningful types yet. That narrowing is a decision, not a bug; see §5.
- **Zero coverage on an ownership key** means the register has no owner for those resources, which is
  the `A.5.9` gap.
- **A resource type you do not recognise** is worth investigating before excluding it. Guessing at
  exclusions is how real assets vanish from a register.

---

## 5 — The open scoping decision

After the exclusions, roughly a thousand resources survive in aws-prod, and much of that is
infrastructure plumbing — network interfaces, security-group rules, target groups, listeners,
subnets, snapshots.

A register that lists every one is technically complete and practically useless. The scoping decision
still to be made is **which resource types belong in the register at all**. The durable,
business-meaningful set is plausibly: S3 buckets, ECR repositories, RDS instances, EKS clusters,
non-EKS EC2 instances, Lambda functions, DynamoDB tables, KMS keys, Secrets Manager secrets, load
balancers, VPCs and ElastiCache clusters — a few hundred rather than a few thousand.

That decision belongs with `DCF-777` alongside the required tag set. Record it as an explicit
inclusion list, so what is absent from the register is absent by decision rather than by oversight.
