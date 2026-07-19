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

try {
    New-Item -ItemType Directory -Path $TempRoot -Force | Out-Null
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "install.ps1") `
        -CodexHome $CodexHome `
        -SharedSkillsHome $SharedSkillsHome `
        -OpenClawHome $OpenClawHome `
        -Workspace $Workspace `
        -NoJunctions
    if ($LASTEXITCODE -ne 0) {
        throw "Installer exited with code $LASTEXITCODE"
    }

    $RequiredPaths = @(
        (Join-Path $CodexHome "harness\catalog\skill-inventory.json"),
        (Join-Path $CodexHome "harness\reports\agent-harness-audit.md"),
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

    $Inventory = Get-Content -LiteralPath (Join-Path $CodexHome "harness\catalog\skill-inventory.json") -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($null -eq $Inventory.plugin_summary -or $null -eq $Inventory.plugins) {
        throw "Plugin inventory fields were not generated."
    }

    $Audit = Get-Content -LiteralPath (Join-Path $CodexHome "harness\reports\agent-harness-audit.md") -Raw -Encoding UTF8
    if ($Audit -notlike "*## Codex Plugin Cache*" -or $Audit -notlike "*MEMORY_POLICY.md*") {
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
