[CmdletBinding()]
param(
    [switch]$FetchRemote,
    [switch]$RunPythonCompile,
    [switch]$RunVerificationSuite
)

$ErrorActionPreference = 'Stop'
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$reportPath = Join-Path $env:TEMP "POL_TODO_PREFLIGHT-$timestamp.log"
New-Item -ItemType File -Path $reportPath -Force | Out-Null

function Write-Report {
    param([Parameter(Mandatory=$true)][string]$Text)
    $Text | Tee-Object -FilePath $reportPath -Append
}

function Invoke-LoggedCommand {
    param(
        [Parameter(Mandatory=$true)][string]$Label,
        [Parameter(Mandatory=$true)][string]$Executable,
        [Parameter(Mandatory=$true)][string[]]$Arguments
    )
    Write-Report "`n### $Label"
    Write-Report ("COMMAND: {0} {1}" -f $Executable, ($Arguments -join ' '))
    try {
        $output = & $Executable @Arguments 2>&1
        $code = $LASTEXITCODE
        if ($null -eq $code) { $code = 0 }
        foreach ($line in $output) { Write-Report ([string]$line) }
        Write-Report "EXIT_CODE: $code"
        return $code
    } catch {
        Write-Report ("ERROR: {0}" -f $_.Exception.Message)
        return 9001
    }
}

function Find-GitRoot {
    $dir = Get-Item -LiteralPath (Get-Location).Path
    while ($null -ne $dir) {
        if (Test-Path -LiteralPath (Join-Path $dir.FullName '.git')) { return $dir.FullName }
        $dir = $dir.Parent
    }
    return $null
}

