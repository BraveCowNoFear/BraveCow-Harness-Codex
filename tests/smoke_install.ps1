#requires -Version 5.1
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$TempParent = [System.IO.Path]::GetTempPath().TrimEnd('\')
$TempRoot = Join-Path $TempParent ("bravecow-harness-smoke-" + [guid]::NewGuid().ToString("N"))
$BraveCowHome = Join-Path $TempRoot ".bravecow"
$CodexHome = Join-Path $TempRoot ".codex"
$ZCodeHome = Join-Path $TempRoot ".zcode"
$SharedSkillsHome = Join-Path $TempRoot ".agents\skills"
$OpenClawHome = Join-Path $TempRoot ".openclaw"
$Workspace = Join-Path $TempRoot "workspace"
$BackupRoot = Join-Path $TempRoot "backups"
$PreviousZCodeExecutable = $env:ZCODE_EXECUTABLE

try {
    New-Item -ItemType Directory -Path (Join-Path $BraveCowHome "memories") -Force | Out-Null
    $FakeZCode = Join-Path $TempRoot "ZCode.exe"
    Set-Content -LiteralPath $FakeZCode -Value "fake-zcode" -Encoding ASCII
    $env:ZCODE_EXECUTABLE = $FakeZCode
    Set-Content -LiteralPath (Join-Path $BraveCowHome "memories\PROFILE.md") -Value "USER-SENTINEL" -Encoding UTF8
    New-Item -ItemType Directory -Path $CodexHome -Force | Out-Null
    $InitialAgents = "User preface.`r`n`r`n<!-- BraveCow Harness Codex: start -->`r`nold managed block`r`n<!-- BraveCow Harness Codex: end -->"
    Set-Content -LiteralPath (Join-Path $CodexHome "AGENTS.md") -Value $InitialAgents -Encoding UTF8

    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "install.ps1") `
        -BraveCowHome $BraveCowHome -CodexHome $CodexHome -ZCodeHome $ZCodeHome `
        -SharedSkillsHome $SharedSkillsHome -OpenClawHome $OpenClawHome -Workspace $Workspace `
        -Targets All -UpdateRuntime -MigrateConfig -InitializeMemory -BackupRoot $BackupRoot `
        -NoJunctions -SkipOnboarding
    if ($LASTEXITCODE -ne 0) { throw "Installer exited with code $LASTEXITCODE" }

    $RequiredPaths = @(
        (Join-Path $BraveCowHome "harness\catalog\skill-inventory.json"),
        (Join-Path $BraveCowHome "harness\catalog\harness.lock.json"),
        (Join-Path $BraveCowHome "harness\reports\agent-harness-audit.md"),
        (Join-Path $BraveCowHome "harness\scripts\start_onboarding.py"),
        (Join-Path $BraveCowHome "harness\index\memory-fts.sqlite3"),
        (Join-Path $BraveCowHome "memories\MEMORY_POLICY.md"),
        (Join-Path $CodexHome "skills\bravecow-onboarding\SKILL.md"),
        (Join-Path $ZCodeHome "skills\bravecow-onboarding\SKILL.md"),
        (Join-Path $ZCodeHome "commands\bravecow-onboarding.md"),
        (Join-Path $CodexHome "AGENTS.md"),
        (Join-Path $ZCodeHome "AGENTS.md"),
        (Join-Path $Workspace "AGENTS.md")
    )
    foreach ($Path in $RequiredPaths) {
        if (-not (Test-Path -LiteralPath $Path)) { throw "Missing smoke-test artifact: $Path" }
    }

    if ((Get-Content -LiteralPath (Join-Path $BraveCowHome "memories\PROFILE.md") -Raw -Encoding UTF8).Trim() -ne "USER-SENTINEL") {
        throw "Runtime/config update overwrote existing user memory."
    }
    $Agents = Get-Content -LiteralPath (Join-Path $CodexHome "AGENTS.md") -Raw -Encoding UTF8
    if ($Agents -notlike "*User preface.*" -or $Agents -like "*old managed block*" -or $Agents -notlike "*~/.bravecow/memories*") {
        throw "Managed AGENTS block migration failed or modified user content."
    }
    if (-not (Get-ChildItem -LiteralPath $BackupRoot -Recurse -File -ErrorAction SilentlyContinue)) {
        throw "Expected backup artifacts were not created for overwritten config."
    }

    $Inventory = Get-Content -LiteralPath (Join-Path $BraveCowHome "harness\catalog\skill-inventory.json") -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($null -eq $Inventory.plugin_summary -or $null -eq $Inventory.plugins) { throw "Plugin inventory fields were not generated." }
    $Lock = Get-Content -LiteralPath (Join-Path $BraveCowHome "harness\catalog\harness.lock.json") -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($Lock.schema_version -ne 2 -or $null -eq $Lock.skills -or $null -eq $Lock.components) { throw "Harness lock was not generated." }
    if ($null -eq ($Lock.components | Where-Object { $_.id -eq "zcode-desktop" })) { throw "ZCode component was not inventoried." }

    $Audit = Get-Content -LiteralPath (Join-Path $BraveCowHome "harness\reports\agent-harness-audit.md") -Raw -Encoding UTF8
    if ($Audit -notlike "*ZCode*" -or $Audit -notlike "*Host OS*" -or $Audit -notlike "*SQLite FTS5 index*") {
        throw "Audit report is missing cross-runtime sections."
    }

    Write-Host "OK: isolated Windows Codex + ZCode install smoke test passed"
} finally {
    if ($null -eq $PreviousZCodeExecutable) { Remove-Item Env:ZCODE_EXECUTABLE -ErrorAction SilentlyContinue } else { $env:ZCODE_EXECUTABLE = $PreviousZCodeExecutable }
    if (Test-Path -LiteralPath $TempRoot) {
        $ResolvedTempRoot = (Resolve-Path -LiteralPath $TempRoot).Path
        $ResolvedTempParent = (Resolve-Path -LiteralPath $TempParent).Path.TrimEnd('\')
        if ((Split-Path -Parent $ResolvedTempRoot) -ne $ResolvedTempParent -or (Split-Path -Leaf $ResolvedTempRoot) -notlike "bravecow-harness-smoke-*") {
            throw "Refusing to remove unexpected smoke-test path: $ResolvedTempRoot"
        }
        Remove-Item -LiteralPath $ResolvedTempRoot -Recurse -Force
    }
}
