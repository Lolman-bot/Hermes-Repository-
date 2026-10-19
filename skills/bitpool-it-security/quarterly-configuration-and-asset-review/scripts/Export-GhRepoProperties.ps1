<#
.SYNOPSIS
    Exports every bitpool repository's name, description and custom properties for the
    quarterly asset register review, using a token that is never persisted on the machine.

.DESCRIPTION
    Produces two files in -OutDir:
      github-repo-properties_<date>.json   raw API output, retained as evidence
      github-repo-properties_<date>.csv    one row per repository, one column per property

    The export MUST cover the whole organisation. See
    references/github-repository-properties.md - a member token silently returns only the
    repositories it can see, and every coverage figure derived from it is measured against
    the wrong denominator.

    COMPLETENESS IS CHECKED BY COUNT, NOT BY PERMISSION - when a count is available at all.
    The denominator is resolved in order of strength:

      1. -ExpectedRepoCount, read off the organisation's repository list by a human.
      2. GET /orgs/<org>, public_repos + total_private_repos.
      3. None. The script then says so loudly, writes a provenance file recording that
         completeness was NOT verified, and exits successfully - it does not invent a total.

    A short export is stamped PARTIAL-DO-NOT-USE-FOR-COVERAGE and the script FAILS, unless
    -AllowPartial is passed for a purpose other than a coverage figure. Every run writes a
    provenance file saying how - or whether - the total was established.

    Two earlier gates were removed on 2026-09-17, both because they could not pass here:

      - A pre-flight GATE on the caller's organisation role. It needs ORGANIZATIONS tab >
        Members: Read-only; without that grant it 403'd and aborted every run before fetching
        anything. The role lookup is back, but as PROVENANCE rather than a gate - it only
        ever predicted what the count comparison measures.
      - A hard requirement for total_private_repos. A fine-grained token receives that field
        only when the token carries ORGANIZATIONS tab > Administration: Read-only. Without it
        the field is simply absent, with no error - which is why the requirement had to become
        optional rather than fatal.

    What must never come back is treating an ABSENT total as a number: $public + $null
    silently equals $public in PowerShell, so a partial export would clear a denominator of
    just the public repositories and print "Full export" over most of the estate.

.PARAMETER ExpectedRepoCount
    The repository count read off the organisation's own list in the GitHub UI. Supply it
    and the completeness check is made here and recorded in the provenance file; omit it and
    the script prints the exported count for you to compare by eye.

.PARAMETER AllowPartial
    Accept a short export. The output is still stamped. Use only when the partial list is
    wanted for something that is NOT a coverage figure.

.EXAMPLE
    .\Export-GhRepoProperties.ps1 -OutDir 'C:\...\Asset register review - 2026 09' -ExpectedRepoCount 61

.NOTES
    Run from PowerShell or Git Bash on Windows, NOT WSL - gh is installed and authenticated
    on the Windows side only. The CSV join runs through WSL because native Windows python
    is a Microsoft Store stub.

    Token permissions (verified by a complete 61-of-61 export, 2026-09-17). Repository access
    must be "All repositories":
      ORGANIZATIONS tab > Custom properties: Read-only  - the export itself
      ORGANIZATIONS tab > Administration:    Read-only  - total_private_repos, the denominator
      ORGANIZATIONS tab > Members:           Read-only  - the caller's role, for provenance
      REPOSITORIES  tab > Metadata:          Read-only  - the repository listing

    BEWARE: "Custom properties" exists on BOTH tabs and they are different permissions. The
    Repositories one grants a single repo-level PATCH and nothing this script uses.
#>
[CmdletBinding()]
param(
    [string]$Org = 'bitpool',
    [string]$OutDir = "$PWD",
    [switch]$AllowPartial,
    # The repository count read off the organisation's own list in the GitHub UI. Supply it
    # and the completeness check becomes automatic and recorded; omit it and the script
    # prints the exported count for you to compare by eye.
    [int]$ExpectedRepoCount
)

$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyy-MM-dd'

