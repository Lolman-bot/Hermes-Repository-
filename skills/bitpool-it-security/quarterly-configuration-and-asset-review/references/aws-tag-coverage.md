# AWS tag coverage

> **Read `references/snapshot-and-diff.md` first.** The tags are the live register; the
> snapshot is what lets this cycle be diffed against the last one. Both halves are the job,
> and the diff is the half a live query can never do for you afterwards.

**Snapshot and diff:**

```bash
wsl -e bash -lc 'python3 scripts/snapshot.py aws --resources tagged-resources.json \
  --cycle 2026-09 -o aws_2026-09.json'
wsl -e bash -lc 'python3 scripts/diff_snapshots.py aws_2026-06.json aws_2026-09.json --format markdown'
```

## What the register tracks — primary assets only

**Bitpool decision, 2026-09-17.** An allow-list of 13 resource types. Anything else is out.

| Group | Types | Count 2026-09-17 |
|---|---|---|
| Compute | `ec2:instance` · `eks:cluster` · `ecs:cluster` · `lambda:function` | 32 |
| Storage and code | `s3:bucket` · `ecr:repository` | 150 |
| Data stores | `rds:db` · `rds:cluster` · `dynamodb:table` · `elasticache:cluster` · `elasticache:replicationgroup` | 23 |
| Secrets and keys | `secretsmanager:secret` · `kms:key` | 52 |
| | **Total in register** | **257** |

Counts are 2026-09-18, across every account in the Organization and every region the estate is permitted to use.
Dropped from 46,505 tagged resources: **44,731** ephemeral by type (pods, fleets, spot requests),
**670** ephemeral by tag (EKS worker nodes, CSI volume churn), **847** not a primary type.

**The 2026-09-17 figure of 300 is superseded and should not be quoted.** It was collected in
`ap-southeast-2` only, and it counted EKS worker nodes as assets — see below.

## EKS worker nodes — excluded by cluster membership, not by provisioner

**102 tagged `ec2:instance` exist in the estate. 87 are EKS worker nodes. The register holds the
other 15.**

Bitpool runs **three** node-provisioning mechanisms and each tags differently:

| Mechanism | Its marker key | Instances |
|---|---|---|
| Managed node groups (legacy) | `aws:eks:cluster-name` | 67 |
| Karpenter | `karpenter.sh/nodeclaim`, `eks:eks-cluster-name` | 85 |
| Cluster-autoscaler node group | `eks:nodegroup-name`, `eks:cluster-name` | 2 |

The sets overlap; their union is 87. Only the first was excluded originally, so **Karpenter nodes
sat in the register and churned**. Measured over a 17-hour gap on 2026-09-18, the diff reported
**46 removals and 20 additions — every one a worker node.** A quarterly diff carrying that much
noise buries the one removal that matters, which is the entire reason the diff exists.

`snapshot.py` now matches **`kubernetes.io/cluster/<name>`**, which all three carry. Verified across
every allow-listed type on 2026-09-18: it selects **87 of 102** `ec2:instance` and **0 of the other
227** resources, and its hit set is *exactly* the union of all six provisioner-specific keys — no
instance in one set and not the other, in either direction. After the fix, the same 17-hour diff
reported **254 → 254, no change**.

**Match on cluster membership, never on a provisioner's key.** A fourth provisioner would tag
differently again, and chasing keys one at a time is what produced this defect. The property worth
testing is *"does this instance belong to a cluster"*.

This removes no compute from the inventory. The durable asset is the **cluster**, tracked as
`eks:cluster`; a node is to a cluster what a pod is to a node. The 15 survivors are the standalone
hosts — `OpenVPNAccessServer`, `ts.bitpool.com`, `edge.bitpool.com`, `node-red.bitpool.com`,
`bitpool-ftp`, the two device pipelines — which is what the register is for.

**Deliberately excluded, so the absences read as decisions rather than oversights:**

