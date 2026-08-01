#requires -Version 5.1
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$TempParent = [System.IO.Path]::GetTempPath().TrimEnd('\')
$TempRoot = Join-Path $TempParent ("bravecow-harness-smoke-" + [guid]::NewGuid().ToString("N"))
$CodexHome = Join-Path $TempRoot ".codex"
$SharedSkillsHome = Join-Path $TempRoot ".agents\skills"
$OpenClawHome = Join-Path $TempRoot ".openclaw"
$Workspace = Join-Path $TempRoot "workspace"
$BackupRoot = Join-Path $TempRoot "backups"

try {
    New-Item -ItemType Directory -Path $TempRoot -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $CodexHome "memories") -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $CodexHome "memories\PROFILE.md") -Value "USER-SENTINEL" -Encoding UTF8
    $InitialAgents = "User preface.`r`n`r`n<!-- BraveCow Harness Codex: start -->`r`nold managed block`r`n<!-- BraveCow Harness Codex: end -->"
    Set-Content -LiteralPath (Join-Path $CodexHome "AGENTS.md") -Value $InitialAgents -Encoding UTF8

    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "install.ps1") `
        -CodexHome $CodexHome `
        -SharedSkillsHome $SharedSkillsHome `
        -OpenClawHome $OpenClawHome `
        -Workspace $Workspace `
        -UpdateRuntime `
        -ReplaceUserData `
        -DryRun `
        -SkipAudit `
        -NoWorkspaceAgents `
        -NoJunctions
    if ((Get-Content -LiteralPath (Join-Path $CodexHome "memories\PROFILE.md") -Raw -Encoding UTF8).Trim() -ne "USER-SENTINEL") {
        throw "Dry-run unexpectedly changed user memory."
    }

    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "install.ps1") `
        -CodexHome $CodexHome `
        -SharedSkillsHome $SharedSkillsHome `
        -OpenClawHome $OpenClawHome `
        -Workspace $Workspace `
        -UpdateRuntime `
        -MigrateConfig `
        -InitializeMemory `
        -BackupRoot $BackupRoot `
        -NoJunctions
    if ($LASTEXITCODE -ne 0) {
        throw "Installer exited with code $LASTEXITCODE"
    }

    $RequiredPaths = @(
        (Join-Path $CodexHome "harness\catalog\skill-inventory.json"),
        (Join-Path $CodexHome "harness\catalog\harness.lock.json"),
        (Join-Path $CodexHome "harness\catalog\skill-contracts.example.json"),
        (Join-Path $CodexHome "harness\catalog\verification.example.json"),
        (Join-Path $CodexHome "harness\catalog\upstream-observations.example.json"),
        (Join-Path $CodexHome "harness\scripts\memory_router.py"),
        (Join-Path $CodexHome "harness\scripts\lock_diff.py"),
        (Join-Path $CodexHome "harness\scripts\memory_write_gate.py"),
        (Join-Path $CodexHome "harness\scripts\skill_contracts.py"),
        (Join-Path $CodexHome "harness\scripts\export_runtime_snapshot.py"),
        (Join-Path $CodexHome "harness\scripts\measure_prompt_baseline.py"),
        (Join-Path $CodexHome "harness\reports\agent-harness-audit.md"),
        (Join-Path $CodexHome "harness\index\memory-fts.sqlite3"),
        (Join-Path $CodexHome "memories\MEMORY_POLICY.md"),
        (Join-Path $CodexHome "memories\SESSION_LOG.md"),
        (Join-Path $CodexHome "skills\agent-harness-introspect\SKILL.md"),
        (Join-Path $Workspace "AGENTS.md")
    )
    foreach ($Path in $RequiredPaths) {
        if (-not (Test-Path -LiteralPath $Path)) {
            throw "Missing smoke-test artifact: $Path"
        }
    }

    if ((Get-Content -LiteralPath (Join-Path $CodexHome "memories\PROFILE.md") -Raw -Encoding UTF8).Trim() -ne "USER-SENTINEL") {
        throw "Runtime/config update overwrote existing user memory."
    }
    $Agents = Get-Content -LiteralPath (Join-Path $CodexHome "AGENTS.md") -Raw -Encoding UTF8
    if ($Agents -notlike "*User preface.*" -or $Agents -like "*old managed block*" -or $Agents -notlike "*Memory retrieval:*") {
        throw "Managed AGENTS block migration failed or modified user content."
    }
    if (-not (Get-ChildItem -LiteralPath $BackupRoot -Recurse -File -ErrorAction SilentlyContinue)) {
        throw "Expected backup artifacts were not created for overwritten config."
    }

    $Inventory = Get-Content -LiteralPath (Join-Path $CodexHome "harness\catalog\skill-inventory.json") -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($null -eq $Inventory.plugin_summary -or $null -eq $Inventory.plugins) {
        throw "Plugin inventory fields were not generated."
    }
    $Lock = Get-Content -LiteralPath (Join-Path $CodexHome "harness\catalog\harness.lock.json") -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($Lock.schema_version -ne 2 -or $null -eq $Lock.skills -or $null -eq $Lock.components) {
        throw "Harness lock was not generated."
    }

    $Audit = Get-Content -LiteralPath (Join-Path $CodexHome "harness\reports\agent-harness-audit.md") -Raw -Encoding UTF8
    if ($Audit -notlike "*## Codex Plugin Cache*" -or $Audit -notlike "*SQLite FTS5 index*" -or $Audit -notlike "*Config runtime gate*" -or $Audit -notlike "*Durable-memory write gate*") {
        throw "Audit report is missing the updated sections."
    }

    Write-Host "OK: isolated install smoke test passed"
} finally {
    if (Test-Path -LiteralPath $TempRoot) {
        $ResolvedTempRoot = (Resolve-Path -LiteralPath $TempRoot).Path
        $ResolvedTempParent = (Resolve-Path -LiteralPath $TempParent).Path.TrimEnd('\')
        if ((Split-Path -Parent $ResolvedTempRoot) -ne $ResolvedTempParent -or (Split-Path -Leaf $ResolvedTempRoot) -notlike "bravecow-harness-smoke-*") {
            throw "Refusing to remove unexpected smoke-test path: $ResolvedTempRoot"
        }
        Remove-Item -LiteralPath $ResolvedTempRoot -Recurse -Force
    }
}