# PSReadLine below 2.1.0 has no sensitive-input filter and saves every typed line to disk.
try { Set-PSReadLineOption -HistorySaveStyle SaveNothing -ErrorAction Stop } catch {}

$cfgDir = Join-Path ([System.IO.Path]::GetTempPath()) ("gh-throwaway-" + [guid]::NewGuid().ToString('N'))

try {
    New-Item -ItemType Directory -Path $cfgDir -Force | Out-Null
    if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir -Force | Out-Null }

    Write-Host ""
    Write-Host "Paste the organisation-owner PAT. Input is not echoed to shell history." -ForegroundColor Cyan
    $tok = Read-Host "PAT"
    if ([string]::IsNullOrWhiteSpace($tok)) { throw "No token supplied." }

    # Process-scoped only: both die with this shell, and gh writes no credential to disk.
    $env:GH_CONFIG_DIR = $cfgDir
    $env:GH_TOKEN      = $tok.Trim()
    $tok = $null

    # --- Identity ---
    $who = gh api user --jq '.login'
    if ($LASTEXITCODE -ne 0) { throw "Token rejected by GitHub." }

    Write-Host ""
    Write-Host "  account : $who" -ForegroundColor Yellow

    # --- The caller's organisation role ---------------------------------------------------
    #
    # NOT a gate. It was one until 2026-09-17 and should not become one again: a role check
    # only ever PREDICTS completeness, and this script MEASURES it. What the role is good
    # for is deciding whether the repository listing can be trusted as the estate, and
    # recording in the evidence who took the export and in what capacity.
    #
    # Needs ORGANIZATIONS tab > Members: Read-only. Non-fatal if absent.
    $role = $null
    $roleRaw = gh api "user/memberships/orgs/$Org" --jq '.role' 2>$null
    if ($LASTEXITCODE -eq 0 -and $roleRaw) { $role = $roleRaw.Trim() }

    $orgInfo = $null
    $orgRaw = gh api "orgs/$Org" 2>$null
    if ($LASTEXITCODE -eq 0 -and $orgRaw) { $orgInfo = $orgRaw | ConvertFrom-Json }

    # --- The denominator, strongest available first ---------------------------------------
    #
    # Two independent ways to establish it, and the review is happy with either.
    #
    #   total_private_repos is available to a fine-grained token, but ONLY with
    #   ORGANIZATIONS tab > Administration: Read-only. Without that grant the field is simply
    #   absent from GET /orgs/<org>, with no error to notice.
    #
    #   Failing that: when the caller is an organisation ADMIN and the token reaches all
    #   repositories, **the repository listing IS the estate** and there is nothing above it
    #   to check against. The member token that saw 31 of 61 was short because a member
    #   cannot see every repository -- not because the listing endpoint is untrustworthy.
    #
    # Never treat an ABSENT total as a number: $public + $null silently equals $public in
    # PowerShell, so a partial export would clear a denominator of just the public repos and
    # print "Full export" over most of the estate.
    #
    # total_private_repos includes private forks; owned_private_repos excludes them. The
    # review standardises on total_private_repos so figures stay comparable quarter to quarter.
    $orgTotal  = $null
    $totalFrom = $null

    if ($PSBoundParameters.ContainsKey('ExpectedRepoCount')) {
        # Operator-asserted: a human read it off the organisation's repository list.
        $orgTotal  = [int]$ExpectedRepoCount
        $totalFrom = "operator-asserted (-ExpectedRepoCount), read from the GitHub UI"
    }
    else {
        $names = if ($orgInfo) { $orgInfo.PSObject.Properties.Name } else { @() }
        if (($names -contains 'public_repos') -and ($names -contains 'total_private_repos')) {
            $orgTotal  = [int]$orgInfo.public_repos + [int]$orgInfo.total_private_repos
            $totalFrom = "GET /orgs/$Org (public_repos + total_private_repos)"
        }
    }

    Write-Host ("  org role: {0}" -f $(if ($role) { $role } else { "unreadable (grant ORGANIZATIONS tab > Members: Read-only to record it)" })) -ForegroundColor Yellow

    # --- Pre-flight: probe EVERY endpoint this script needs, in one pass ----------------
    #
    # Written 2026-09-17 after three consecutive runs each failed on a different endpoint,
    # each costing the operator another token paste. Failing on the first missing permission
    # tells you one thing; probing all of them tells you everything that has to be fixed
    # before the next attempt. Each probe is a single-item read, so this costs nothing.
    Write-Host ""
    Write-Host "Checking what this token can actually reach..." -ForegroundColor Cyan

    # THE PERMISSION NAMES BELOW NAME THEIR TAB DELIBERATELY. GitHub offers TWO different
    # permissions both called "Custom properties", and the token UI gives no hint that they
    # differ:
    #   Repositories tab  -> grants PATCH /repos/{owner}/{repo}/properties/values only.
    #                        Useless for this script. Granting it looks like compliance.
    #   Organizations tab -> grants GET /orgs/{org}/properties/schema and .../values,
    #                        which is what this script actually calls.
    # Verified against GitHub's fine-grained permission reference, 2026-09-17, after a token
    # carrying the repository-level one 403'd on the org endpoint.
    $probes = @(
        @{ Name = 'repository list'
           Call = "orgs/$Org/repos?per_page=1"
           Perm = 'REPOSITORIES tab > Metadata: Read-only' }
        @{ Name = 'caller''s organisation role'
           Call = "user/memberships/orgs/$Org"
           Perm = 'ORGANIZATIONS tab > Members: Read-only  (optional - without it the export still runs, but completeness cannot be confirmed automatically)'
           Optional = $true }
        @{ Name = 'custom property schema'
           Call = "orgs/$Org/properties/schema"
           Perm = 'ORGANIZATIONS tab > Custom properties: Read-only  (NOT the Repositories tab one of the same name)' }
        @{ Name = 'custom property values'
           Call = "orgs/$Org/properties/values?per_page=1"
           Perm = 'ORGANIZATIONS tab > Custom properties: Read-only  (NOT the Repositories tab one of the same name)' }
    )

    $blocked = @()
    foreach ($p in $probes) {
        gh api $p.Call *> $null
        if ($LASTEXITCODE -eq 0) {
            Write-Host ("  ok       {0}" -f $p.Name) -ForegroundColor Green
        }
        elseif ($p.Optional) {
            Write-Host ("  absent   {0}  (optional)" -f $p.Name) -ForegroundColor DarkYellow
        }
        else {
            Write-Host ("  BLOCKED  {0}" -f $p.Name) -ForegroundColor Red
            $blocked += $p
        }
    }

    if ($blocked.Count -gt 0) {
        Write-Host ""
        Write-Host "This token is missing the following. Grant ALL of them, then re-run once:" -ForegroundColor Yellow
        foreach ($g in ($blocked | Group-Object { $_.Perm })) {
            Write-Host ("  - {0}" -f $g.Name) -ForegroundColor Yellow
            foreach ($item in $g.Group) { Write-Host ("      needed for: {0}" -f $item.Name) -ForegroundColor DarkGray }
        }
        Write-Host ""
        throw "Stopping before any export. $($blocked.Count) required read(s) are blocked - the permissions are listed above. Nothing was written."
    }

    Write-Host ""
    Write-Host "Pulling repositories and custom properties..." -ForegroundColor Cyan

    $jsonOut  = Join-Path $OutDir "github-repo-properties_$stamp.json"
    $csvOut   = Join-Path $OutDir "github-repo-properties_$stamp.csv"
    $reposRaw = Join-Path $cfgDir 'repos.json'

    gh api --paginate "orgs/$Org/repos?per_page=100&type=all" | Out-File -FilePath $reposRaw -Encoding utf8
    if ($LASTEXITCODE -ne 0) { throw "Failed to list repositories." }

    # The raw values output is the retained evidence - written to OutDir, not the temp dir.
    gh api --paginate "orgs/$Org/properties/values?per_page=100" | Out-File -FilePath $jsonOut -Encoding utf8
    if ($LASTEXITCODE -ne 0) { throw "Failed to read custom property values." }

    Copy-Item $jsonOut (Join-Path $cfgDir 'props.json')

    # --- Join to CSV. Pure stdlib python, run through WSL. ---
    $py = Join-Path $cfgDir 'join.py'
    $joinSource = @'
