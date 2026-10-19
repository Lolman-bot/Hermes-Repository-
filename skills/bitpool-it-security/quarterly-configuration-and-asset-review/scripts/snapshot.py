#!/usr/bin/env python3
"""Normalise a raw cloud dump into a canonical asset-register snapshot.

The tags ARE the register. This does not replace them -- it freezes what the register
said on one date, so the next cycle can diff against it and see what appeared or
vanished without anyone accounting for it.

One output shape for all three cloud registers, so diff_snapshots.py needs no
per-register logic:

    {
      "register": "aws|azure|github",
      "cycle":    "2026-09",
      "captured": "2026-09-17T15:41:00Z",
      "source":   "<what produced this, in words>",
      "scope":    {...counts that make the run reproducible...},
      "excluded": {...what was dropped and why...},
      "items":    { "<stable id>": {"name":..., "type":..., "unit":..., "attrs": {...}} }
    }

Stable ids, never names -- a rename must read as a change, not as a delete plus an add:
    AWS     ARN
    Azure   resource id / resource group id
    GitHub  numeric repository id

Pure stdlib. Run through WSL.

Usage:
    snapshot.py aws    --resources tagged.json               --cycle 2026-09 -o aws_2026-09.json
    snapshot.py azure  --resources res.json --groups grp.json --cycle 2026-09 -o azure_2026-09.json
    snapshot.py github --values props.json  --repos repos.json --cycle 2026-09 -o github_2026-09.json
"""

import argparse
import collections
import datetime
import json
import sys

# The required set from the cloud resource tagging standard. Same keys in both clouds and
# in GitHub custom properties, deliberately -- one convention covers all three.
REQUIRED = ["OwnerGroup", "Purpose", "Criticality", "DataClassification", "IsPersonalData"]
RECOMMENDED = ["OwnerContact", "Environment", "WorkloadType", "Ephemeral", "HasPublicAccess"]
GOVERNANCE = REQUIRED + RECOMMENDED

# Platform-generated keys are not Bitpool's to standardise and are filtered from coverage.
NOISE_PREFIXES = ("aws:", "app.kubernetes.io/", "eks.amazonaws.com/", "stackgres.io/",
                  "elbv2.k8s.aws/", "hidden-",
                  # Karpenter and Kubernetes cluster-membership keys. Machine-written, and
                  # counting them as governance attributes makes an unowned node look
                  # richly tagged.
                  "karpenter.sh/", "karpenter.k8s.aws/", "kubernetes.io/", "eks:")
NOISE_EXACT = {"app", "chart", "release", "heritage", "component"}

# --- AWS scoping, per the cloud resource tagging standard. Three mechanisms. ---
#
# 1. EPHEMERAL: runtime artefacts of something already in the register. Pods alone are the
#    overwhelming majority of tagged resources in aws-prod.
AWS_EPHEMERAL_TYPES = {"eks:pod", "ec2:fleet", "ec2:spot-instances-request"}
AWS_EXCLUDING_TAGS = ("CSIVolumeName", "CSIVolumeSnapshotName")
#
# EKS WORKER NODES, excluded by CLUSTER MEMBERSHIP rather than by provisioner.
#
# Bitpool runs THREE node-provisioning mechanisms and each tags differently. Excluding one
# key at a time left the others in the register, churning:
#
#   managed node groups (legacy)  aws:eks:cluster-name                        67 instances
#   Karpenter                     karpenter.sh/nodeclaim, eks:eks-cluster-name 85
#   cluster-autoscaler node group eks:nodegroup-name, eks:cluster-name          2
#
# Measured over a 17-hour gap on 2026-09-18, chasing these keys individually left the
# register reporting 46 removals and 20 additions -- every one a worker node, none of it
# real. A quarterly diff full of that noise buries the one removal that matters, which is
# the entire reason the diff exists.
#
# kubernetes.io/cluster/<name> is carried by ALL of them and is what is matched instead.
# Verified 2026-09-18 across every allow-listed type: it selects 87 of 102 ec2:instance and
# 0 of the other 227 resources, and its hit set is exactly the union of all six
# provisioner-specific keys -- no instance in one set and not the other, in either
# direction. A fourth provisioner would still be caught, because cluster membership is the
# property being tested rather than the tool that wrote the tag.
#
# This removes no compute from the inventory. The durable asset is the CLUSTER, tracked as
# eks:cluster; a node is to a cluster what a pod is to a node. The 15 EC2 instances that
# survive are the standalone ones -- named hosts with owners, which is what the register is
# for.
AWS_EXCLUDING_TAG_PREFIXES = ("kubernetes.io/cluster/",)

