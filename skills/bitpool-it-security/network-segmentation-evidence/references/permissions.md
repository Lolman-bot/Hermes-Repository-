# AWS permissions required

Verified 2026-09-01 by fetching the actual AWS managed policy documents and testing each required
action against them — not inferred from policy names.

## The answer

Attach **two AWS-managed policies** to the `aws-mcp-access` permission set in IAM Identity Center:

| Policy | ARN | What it provides |
|---|---|---|
| **SecurityAudit** | `arn:aws:iam::aws:policy/SecurityAudit` | Every `ec2:Describe*`, `elasticloadbalancing:Describe*` and `organizations:List*` the sweep needs |
| **AWSAccountManagementReadOnlyAccess** | `arn:aws:iam::aws:policy/AWSAccountManagementReadOnlyAccess` | `account:ListRegions` and `account:GetRegionOptStatus` — the one gap in SecurityAudit |

**No custom policy is required, and no StackSet-deployed role is needed.** Both are AWS-managed,
both are read-only, and together they are strictly narrower than `ReadOnlyAccess`.

## Why not the alternatives

| Candidate | Verdict |
|---|---|
| `ReadOnlyAccess` | Covers everything, but reads S3 object data, Secrets Manager metadata, DynamoDB contents and much more. Far broader than this tool needs |
| `SecurityAudit` alone | Missing `account:ListRegions`, which is how region opt-in status is verified |
| `AWSOrganizationsReadOnlyAccess` | Grants the Organizations calls *and* `account:ListRegions`, but none of the EC2 or ELB describes |
| `ViewOnlyAccess` | Does not resolve as an AWS-managed policy on this account |

## Coverage matrix

Tested action by action against the fetched policy documents.

| Action | Why the tool needs it | SecurityAudit | AWSAccountMgmtRO |
|---|---|---|---|
| `sts:GetCallerIdentity` | Identity check | n/a — see note | n/a |
| `organizations:ListAccounts` | Scope from the Organization | ✅ | ❌ |
| `organizations:ListDelegatedAdministrators` | Who aggregates findings | ✅ | ❌ |
| `organizations:ListDelegatedServicesForAccount` | What is delegated | ✅ | ❌ |
| `account:ListRegions` | Region opt-in status | ❌ | ✅ |
| `ec2:DescribeRegions` | Enabled regions | ✅ | ❌ |
| `ec2:DescribeVpcs` | VPC inventory | ✅ | ❌ |
| `ec2:DescribeSubnets` | Subnet tiers | ✅ | ❌ |
| `ec2:DescribeRouteTables` | Tier derivation — the load-bearing one | ✅ | ❌ |
| `ec2:DescribeSecurityGroups` | Exposure analysis | ✅ | ❌ |
| `ec2:DescribeNetworkAcls` | NACL posture | ✅ | ❌ |
| `ec2:DescribeFlowLogs` | Flow log coverage | ✅ | ❌ |
| `ec2:DescribeVpcPeeringConnections` | Adjacency graph | ✅ | ❌ |
| `ec2:DescribeTransitGatewayAttachments` | Adjacency graph | ✅ | ❌ |
| `ec2:DescribeVpcEndpoints` | Endpoint inventory | ✅ | ❌ |
| `ec2:DescribeNetworkInterfaces` | Whether a VPC is actually live | ✅ | ❌ |
| `elasticloadbalancing:DescribeLoadBalancers` | Internal vs internet-facing scheme | ✅ | ❌ |

> **`sts:GetCallerIdentity` needs no permission.** AWS always allows it for any authenticated
> principal and it cannot be denied by an identity policy. A permission checker will report it as
> "not granted" by every policy; that is a false negative, not a gap.

`SecurityAudit` also happens to cover three useful side checks the tool does not strictly need:
`securityhub:ListOrganizationAdminAccounts`, `sso:ListInstances`, `s3:ListAllMyBuckets`.

## The one thing no managed policy covers

`controltower:ListLandingZones` appears in **none** of the candidates, including `ReadOnlyAccess`.
The tool does not need it — it was used for a one-off landing-zone question. If landing-zone drift
checking is ever wanted, it needs a small inline policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["controltower:ListLandingZones", "controltower:GetLandingZone"],
    "Resource": "*"
  }]
}
```

## What happens without these

The sweep still completes — it did on 2026-09-01 — but two calls fail and the gaps are silent
unless you look:

- `account:ListRegions` → `AccessDeniedException`. Region opt-in status cannot be confirmed from
  the API, so the claim "none of these regions can be disabled" rests on reading the region names
  rather than on evidence. That is sound reasoning but it is not evidence, and the difference
  matters in an audit.
- `controltower:ListLandingZones` → `AccessDeniedException`. Governed-region drift cannot be
  checked at all.
