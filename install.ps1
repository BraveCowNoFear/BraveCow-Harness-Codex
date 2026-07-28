#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$CodexHome = (Join-Path $HOME ".codex"),
    [string]$SharedSkillsHome = (Join-Path $HOME ".agents\skills"),
    [string]$OpenClawHome = (Join-Path $HOME ".openclaw"),
    [string]$Workspace = (Get-Location).Path,
    [switch]$UpdateRuntime,
    [switch]$MigrateConfig,
    [switch]$InitializeMemory,
    [switch]$ReplaceUserData,
    [switch]$DryRun,
    [string]$BackupRoot,
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
$RunStamp = Get-Date -Format "yyyyMMdd-HHmmss"

if ($Force) {
    Write-Warning "-Force is deprecated. It now maps to -UpdateRuntime -MigrateConfig and never replaces memory/user data."
    $UpdateRuntime = $true
    $MigrateConfig = $true
}
if ($ReplaceUserData) {
    $InitializeMemory = $true
}
$HasExplicitOperation = [bool]($UpdateRuntime -or $MigrateConfig -or $InitializeMemory -or $ReplaceUserData -or $Force)
if (-not $HasExplicitOperation) {
    $InitializeMemory = $true
}
if (-not $BackupRoot) {
    $BackupRoot = Join-Path $HarnessHome ("backups\" + $RunStamp)
}

function Write-Plan {
    param([Parameter(Mandatory = $true)][string]$Message)
    if ($DryRun) {
        Write-Host "DRY-RUN: $Message"
    } else {
        Write-Host $Message
    }
}

function Ensure-Dir {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (Test-Path -LiteralPath $Path) {
        return
    }
    if ($DryRun) {
        Write-Plan "Create directory: $Path"
        return
    }
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

function Get-ContentHash {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
}

function Get-BackupPath {
    param([Parameter(Mandatory = $true)][string]$Destination)
    $full = [System.IO.Path]::GetFullPath($Destination)
    $safe = $full.Replace(":", "").TrimStart("\", "/")
    return Join-Path $BackupRoot $safe
}

function Backup-File {
    param([Parameter(Mandatory = $true)][string]$Destination)
    if (-not (Test-Path -LiteralPath $Destination -PathType Leaf)) {
        return
    }
    $backup = Get-BackupPath $Destination
    if ($DryRun) {
        Write-Plan "Backup file: $Destination -> $backup"
        return
    }
    Ensure-Dir (Split-Path -Parent $backup)
    Copy-Item -LiteralPath $Destination -Destination $backup -Force
}

function Copy-ManagedFile {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination,
        [Parameter(Mandatory = $true)][bool]$AllowOverwrite,
        [Parameter(Mandatory = $true)][string]$Category
    )
    if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
        throw "Missing source file: $Source"
    }

    $exists = Test-Path -LiteralPath $Destination -PathType Leaf
    if ($exists -and (Get-ContentHash $Source) -eq (Get-ContentHash $Destination)) {
        Write-Host "Up to date [$Category]: $Destination"
        return
    }
    if ($exists -and -not $AllowOverwrite) {
        Write-Host "Keep existing [$Category]: $Destination"
        return
    }

    Ensure-Dir (Split-Path -Parent $Destination)
    if ($exists) {
        Backup-File $Destination
    }
    if ($DryRun) {
        Write-Plan "Write [$Category]: $Destination"
        return
    }
    Copy-Item -LiteralPath $Source -Destination $Destination -Force
    Write-Host "Wrote [$Category]: $Destination"
}

function Copy-ManagedTree {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination,
        [Parameter(Mandatory = $true)][bool]$AllowOverwrite,
        [Parameter(Mandatory = $true)][string]$Category
    )
    if (-not (Test-Path -LiteralPath $Source -PathType Container)) {
        return
    }
    Ensure-Dir $Destination
    $sourceRoot = [System.IO.Path]::GetFullPath($Source).TrimEnd("\", "/")
    Get-ChildItem -LiteralPath $Source -Recurse -File -Force |
        Where-Object { $_.Name -notlike "*.pyc" -and $_.FullName -notlike "*\__pycache__\*" } |
        ForEach-Object {
            $relative = $_.FullName.Substring($sourceRoot.Length).TrimStart("\", "/")
            Copy-ManagedFile $_.FullName (Join-Path $Destination $relative) $AllowOverwrite $Category
        }
}

function Update-AgentsSnippet {
    param([Parameter(Mandatory = $true)][string]$Destination)
    $snippetPath = Join-Path $RepoRoot "templates\AGENTS.snippet.md"
    $snippet = Get-Content -Raw -Encoding UTF8 $snippetPath
    Ensure-Dir (Split-Path -Parent $Destination)

    if (-not (Test-Path -LiteralPath $Destination -PathType Leaf)) {
        if ($DryRun) {
            Write-Plan "Create AGENTS.md: $Destination"
        } else {
            Set-Content -LiteralPath $Destination -Value $snippet -Encoding UTF8
            Write-Host "Created AGENTS.md: $Destination"
        }
        return
    }

    $existing = Get-Content -Raw -Encoding UTF8 $Destination
    $startMarker = "<!-- BraveCow Harness Codex: start -->"
    $endMarker = "<!-- BraveCow Harness Codex: end -->"
    $hasManagedBlock = $existing.Contains($startMarker) -and $existing.Contains($endMarker)

    if (-not $MigrateConfig) {
        Write-Host "Keep existing AGENTS.md (use -MigrateConfig to update the managed block): $Destination"
        return
    }

    if ($hasManagedBlock) {
        $pattern = "(?s)" + [regex]::Escape($startMarker) + ".*?" + [regex]::Escape($endMarker)
        $updated = [regex]::Replace($existing, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($match) $snippet }, 1)
    } else {
        $updated = $existing.TrimEnd() + "`r`n`r`n" + $snippet
    }

    if ($updated -eq $existing) {
        Write-Host "Up to date [config]: $Destination"
        return
    }
    Backup-File $Destination
    if ($DryRun) {
        Write-Plan "Update managed AGENTS.md block: $Destination"
    } else {
        Set-Content -LiteralPath $Destination -Value $updated -Encoding UTF8
        Write-Host "Updated managed AGENTS.md block: $Destination"
    }
}

foreach ($path in @($CodexHome, $HarnessHome, (Join-Path $HarnessHome "catalog"), (Join-Path $HarnessHome "reports"), (Join-Path $HarnessHome "vendor"), $CodexSkillsHome, $SharedSkillsHome, $MemoryHome, $AgentProfilesHome)) {
    Ensure-Dir $path
}

Copy-ManagedFile (Join-Path $RepoRoot "harness\README.md") (Join-Path $HarnessHome "README.md") ([bool]$UpdateRuntime) "runtime"
Copy-ManagedTree (Join-Path $RepoRoot "harness\scripts") (Join-Path $HarnessHome "scripts") ([bool]$UpdateRuntime) "runtime"
Copy-ManagedFile (Join-Path $RepoRoot "harness\catalog\import-backlog.example.json") (Join-Path $HarnessHome "catalog\import-backlog.example.json") ([bool]$UpdateRuntime) "runtime"
Copy-ManagedFile (Join-Path $RepoRoot "harness\catalog\external-round1.example.md") (Join-Path $HarnessHome "catalog\external-round1.example.md") ([bool]$UpdateRuntime) "runtime"

$sharedSkillSource = Join-Path $RepoRoot "skills\agent-harness-introspect"
$sharedSkillTarget = Join-Path $SharedSkillsHome "agent-harness-introspect"
Copy-ManagedTree $sharedSkillSource $sharedSkillTarget ([bool]$UpdateRuntime) "runtime"

$codexSkillTarget = Join-Path $CodexSkillsHome "agent-harness-introspect"
if (Test-Path -LiteralPath $codexSkillTarget) {
    $item = Get-Item -LiteralPath $codexSkillTarget -Force
    if ($item.LinkType -eq "Junction" -or $item.LinkType -eq "SymbolicLink") {
        Write-Host "Keep existing Codex skill link: $codexSkillTarget"
    } elseif ($UpdateRuntime) {
        Copy-ManagedTree $sharedSkillSource $codexSkillTarget $true "runtime"
    } else {
        Write-Host "Keep existing Codex skill entry: $codexSkillTarget"
    }
} elseif ($NoJunctions) {
    Copy-ManagedTree $sharedSkillSource $codexSkillTarget $true "runtime"
} elseif ($DryRun) {
    Write-Plan "Create junction: $codexSkillTarget -> $sharedSkillTarget"
} else {
    try {
        New-Item -ItemType Junction -Path $codexSkillTarget -Target $sharedSkillTarget | Out-Null
        Write-Host "Created junction: $codexSkillTarget -> $sharedSkillTarget"
    } catch {
        Write-Warning "Junction failed, copying skill instead: $($_.Exception.Message)"
        Copy-ManagedTree $sharedSkillSource $codexSkillTarget $true "runtime"
    }
}

Get-ChildItem -LiteralPath (Join-Path $RepoRoot "templates\memories") -Filter "*.md" | ForEach-Object {
    $destination = Join-Path $MemoryHome $_.Name
    if ((Test-Path -LiteralPath $destination -PathType Leaf) -or $InitializeMemory) {
        Copy-ManagedFile $_.FullName $destination ([bool]$ReplaceUserData) "memory"
    } else {
        Write-Host "Skip missing memory (use -InitializeMemory): $destination"
    }
}

Get-ChildItem -LiteralPath (Join-Path $RepoRoot "templates\agents") -Filter "*.toml" | ForEach-Object {
    Copy-ManagedFile $_.FullName (Join-Path $AgentProfilesHome $_.Name) ([bool]$MigrateConfig) "config"
}

Update-AgentsSnippet (Join-Path $CodexHome "AGENTS.md")
if (-not $NoWorkspaceAgents -and $Workspace) {
    Ensure-Dir $Workspace
    Update-AgentsSnippet (Join-Path $Workspace "AGENTS.md")
}

if (-not $SkipAudit -and -not $DryRun) {
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
Write-Host "BraveCow Harness Codex install/update completed."
Write-Host "Codex home: $CodexHome"
Write-Host "Shared skills: $SharedSkillsHome"
Write-Host "Runtime update: $([bool]$UpdateRuntime)"
Write-Host "Config migration: $([bool]$MigrateConfig)"
Write-Host "Initialize missing memory: $([bool]$InitializeMemory)"
Write-Host "User data replacement: $([bool]$ReplaceUserData)"
if ($DryRun) {
    Write-Host "Mode: dry-run (no files changed)"
} else {
    Write-Host "Backup root (used only for overwritten files): $BackupRoot"
    Write-Host "Harness audit: $(Join-Path $HarnessHome 'reports\agent-harness-audit.md')"
}