# 2. THE REGISTER SCOPE -- an ALLOW-LIST of primary asset types.
#
#    Bitpool decision, 2026-09-17: track primary assets only. Compute, storage, data
#    stores, code artefacts and secrets. Everything else is excluded.
#
#    What this deliberately leaves out, and why:
#      - Copies of something already listed: RDS/ElastiCache snapshots, AMIs. They churn on
#        a backup schedule, so including them opens every quarterly diff with dozens of
#        additions and removals that mean nothing, and buries the one that does.
#      - Configuration objects: parameter groups, subnet groups, option groups, Beanstalk
#        configuration templates. Settings for an asset, not assets.
#      - Plumbing: EBS volumes, ENIs, security groups, subnets, route tables, target
#        groups, listeners, CloudFormation stacks, log groups, alarms, EventBridge rules.
#      - Endpoints and messaging: load balancers, API Gateway, SQS, SNS, Firehose, VPCs,
#        ACM certificates, Cognito user pools. These carry or expose data rather than
#        holding it. Reconsider Cognito if a user pool ever holds production identities.
#
#    An allow-list is the safer shape here: a resource type nobody has decided on is
#    excluded rather than silently swept into the register with no owner. The cost is that
#    a genuinely new primary type would be dropped unnoticed -- so build_aws reports every
#    excluded type it saw, and a new one turning up in that list is a scope decision to
#    make, not noise to skim past.
AWS_INCLUDED_TYPES = {
    # compute
    "ec2:instance", "eks:cluster", "ecs:cluster", "lambda:function",
    # storage and code artefacts
    "s3:bucket", "ecr:repository",
    # data stores
    "rds:db", "rds:cluster", "dynamodb:table",
    "elasticache:cluster", "elasticache:replicationgroup",
    # secrets and keys
    "secretsmanager:secret", "kms:key",
}

# Most ARNs read service:type/name. These services carry no type segment at all --
# arn:aws:s3:::my-bucket -- so the type must be supplied rather than parsed, or every
# bucket is typed as its own name and matches no list.
NO_TYPE_SEGMENT = {"s3": "bucket", "sqs": "queue", "sns": "topic"}


def governance_only(tags):
    """Drop platform noise; keep what the register is actually asserting."""
    out = {}
    for k, v in (tags or {}).items():
        if k in NOISE_EXACT or k.startswith(NOISE_PREFIXES):
            continue
        out[k] = v
    return out


def arn_resource_type(arn):
    """service:type from an ARN, e.g. arn:aws:eks:...:pod/x -> eks:pod."""
    parts = arn.split(":")
    if len(parts) < 6:
        return ""
    service, tail = parts[2], parts[5]
    if service in NO_TYPE_SEGMENT:
        return "%s:%s" % (service, NO_TYPE_SEGMENT[service])
    kind = tail.split("/")[0] if "/" in tail else tail
    return "%s:%s" % (service, kind)


