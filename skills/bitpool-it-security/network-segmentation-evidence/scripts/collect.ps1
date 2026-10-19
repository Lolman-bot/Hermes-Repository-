# collect.ps1 - read-only AWS network evidence collection.
#
# Fixes over v1.0:
#   * account list comes from AWS Organizations, not a hardcoded literal
#   * every enabled region is probed, not just the primary
#   * load balancers are collected for EVERY account (v1.0 only did aws-prod,
#     which silently mislabelled exposure scope elsewhere)
#   * transit gateways and VPC endpoints are collected AND modelled
#   * provenance is stamped at collection time and hashed
param(
  [string]$OutDir = ".\dump",
  [string]$OrgProfile = "aws-master"
)
$ErrorActionPreference = "Continue"
$env:AWS_PAGER = ""
$started = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
New-Item -ItemType Directory -Force $OutDir | Out-Null

# --- who is running this, and under what identity -------------------------
$idJson = aws sts get-caller-identity --profile $OrgProfile --output json 2>$null
$ident  = $idJson | ConvertFrom-Json
Write-Output "identity: $($ident.Arn)"

# --- accounts, from Organizations rather than a literal --------------------
$orgRaw = aws organizations list-accounts --profile $OrgProfile --output json 2>$null
$orgAccounts = @()
if ($orgRaw) {
  $orgAccounts = ($orgRaw | ConvertFrom-Json).Accounts |
                 Where-Object { $_.Status -eq "ACTIVE" } |
                 Select-Object Id, Name, Email
}
Write-Output "organizations reports $($orgAccounts.Count) active accounts"

# --- map local profiles to account ids ------------------------------------
$profiles = @()
$awsConfig = if ($env:AWS_CONFIG_FILE) { $env:AWS_CONFIG_FILE } else { Join-Path (Join-Path $HOME ".aws") "config" }
foreach ($line in (Get-Content $awsConfig)) {
  if ($line -match '^\[profile\s+(.+?)\]\s*$') { $profiles += $Matches[1] }
}
$map = @{}
foreach ($p in $profiles) {
  $r = aws sts get-caller-identity --profile $p --output json 2>$null | ConvertFrom-Json
  if ($r) { $map[$p] = $r.Account; Write-Output "  profile $p -> $($r.Account)" }
}

# --- declared exclusions ---------------------------------------------------
# An excluded account is a STATED scope decision carrying a reason, not a gap.
# Anything in the org that is neither surveyed nor excluded IS a gap.
$excluded = @()
$exclPath = Join-Path $PSScriptRoot "exclusions.json"
if (Test-Path $exclPath) {
  $excluded = (Get-Content $exclPath -Raw | ConvertFrom-Json).excluded_accounts
  Write-Output "$($excluded.Count) account(s) excluded by declared scope decision"
}
$exclIds = @($excluded | ForEach-Object { $_.id })

# --- accounts with no local profile and no exclusion = a coverage gap ------
$covered = $map.Values | Sort-Object -Unique
$uncovered = @()
foreach ($a in $orgAccounts) {
  if (($covered -notcontains $a.Id) -and ($exclIds -notcontains $a.Id)) { $uncovered += $a }
}
if ($uncovered.Count -gt 0) {
  Write-Output "WARNING: $($uncovered.Count) org account(s) neither surveyed nor excluded:"
  foreach ($a in $uncovered) { Write-Output "  UNCOVERED $($a.Id) $($a.Name)" }
} else {
  Write-Output "every org account is either surveyed or explicitly excluded"
}

# --- enabled regions -------------------------------------------------------
$firstProfile = ($map.Keys | Select-Object -First 1)
$regions = (aws ec2 describe-regions --profile $firstProfile --region ap-southeast-2 `
            --query "Regions[].RegionName" --output text 2>$null) -split "\s+" |
           Where-Object { $_ -ne "" } | Sort-Object
Write-Output "probing $($regions.Count) enabled regions across $($map.Count) accounts"

# --- pass 1: where do VPCs actually exist? --------------------------------
$present = @()
foreach ($p in $map.Keys) {
  foreach ($r in $regions) {
    $n = aws ec2 describe-vpcs --profile $p --region $r --query "length(Vpcs)" --output text 2>$null
    if ($n -and $n -ne "0" -and $n -ne "None") {
      $present += [pscustomobject]@{ profile = $p; region = $r; vpcs = [int]$n }
      Write-Output "  $p/$r -> $n vpc(s)"
    }
  }
}

# --- pass 2: full sweep only where something exists ------------------------
$kinds = @{
  "vpcs"      = "ec2 describe-vpcs";
  "subnets"   = "ec2 describe-subnets";
  "rtb"       = "ec2 describe-route-tables";
  "sg"        = "ec2 describe-security-groups";
  "nacl"      = "ec2 describe-network-acls";
  "peer"      = "ec2 describe-vpc-peering-connections";
  "flowlogs"  = "ec2 describe-flow-logs";
  "tgw"       = "ec2 describe-transit-gateway-attachments";
  "endpoints" = "ec2 describe-vpc-endpoints";
  "eni"       = "ec2 describe-network-interfaces";
  "elbv2"     = "elbv2 describe-load-balancers"
}
foreach ($row in $present) {
  foreach ($k in $kinds.Keys) {
    $parts = $kinds[$k] -split " "
    $file = Join-Path $OutDir "$($row.profile)__$($row.region)__$k.json"
    $out = & aws $parts[0] $parts[1] --profile $row.profile --region $row.region --output json 2>$null
    if ($out) { $out | Out-File -Encoding utf8 $file }
  }
  Write-Output "  swept $($row.profile)/$($row.region)"
}

# --- provenance ------------------------------------------------------------
$files = Get-ChildItem $OutDir -Filter *.json | Sort-Object Name
$hashes = @{}
foreach ($f in $files) { $hashes[$f.Name] = (Get-FileHash $f.FullName -Algorithm SHA256).Hash.Substring(0,16) }
$combined = ($hashes.Keys | Sort-Object | ForEach-Object { "$_=$($hashes[$_])" }) -join ";"
$sha = [System.BitConverter]::ToString(
        [System.Security.Cryptography.SHA256]::Create().ComputeHash(
          [System.Text.Encoding]::UTF8.GetBytes($combined))).Replace("-","").Substring(0,16)

$manifest = [ordered]@{
  generator        = "netpack v1.1"
  collected_utc    = $started
  finished_utc     = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
  collected_by     = $ident.Arn
  identity_account = $ident.Account
  org_accounts     = $orgAccounts
  uncovered_accounts = $uncovered
  excluded_accounts  = $excluded
  profiles         = $map
  regions_enabled  = $regions
  regions_with_vpcs = $present
  file_count       = $files.Count
  dump_digest      = $sha
  file_hashes      = $hashes
}
$manifest | ConvertTo-Json -Depth 6 | Out-File -Encoding utf8 (Join-Path $OutDir "_manifest.json")
Write-Output ""
Write-Output "COLLECTION COMPLETE"
Write-Output "  files:  $($files.Count)"
Write-Output "  digest: $sha"
Write-Output "  regions with VPCs: $(($present | ForEach-Object { $_.region } | Sort-Object -Unique) -join ', ')"