Write-Report "POL-2.3 TODO preflight"
Write-Report ("Timestamp: {0}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'))
Write-Report "Safety: this script does not checkout branches, reset files, stash changes, commit, push, or write secrets."

$root = Find-GitRoot
if (-not $root) {
    Write-Report 'FATAL: current directory is not inside a Git worktree. Run this script from the POL-2.3 repository folder.'
    Write-Report ("Report: {0}" -f $reportPath)
    exit 2
}
Set-Location -LiteralPath $root
Write-Report ("Repository root: {0}" -f $root)

$remoteRaw = (& git remote get-url origin 2>$null | Select-Object -First 1)
if (-not $remoteRaw) {
    Write-Report 'FATAL: git remote origin is not configured.'
    exit 2
}
$remoteSafe = $remoteRaw -replace '(^\w+://)[^/@]+:[^/@]+@', '$1[REDACTED]@' -replace '(^\w+://)[^/@]+@', '$1[REDACTED]@'
Write-Report ("Origin: {0}" -f $remoteSafe)
$originMatches = $remoteRaw -match 'github\.com[:/]rrasi90/POL-2\.3(?:\.git)?(?:$|[?#])'
if (-not $originMatches) {
    Write-Report 'WARNING: origin does not match the expected rrasi90/POL-2.3 repository. Remote fetch is disabled for safety.'
}

$null = Invoke-LoggedCommand -Label 'Current branch' -Executable 'git' -Arguments @('branch','--show-current')
$null = Invoke-LoggedCommand -Label 'Current HEAD' -Executable 'git' -Arguments @('rev-parse','HEAD')
$null = Invoke-LoggedCommand -Label 'Working tree (preserve all changes)' -Executable 'git' -Arguments @('status','--short','--branch')
$null = Invoke-LoggedCommand -Label 'Recent commits' -Executable 'git' -Arguments @('log','-5','--oneline','--decorate')

Write-Report "`n### Remote reachability"
try {
    $remoteRefs = & git ls-remote origin HEAD refs/heads/main refs/heads/fix/audit-remediation-20261011 2>&1
    $rc = $LASTEXITCODE
    foreach ($line in $remoteRefs) { Write-Report ([string]$line) }
    Write-Report "EXIT_CODE: $rc"
    if ($rc -ne 0) { Write-Report 'REMOTE_STATUS: UNAVAILABLE_OR_AUTH_FAILED' }
} catch {
    Write-Report ('REMOTE_STATUS: ERROR - ' + $_.Exception.Message)
}

if ($FetchRemote) {
    Write-Report "`n### Fetch requested"
    if ($originMatches) {
        Write-Report 'Fetch updates remote-tracking refs only; it does not change the checked-out worktree or prune existing refs.'
        $null = Invoke-LoggedCommand -Label 'git fetch origin' -Executable 'git' -Arguments @('fetch','origin')
    } else {
        Write-Report 'SKIPPED: origin does not match the expected repository; no fetch was attempted.'
    }
}

Write-Report "`n### PR #30 status"
$gh = Get-Command gh -ErrorAction SilentlyContinue
if ($gh) {
    $null = Invoke-LoggedCommand -Label 'PR #30 metadata' -Executable 'gh' -Arguments @('pr','view','30','--repo','rrasi90/POL-2.3','--json','state,isDraft,mergedAt,headRefName,headRefOid,baseRefName,url')
    $null = Invoke-LoggedCommand -Label 'PR #30 checks' -Executable 'gh' -Arguments @('pr','checks','30','--repo','rrasi90/POL-2.3')
} else {
    try {
        $headers = @{ 'User-Agent'='POL-TODO-Preflight'; 'Accept'='application/vnd.github+json' }
        $pr = Invoke-RestMethod -Uri 'https://api.github.com/repos/rrasi90/POL-2.3/pulls/30' -Headers $headers -Method Get -TimeoutSec 15
        Write-Report ("PR_URL: {0}" -f $pr.html_url)
        Write-Report ("PR_STATE: {0}; MERGED: {1}; DRAFT: {2}" -f $pr.state, $pr.merged, $pr.draft)
        Write-Report ("PR_HEAD_BRANCH: {0}; PR_HEAD_SHA: {1}; BASE: {2}" -f $pr.head.ref, $pr.head.sha, $pr.base.ref)
        $checks = Invoke-RestMethod -Uri ("https://api.github.com/repos/rrasi90/POL-2.3/commits/{0}/check-runs" -f $pr.head.sha) -Headers $headers -Method Get -TimeoutSec 15
        Write-Report ("CHECK_RUN_COUNT: {0}" -f $checks.total_count)
        foreach ($check in $checks.check_runs) {
            Write-Report ("CHECK: {0} | {1} | {2} | {3}" -f $check.name, $check.status, $check.conclusion, $check.html_url)
        }
        if (-not $pr.merged -and $pr.state -eq 'open' -and $pr.head.sha) {
            Write-Report 'NEXT: Run the verification suite ONLY after the local checkout SHA has been confirmed to equal the intended PR head SHA, or after recording why a different SHA is intentionally under test.'
        }
    } catch {
        Write-Report ('PR_API_STATUS: UNAVAILABLE_OR_PRIVATE - ' + $_.Exception.Message)
        Write-Report 'If the repository is private, authenticate gh in this terminal or use the already-authorized GitHub connection available to the local coding agent. Do not paste tokens into logs or this file.'
    }
}

foreach ($rel in @('mvp/apps/web/package.json','mvp/apps/mobile/package.json')) {
    $path = Join-Path $root $rel
    Write-Report "`n### Package scripts: $rel"
    if (Test-Path -LiteralPath $path) {
        try {
            $pkg = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
            Write-Report ("Package: {0}; version: {1}" -f $pkg.name, $pkg.version)
            if ($pkg.scripts) {
                $pkg.scripts.PSObject.Properties | Sort-Object Name | ForEach-Object { Write-Report ("SCRIPT {0} = {1}" -f $_.Name, $_.Value) }
            } else { Write-Report 'No package scripts declared.' }
        } catch { Write-Report ("PACKAGE_JSON_ERROR: {0}" -f $_.Exception.Message) }
    } else { Write-Report 'NOT_PRESENT in this checkout.' }
}

if ($RunPythonCompile) {
    if (Test-Path -LiteralPath (Join-Path $root 'scripts')) {
        $null = Invoke-LoggedCommand -Label 'Python compileall scripts/' -Executable 'python' -Arguments @('-m','compileall','-q','scripts')
    } else { Write-Report 'SKIPPED: scripts/ directory not present.' }
}

if ($RunVerificationSuite) {
    $suite = Join-Path $root 'scripts/run_verification_suite.py'
    if (Test-Path -LiteralPath $suite) {
        Write-Report 'NOTICE: the full suite can mutate test databases and may require PostgreSQL 18 plus environment configuration. Verify DB target before proceeding.'
        $null = Invoke-LoggedCommand -Label 'Full verification suite (current checkout SHA)' -Executable 'python' -Arguments @('scripts/run_verification_suite.py')
        Write-Report 'IMPORTANT: associate the result with the exact HEAD SHA printed above. This runner does not mark TODO items complete.'
    } else { Write-Report 'SUITE_NOT_FOUND: scripts/run_verification_suite.py is absent from this checkout; use the canonical command named in TEST_VERIFICATION_MANIFEST.md.' }
}

Write-Report "`n### Runtime tooling availability"
foreach ($cmd in @('python','node','npm','java','adb','emulator')) {
    $found = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($found) { Write-Report ("{0}: {1}" -f $cmd, $found.Source) } else { Write-Report ("{0}: NOT_FOUND" -f $cmd) }
}
Write-Report "`nReport saved at: $reportPath"
Write-Report 'Next: review this report together with TODO_LIST.md, confirm the exact tested SHA and CI artifact, then continue with the first OPEN TODO whose dependencies are satisfied. This helper does not merge, checkout, reset, stash, commit, push, or modify credentials automatically.'