def build_aws(args):
    raw = json.load(open(args.resources, encoding="utf-8-sig"))
    # Accept either the bare list or the get-resources envelope.
    rows = raw.get("ResourceTagMappingList", raw) if isinstance(raw, dict) else raw

    items = {}
    dropped = {"ephemeral_type": 0, "ephemeral_tag": 0, "ephemeral_flag": 0,
               "not_a_primary_type": 0}
    excluded_types = collections.Counter()
    # An IN-SCOPE type dropped by an ephemeral rule is the one exclusion that can remove a
    # real asset from the register. EKS-managed EC2 instances carry aws:eks:cluster-name,
    # so the rule written to drop pod churn also drops the nodes the pods run on. Counted
    # per type so the trade is visible rather than implied.
    ephemeral_drops_in_scope = collections.Counter()
    # Self-declared opt-outs. A resource excluding ITSELF from the asset register by
    # setting its own tag is a control weakness however it is decided, so the ARNs are
    # named rather than merely counted -- a count cannot be reviewed.
    ephemeral_flag_arns = []

    for r in rows:
        arn = r.get("ResourceARN") or r.get("arn")
        if not arn:
            continue
        tags = {t["Key"]: t["Value"] for t in (r.get("Tags") or [])}
        rtype = arn_resource_type(arn)
        in_scope = rtype in AWS_INCLUDED_TYPES

        # Record EVERY type that failed the allow-list, whichever rule actually dropped it.
        # Recording only those that fell all the way through to the allow-list check meant
        # a type carrying an ephemeral tag never appeared here at all -- so an asset class
        # could leave the register with nothing in the output naming it. This list is the
        # only thing standing between an allow-list and a silent disappearance, and it has
        # to be complete to do that job.
        if not in_scope:
            excluded_types[rtype] += 1

        if rtype in AWS_EPHEMERAL_TYPES:
            dropped["ephemeral_type"] += 1
            continue
        if (any(t in tags for t in AWS_EXCLUDING_TAGS)
                or any(k.startswith(AWS_EXCLUDING_TAG_PREFIXES) for k in tags)):
            dropped["ephemeral_tag"] += 1
            if in_scope:
                ephemeral_drops_in_scope[rtype] += 1
            continue
        if str(tags.get("Ephemeral", "")).lower() == "true":
            dropped["ephemeral_flag"] += 1
            ephemeral_flag_arns.append(arn)
            if in_scope:
                ephemeral_drops_in_scope[rtype] += 1
            continue
        if not in_scope:
            dropped["not_a_primary_type"] += 1
            continue

        items[arn] = {"name": arn.rsplit("/", 1)[-1].rsplit(":", 1)[-1],
                      "type": rtype, "unit": "resource",
                      "attrs": governance_only(tags)}

    scope = {"resources_raw": len(rows), "resources_in_register": len(items),
             "primary_types_tracked": sorted(AWS_INCLUDED_TYPES),
             # Retained so a type that SHOULD be primary is visible rather than silently
             # absent. A new entry here is a scope decision, not noise.
             "excluded_types_seen": dict(excluded_types.most_common()),
             # A primary type dropped as ephemeral. Read this every cycle -- it is where a
             # real asset goes missing without ever appearing above.
             "ephemeral_drops_of_primary_types": dict(ephemeral_drops_in_scope.most_common()),
             # Named, because a self-declared opt-out has to be reviewable.
             "self_declared_ephemeral": sorted(ephemeral_flag_arns)}
    return items, scope, dropped


def build_azure(args):
    res = json.load(open(args.resources, encoding="utf-8-sig"))
    grp = json.load(open(args.groups, encoding="utf-8-sig"))

    items = {}
    # The resource GROUP is Azure's tagging unit, so groups carry the governance attrs.
    for g in grp:
        items[g["id"].lower()] = {
            "name": g["name"], "type": "resourceGroup", "unit": "group",
            "attrs": governance_only(g.get("tags")),
        }
    # Resources are tracked for existence. They are not expected to carry tags, and an
    # untagged resource is NOT a finding in Azure -- the group above is what must be tagged.
    for r in res:
        items[r["id"].lower()] = {
            "name": r["name"], "type": r.get("type", ""), "unit": "resource",
            # resourceGroup casing is inconsistent between the two APIs; normalise or one
            # group appears twice and the count is wrong.
            "attrs": {"resourceGroup": (r.get("resourceGroup") or "").lower(),
                      "location": r.get("location", "")},
        }

    return items, {"resource_groups": len(grp), "resources": len(res)}, {}


