#!/usr/bin/env bash
# AWS asset tag coverage — the register check.
#
# Reports tag coverage across one AWS account, excluding ephemeral Kubernetes objects.
# Read-only: uses only resourcegroupstaggingapi get-resources.
#
# Usage:  bash aws-tag-coverage.sh <profile> [region]
# See:    references/aws-asset-tag-coverage.md for the exclusion rule and its reasoning.

set -uo pipefail

PROFILE="${1:?usage: aws-tag-coverage.sh <profile> [region]}"
REGION="${2:-ap-southeast-2}"
export AWS_PAGER=""

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# The five REQUIRED keys, agreed 2026-08-28 and published in the cloud resource tagging
# standard on the Bitpool Private Wiki. A scoped resource missing any of these is a
# register gap. DataClassification and IsPersonalData are how information assets are
# inventoried - through the asset that holds them - per ISO 27001 A.5.9.
REQUIRED_KEYS=(OwnerGroup Purpose Criticality DataClassification IsPersonalData)

# Additional keys observed in the estate. Recommended or legacy, not gaps when absent.
# Note: the ownership key is OwnerGroup, not Owner - that is the key already in use across the
# AWS estate, and the standard was written to match the estate rather than rename it. Owner is
# kept here only so a resource carrying the old key is still counted as owned.
OTHER_KEYS=(Owner OwnerContact ManagedBy IsCritical Environment WorkloadType Department Tier DataType Ephemeral PublicAccess)

GOV_KEYS=("${REQUIRED_KEYS[@]}" "${OTHER_KEYS[@]}")

is_required() {
  local k
  for k in "${REQUIRED_KEYS[@]}"; do [ "$k" = "$1" ] && return 0; done
  return 1
}

echo "==================================================================="
echo " AWS tag coverage : $PROFILE ($REGION)"
echo " $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "==================================================================="

if ! aws sts get-caller-identity --profile "$PROFILE" >/dev/null 2>&1; then
  echo "  SESSION ERROR - no valid credentials for profile '$PROFILE'."
  echo "  Run /aws-context, then: aws sso login --sso-session bitpool"
  exit 1
fi

# ---- collect every tagged ARN -------------------------------------------------
aws resourcegroupstaggingapi get-resources \
  --profile "$PROFILE" --region "$REGION" \
  --query 'ResourceTagMappingList[].ResourceARN' --output text 2>/dev/null \
  | tr '\t' '\n' | grep . > "$TMP/all.txt" || true

TOTAL=$(wc -l < "$TMP/all.txt" | tr -d ' ')
if [ "$TOTAL" -eq 0 ]; then
  echo "  No tagged resources found in $PROFILE/$REGION."
  exit 0
fi

# ---- exclusion 1: by ARN resource type ---------------------------------------
# eks:pod            - individual Kubernetes pods, the dominant volume
# ec2:fleet          - Karpenter provisioning artefacts
# ec2:spot-instances-request
grep -vE ':eks:[^:]*:[0-9]*:pod/' "$TMP/all.txt" \
  | grep -vE ':(fleet|spot-instances-request)/' > "$TMP/typed.txt" || true

TYPED=$(wc -l < "$TMP/typed.txt" | tr -d ' ')

# ---- exclusion 2: by tag presence (EKS nodes, CSI volumes/snapshots) ---------
: > "$TMP/k8s_tagged.txt"
for k in aws:eks:cluster-name CSIVolumeName CSIVolumeSnapshotName; do
  aws resourcegroupstaggingapi get-resources \
    --profile "$PROFILE" --region "$REGION" --tag-filters "Key=$k" \
    --query 'ResourceTagMappingList[].ResourceARN' --output text 2>/dev/null \
    | tr '\t' '\n' | grep . >> "$TMP/k8s_tagged.txt" || true
done
sort -u "$TMP/k8s_tagged.txt" -o "$TMP/k8s_tagged.txt"

sort -u "$TMP/typed.txt" -o "$TMP/typed.txt"
comm -23 "$TMP/typed.txt" "$TMP/k8s_tagged.txt" > "$TMP/scoped.txt"
SCOPED=$(wc -l < "$TMP/scoped.txt" | tr -d ' ')

echo
echo "-- Exclusions -----------------------------------------------------"
printf "  %-46s %8s\n" "Tagged resources, total"                 "$TOTAL"
printf "  %-46s %8s\n" "After excluding pods/fleet/spot by type" "$TYPED"
printf "  %-46s %8s\n" "After excluding EKS-node and CSI tags"   "$SCOPED"

echo
echo "-- Scoped set by service:resource-type ----------------------------"
awk -F: '{svc=$3; rest=$6; sub(/\/.*/,"",rest);
        if (svc=="s3" || svc=="sqs" || svc=="sns" || rest=="") print svc; else print svc":"rest}' "$TMP/scoped.txt" \
  | sort | uniq -c | sort -rn | head -40 | while read -r n t; do
      printf "  %6s  %s\n" "$n" "$t"
    done

echo
echo "-- Governance tag coverage across the scoped set ------------------"
echo "  (* = required by the cloud resource tagging standard)"
: > "$TMP/owned.txt"
for k in "${GOV_KEYS[@]}"; do
  if is_required "$k"; then mark="*"; else mark=" "; fi
  aws resourcegroupstaggingapi get-resources \
    --profile "$PROFILE" --region "$REGION" --tag-filters "Key=$k" \
    --query 'ResourceTagMappingList[].ResourceARN' --output text 2>/dev/null \
    | tr '\t' '\n' | grep . | sort -u > "$TMP/key.txt" || true
  HITS=$(comm -12 "$TMP/scoped.txt" "$TMP/key.txt" | wc -l | tr -d ' ')
  case "$k" in
    Owner|OwnerGroup|OwnerContact|ManagedBy)
      comm -12 "$TMP/scoped.txt" "$TMP/key.txt" >> "$TMP/owned.txt" ;;
  esac
  if [ "$SCOPED" -gt 0 ]; then PCT=$(( 100 * HITS / SCOPED )); else PCT=0; fi
  printf "  %s %-24s %6s / %-6s  %3s%%\n" "$mark" "$k" "$HITS" "$SCOPED" "$PCT"
done

sort -u "$TMP/owned.txt" -o "$TMP/owned.txt"
OWNED=$(wc -l < "$TMP/owned.txt" | tr -d ' ')
UNOWNED=$(( SCOPED - OWNED ))

echo
echo "-- Ownership ------------------------------------------------------"
printf "  %-46s %8s\n" "Carrying ANY ownership tag"    "$OWNED"
printf "  %-46s %8s\n" "Carrying NO ownership tag"     "$UNOWNED"
echo "  (ownership keys counted: Owner, OwnerGroup, OwnerContact, ManagedBy)"

if [ "$UNOWNED" -gt 0 ]; then
  echo
  echo "-- Unowned, by type (the A.5.9 gap) -------------------------------"
  comm -23 "$TMP/scoped.txt" "$TMP/owned.txt" \
    | awk -F: '{svc=$3; rest=$6; sub(/\/.*/,"",rest);
        if (svc=="s3" || svc=="sqs" || svc=="sns" || rest=="") print svc; else print svc":"rest}' \
    | sort | uniq -c | sort -rn | head -25 | while read -r n t; do
        printf "  %6s  %s\n" "$n" "$t"
      done
fi

echo
echo "Note: a large scoped count is not a failure - it means the register scope"
echo "has not been narrowed to business-meaningful resource types yet. That"
echo "narrowing is DCF-777's decision; see references/aws-asset-tag-coverage.md."