- **Copies** — RDS and ElastiCache snapshots, AMIs. They are copies of something already in the
  register and they turn over on a backup schedule, so including them opens every diff with dozens
  of meaningless additions and removals and buries the one that matters.
- **Configuration** — parameter groups, subnet groups, option groups, Beanstalk configuration
  templates. Settings for an asset, not assets.
- **Plumbing** — EBS volumes, ENIs, security groups, subnets, route tables, target groups,
  listeners, CloudFormation stacks, log groups, alarms, EventBridge rules.
- **Endpoints and messaging** — load balancers, API Gateway, SQS, SNS, Firehose, VPCs, ACM
  certificates, Cognito user pools. These carry or expose data rather than holding it.
  **Revisit Cognito** if a user pool ever holds production identities; that would make it primary.

`snapshot.py` records every excluded type it saw under `scope.excluded_types_seen` — **77 distinct
types on 2026-09-18**. **A type appearing there that should be primary is a scope decision, not
noise.** That list is the only thing standing between an allow-list and an asset class quietly
vanishing from the register.

It counts 77 rather than 66 because of a defect fixed on 2026-09-18: the list was previously
populated only for types that fell all the way through to the allow-list check, so a type dropped by
an *ephemeral tag* first never appeared in it at all. The one list guarding against a silent
disappearance had a silent gap of its own.

**Read `scope.ephemeral_drops_of_primary_types` alongside it.** That field names an *allow-listed*
type removed by an ephemeral rule — the only exclusion that can take a real asset out of the
register. It is what surfaced the EKS worker-node problem above, on its first run.

**AWS resource tags are the asset register.** There is no separate list to maintain.

Bitpool's estate is entirely AWS across multiple accounts under one Organization. **Do not hardcode
the account count here** — enumerate the profiles at run time via `/aws-context`. A written count
goes stale silently, and a reader cannot tell a stale count from a current one, so it gets trusted.

## The cycle

### 1. Confirm the session

**Delegate to `/aws-context`** — the once-per-session pre-flight. It checks the CLI and the IAM
Identity Center session, and carries the safe sign-in procedure.

One thing from it that matters enough to repeat: `aws sso login` must be forced to open the dedicated
Edge profile. The dedicated sign-in identity shares an Entra tenant with real admin accounts, and
signing in from the wrong browser profile can silently authenticate as the wrong identity **with no
visible error**. After sign-in, confirm the identity with `aws sts get-caller-identity`.

### 2. Enumerate the accounts, then collect

**Delegate to `/aws-query`**, which owns the call construction, the multi-account loop pattern and the
JMESPath gotchas.

Write output to a file per account, then analyse. Record the account, the identity used and the date
alongside it.

### 3. Check coverage of the required keys

The required key set and its casing convention are defined by the *Cloud resource tagging standard*
on the wiki. **That page is the authority — read it rather than working from a remembered list.** The
Azure reference in this same skill carries the keys as they stood at the last review, which is a
starting point for comparison, not a substitute.

`OwnerGroup` records the accountable **team**, not an individual, and is deliberately free text.

Report coverage per account and per resource type, and list every in-scope resource missing a
required key.

### 4. Tag what is missing

Apply the required keys to anything in scope that lacks them. A resource that should not be in scope
gets recorded as an exclusion with a reason — not silently skipped.

### 5. Evidence

Per `references/evidence-contract.md`. Retain the per-account output in the cycle folder.

## What this does not rely on

**Drata's AWS asset list is not the register.** Its cloud resource list is not cited as the inventory.

**Do not delete the Drata AWS connection** — roughly 35 enabled infrastructure monitoring tests read
from it. It stays connected; its asset list simply is not the register.

## Known state to check, not assume

The AWS sub-task was **`Cancelled`** in the 2026-08 cycle, and the reason is not recorded. AWS is the
largest register in the estate and was the only one with no evidence retained that quarter.

**Do not treat a cancelled sub-task as a passed check.** Either the work was covered elsewhere — in
which case record where, as a scope decision — or it was cancelled in error and the cycle owes a run.
Ask before writing either into the evidence.