def build_github(args):
    vals = json.load(open(args.values, encoding="utf-8-sig"))
    repos = json.load(open(args.repos, encoding="utf-8-sig")) if args.repos else []
    meta = {r["name"]: r for r in repos}

    items = {}
    for row in vals:
        rid = str(row.get("repository_id") or row.get("repository_name"))
        name = row.get("repository_name")
        props = {p["property_name"]: p.get("value")
                 for p in (row.get("properties") or []) if p.get("value") is not None}
        m = meta.get(name, {})
        attrs = dict(props)
        if m:
            attrs["visibility"] = m.get("visibility", "")
            attrs["archived"] = str(m.get("archived", False))
        items[rid] = {"name": name, "type": "repository", "unit": "repository",
                      "attrs": attrs}

    scope = {"repositories_with_values": len(items)}
    if repos:
        scope["repositories_listed"] = len(repos)
    return items, scope, {}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("register", choices=["aws", "azure", "github"])
    ap.add_argument("--resources", help="aws: tagged-resources json. azure: az resource list")
    ap.add_argument("--groups", help="azure: az group list")
    ap.add_argument("--values", help="github: orgs/<org>/properties/values")
    ap.add_argument("--repos", help="github: orgs/<org>/repos (optional, adds visibility)")
    ap.add_argument("--cycle", required=True, help="e.g. 2026-09")
    ap.add_argument("--source", default="", help="what produced this, in words")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()

    if a.register == "aws":
        if not a.resources:
            ap.error("aws needs --resources")
        items, scope, dropped = build_aws(a)
    elif a.register == "azure":
        if not (a.resources and a.groups):
            ap.error("azure needs --resources and --groups")
        items, scope, dropped = build_azure(a)
    else:
        if not a.values:
            ap.error("github needs --values")
        items, scope, dropped = build_github(a)

    # Coverage of the required keys, over the units that are supposed to carry them.
    bearing = [i for i in items.values() if i["unit"] in ("group", "repository", "resource")]
    if a.register == "azure":
        bearing = [i for i in items.values() if i["unit"] == "group"]
    complete = sum(1 for i in bearing if all(i["attrs"].get(k) for k in REQUIRED))

    snap = {
        "register": a.register,
        "cycle": a.cycle,
        "captured": datetime.datetime.now(datetime.timezone.utc)
                    .replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source": a.source,
        "scope": scope,
        "excluded": dropped,
        "coverage": {"units_bearing_tags": len(bearing),
                     "all_required_keys_present": complete},
        "items": items,
    }

    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(snap, f, indent=2, sort_keys=True)

    print("register : %s   cycle %s" % (a.register, a.cycle))
    for k, v in sorted(scope.items()):
        if isinstance(v, (list, dict)):
            continue
        print("  %-28s %s" % (k, v))
    if dropped and any(dropped.values()):
        print("  excluded from register:")
        for k, v in sorted(dropped.items()):
            print("      %-24s %s" % (k, v))
    if scope.get("primary_types_tracked"):
        print("  primary types tracked (%d): %s"
              % (len(scope["primary_types_tracked"]),
                 ", ".join(scope["primary_types_tracked"])))
    seen = scope.get("excluded_types_seen") or {}
    if seen:
        top = list(seen.items())[:8]
        print("  excluded types seen (%d distinct), largest: %s"
              % (len(seen), ", ".join("%s %d" % (k, v) for k, v in top)))
        print("      full list is in the snapshot's scope.excluded_types_seen -- a type that"
              " SHOULD be primary is visible there, not silently absent")
    print("  %-28s %d of %d" % ("all required keys present", complete, len(bearing)))
    print("written  : %s  (%d items)" % (a.out, len(items)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
