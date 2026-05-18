#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$CodexHome = (Join-Path $HOME ".codex"),
    [string]$SharedSkillsHome = (Join-Path $HOME ".agents\skills"),
    [string]$OpenClawHome = (Join-Path $HOME ".openclaw"),
    [string]$Workspace = (Get-Location).Path,
    [switch]$Force,
    [switch]$NoWorkspaceAgents,
    [switch]$NoJunctions,
    [switch]$SkipAudit
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$HarnessHome = Join-Path $CodexHome "harness"
$CodexSkillsHome = Join-Path $CodexHome "skills"
$MemoryHome = Join-Path $CodexHome "memories"
$AgentProfilesHome = Join-Path $CodexHome "agents"

function Ensure-Dir {
    param([Parameter(Mandatory = $true)][string]$Path)
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

function Copy-FileIfNeeded {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )
    Ensure-Dir (Split-Path -Parent $Destination)
    if ((Test-Path -LiteralPath $Destination) -and -not $Force) {
        Write-Host "Keep existing file: $Destination"
        return
    }
    Copy-Item -LiteralPath $Source -Destination $Destination -Force
    Write-Host "Wrote file: $Destination"
}

function Copy-Tree {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )
    Ensure-Dir $Destination
    if (-not (Test-Path -LiteralPath $Source)) {
        return
    }
    Get-ChildItem -LiteralPath $Source -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $Destination -Recurse -Force
    }
    Write-Host "Synced directory: $Destination"
}

function Add-AgentsSnippet {
    param([Parameter(Mandatory = $true)][string]$Destination)
    $snippetPath = Join-Path $RepoRoot "templates\AGENTS.snippet.md"
    $snippet = Get-Content -Raw -Encoding UTF8 $snippetPath
    Ensure-Dir (Split-Path -Parent $Destination)

    if (-not (Test-Path -LiteralPath $Destination)) {
        Set-Content -LiteralPath $Destination -Value $snippet -Encoding UTF8
        Write-Host "Created AGENTS.md: $Destination"
        return
    }

    $existing = Get-Content -Raw -Encoding UTF8 $Destination
    if ($existing -like "*BraveCow Harness Codex: start*") {
        Write-Host "AGENTS.md already contains BraveCow snippet: $Destination"
        return
    }

    Add-Content -LiteralPath $Destination -Value ("`r`n`r`n" + $snippet) -Encoding UTF8
    Write-Host "Appended BraveCow snippet to: $Destination"
}

Ensure-Dir $CodexHome
Ensure-Dir $HarnessHome
Ensure-Dir (Join-Path $HarnessHome "catalog")
Ensure-Dir (Join-Path $HarnessHome "reports")
Ensure-Dir (Join-Path $HarnessHome "vendor")
Ensure-Dir $CodexSkillsHome
Ensure-Dir $SharedSkillsHome
Ensure-Dir $MemoryHome
Ensure-Dir $AgentProfilesHome

Copy-FileIfNeeded (Join-Path $RepoRoot "harness\README.md") (Join-Path $HarnessHome "README.md")
Copy-Tree (Join-Path $RepoRoot "harness\scripts") (Join-Path $HarnessHome "scripts")
Copy-FileIfNeeded (Join-Path $RepoRoot "harness\catalog\import-backlog.example.json") (Join-Path $HarnessHome "catalog\import-backlog.example.json")
Copy-FileIfNeeded (Join-Path $RepoRoot "harness\catalog\external-round1.example.md") (Join-Path $HarnessHome "catalog\external-round1.example.md")

$sharedSkillSource = Join-Path $RepoRoot "skills\agent-harness-introspect"
$sharedSkillTarget = Join-Path $SharedSkillsHome "agent-harness-introspect"
Copy-Tree $sharedSkillSource $sharedSkillTarget

$codexSkillTarget = Join-Path $CodexSkillsHome "agent-harness-introspect"
if (Test-Path -LiteralPath $codexSkillTarget) {
    Write-Host "Keep existing Codex skill entry: $codexSkillTarget"
} elseif ($NoJunctions) {
    Copy-Tree $sharedSkillSource $codexSkillTarget
} else {
    try {
        New-Item -ItemType Junction -Path $codexSkillTarget -Target $sharedSkillTarget | Out-Null
        Write-Host "Created junction: $codexSkillTarget -> $sharedSkillTarget"
    } catch {
        Write-Warning "Junction failed, copying skill instead: $($_.Exception.Message)"
        Copy-Tree $sharedSkillSource $codexSkillTarget
    }
}

Get-ChildItem -LiteralPath (Join-Path $RepoRoot "templates\memories") -Filter "*.md" | ForEach-Object {
    Copy-FileIfNeeded $_.FullName (Join-Path $MemoryHome $_.Name)
}

Get-ChildItem -LiteralPath (Join-Path $RepoRoot "templates\agents") -Filter "*.toml" | ForEach-Object {
    Copy-FileIfNeeded $_.FullName (Join-Path $AgentProfilesHome $_.Name)
}

Add-AgentsSnippet (Join-Path $CodexHome "AGENTS.md")
if (-not $NoWorkspaceAgents -and $Workspace) {
    Ensure-Dir $Workspace
    Add-AgentsSnippet (Join-Path $Workspace "AGENTS.md")
}

if (-not $SkipAudit) {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $python) {
        Write-Warning "Python was not found. Skipping inventory and audit generation."
    } else {
        $oldCodexHome = $env:CODEX_HOME
        $oldSharedSkillsHome = $env:SHARED_SKILLS_HOME
        $oldOpenClawHome = $env:OPENCLAW_HOME
        try {
            $env:CODEX_HOME = $CodexHome
            $env:SHARED_SKILLS_HOME = $SharedSkillsHome
            $env:OPENCLAW_HOME = $OpenClawHome
            & $python.Source (Join-Path $HarnessHome "scripts\build_skill_inventory.py")
            if ($LASTEXITCODE -ne 0) { throw "Skill inventory failed." }
            & $python.Source (Join-Path $HarnessHome "scripts\harness_audit.py")
            if ($LASTEXITCODE -ne 0) { throw "Harness audit failed." }
        } finally {
            $env:CODEX_HOME = $oldCodexHome
            $env:SHARED_SKILLS_HOME = $oldSharedSkillsHome
            $env:OPENCLAW_HOME = $oldOpenClawHome
        }
    }
}

Write-Host ""
Write-Host "BraveCow Harness Codex installed."
Write-Host "Codex home: $CodexHome"
Write-Host "Shared skills: $SharedSkillsHome"
Write-Host "OpenClaw home: $OpenClawHome"
Write-Host "Harness audit: $(Join-Path $HarnessHome 'reports\agent-harness-audit.md')"