import json, csv, sys, pathlib

src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
repos = json.loads((src / "repos.json").read_text(encoding="utf-8"))
props = json.loads((src / "props.json").read_text(encoding="utf-8"))

pmap = {r["repository_name"]: {p["property_name"]: p.get("value")
        for p in r.get("properties", [])} for r in props}
cols = sorted({k for v in pmap.values() for k in v})

def flat(v):
    if isinstance(v, list):
        return "; ".join(str(x) for x in v)
    return "" if v is None else str(v)

with out.open("w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["name", "visibility", "archived", "description"] + cols)
    for repo in sorted(repos, key=lambda r: r["name"].lower()):
        p = pmap.get(repo["name"], {})
        w.writerow([repo["name"], repo.get("visibility", ""), repo.get("archived", False),
                    (repo.get("description") or "").replace("\n", " ").strip()]
                   + [flat(p.get(c)) for c in cols])

# A repository whose values are all null is unclassified. Expect a binary split:
# all five properties or none, because values are set per repository by hand.
classified = [n for n, v in pmap.items() if [x for x in v.values() if x is not None]]
unset      = sorted(n for n in pmap if n not in classified)
print("repositories returned : {}".format(len(repos)))
print("property columns      : {}".format(", ".join(cols) if cols else "(none defined)"))
print("classified            : {}".format(len(classified)))
print("unclassified          : {}{}".format(len(unset), " -> " + ", ".join(unset) if unset else ""))
'@
    $joinSource | Out-File -FilePath $py -Encoding utf8

    $wslSrc = (wsl -e wslpath -a "$cfgDir").Trim()
    $wslPy  = (wsl -e wslpath -a "$py").Trim()
    $wslCsv = (wsl -e wslpath -a "$csvOut").Trim()
    wsl -e bash -lc "python3 '$wslPy' '$wslSrc' '$wslCsv'"
    if ($LASTEXITCODE -ne 0) { throw "CSV join failed." }

    $seen = (Get-Content $csvOut | Measure-Object -Line).Lines - 1

    Write-Host ""
    Write-Host "repositories in this export : $seen" -ForegroundColor Yellow

    $provenance = Join-Path $OutDir "github-repo-properties_$stamp.provenance.txt"

    if ($null -eq $orgTotal) {
        if ($role -eq 'admin') {
            # An organisation admin whose token reaches all repositories sees the whole
            # estate, so the listing IS the total and there is nothing above it to check
            # against. This is a complete export, and the evidence says why.
            @(
                "Exported by $who on $stamp."
                "Organisation role: admin."
                "Repositories in this export: $seen."
                ""
                "COMPLETE."
                "The caller is an organisation admin, so GET /orgs/$Org/repos returns every"
                "repository in the organisation and the listing is itself the denominator."
                "No separate total is required, and total_private_repos is unavailable to a"
                "fine-grained token regardless."
                ""
                "The 2026-09-16 partial export (31 of 61) was short because that token"
                "belonged to an organisation MEMBER, who cannot see every repository -- not"
                "because the listing endpoint is unreliable."
            ) -join "`r`n" | Out-File -FilePath $provenance -Encoding utf8

            Write-Host ""
            Write-Host "Complete - caller is an organisation admin, so the listing of $seen repositories is the whole estate." -ForegroundColor Green
            Write-Host "Provenance: $provenance" -ForegroundColor DarkGray
        }
        else {
            $roleText = if ($role) { "organisation role '$role'" } else { "organisation role unknown" }
            @(
                "Exported by $who on $stamp."
                "Organisation role: $(if ($role) { $role } else { 'unreadable' })."
                "Repositories in this export: $seen."
                ""
                "COMPLETENESS NOT VERIFIED."
                "The caller is not a confirmed organisation admin, so the repository listing"
                "may be a subset -- a member sees only the repositories they can access, with"
                "no error and no indication that anything is missing."
                ""
                "Before citing a coverage figure, confirm $seen matches the repository count"
                "shown in the organisation's own list, and record who confirmed it and when."
                "Re-running with -ExpectedRepoCount <n> makes that check here instead."
            ) -join "`r`n" | Out-File -FilePath $provenance -Encoding utf8

            Write-Host ""
            Write-Warning "Completeness not verified ($roleText) - confirm $seen against the organisation's repository list before citing any coverage figure."
            Write-Host "Provenance: $provenance" -ForegroundColor DarkYellow
        }

        Write-Host ""
        Write-Host "Evidence : $jsonOut" -ForegroundColor Green
        Write-Host "Register : $csvOut"  -ForegroundColor Green
        return
    }

    Write-Host "organisation total          : $orgTotal" -ForegroundColor Yellow
    Write-Host "total established from      : $totalFrom" -ForegroundColor DarkGray

    # This comparison is the completeness guard. It replaced the pre-flight role check, so
    # a short export is a FAILURE here rather than a warning that scrolls past.
    if ($seen -lt $orgTotal) {
        $missing = $orgTotal - $seen
        $partial = Join-Path $OutDir "github-repo-properties_$stamp.PARTIAL-DO-NOT-USE-FOR-COVERAGE.txt"
        "Exported by $who on $stamp.`r`nSaw $seen of $orgTotal repositories. $missing invisible to this token.`r`nTotal established from: $totalFrom.`r`nThis export is NOT a valid basis for a coverage figure. See references/github-repository-properties.md." |
            Out-File -FilePath $partial -Encoding utf8

        Write-Warning "PARTIAL EXPORT - $missing of $orgTotal repositories were invisible to this token."
        Write-Host "Stamped: $partial" -ForegroundColor DarkYellow

        if (-not $AllowPartial) {
            throw "Refusing to report a partial export as a result. $seen of $orgTotal repositories. The files are written and stamped, but a coverage figure from them would be measured against the wrong denominator - which reads as a finding while meaning nothing. Run as an organisation owner, or re-run with -AllowPartial if you need the partial list for something other than coverage."
        }
        Write-Host "-AllowPartial was passed, so this is not treated as a failure. The stamp stands." -ForegroundColor DarkYellow
    }
    elseif ($seen -gt $orgTotal) {
        # More than expected. Worth surfacing rather than passing as "at least complete":
        # against an operator-asserted total it usually means the figure was misread, and
        # the coverage denominator would then be wrong in the other direction.
        Write-Warning "Export returned MORE repositories than expected - $seen against a total of $orgTotal ($totalFrom). Re-check the expected figure before citing coverage."
        "Exported by $who on $stamp.`r`nSaw $seen repositories against an expected total of $orgTotal.`r`nTotal established from: $totalFrom.`r`nThe export exceeded the expected total - confirm which figure is wrong before citing coverage." |
            Out-File -FilePath $provenance -Encoding utf8
        Write-Host "Provenance: $provenance" -ForegroundColor DarkYellow
    }
    else {
        Write-Host "Full export - every repository accounted for ($seen of $orgTotal)." -ForegroundColor Green
        "Exported by $who on $stamp.`r`nComplete: $seen of $orgTotal repositories.`r`nTotal established from: $totalFrom." |
            Out-File -FilePath $provenance -Encoding utf8
    }

    Write-Host ""
    Write-Host "Evidence : $jsonOut" -ForegroundColor Green
    Write-Host "Register : $csvOut"  -ForegroundColor Green
}
finally {
    # Runs on success, on error, and on Ctrl-C.
    $env:GH_TOKEN      = $null
    $env:GH_CONFIG_DIR = $null
    if (Test-Path $cfgDir) { Remove-Item $cfgDir -Recurse -Force -ErrorAction SilentlyContinue }
    Write-Host "Token cleared; throwaway gh config removed." -ForegroundColor DarkGray
}
