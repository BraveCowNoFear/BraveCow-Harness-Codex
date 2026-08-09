#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$BraveCowHome = (Join-Path $HOME ".bravecow"),
    [string]$CodexHome = (Join-Path $HOME ".codex"),
    [string]$ZCodeHome = (Join-Path $HOME ".zcode"),
    [string]$SharedSkillsHome = (Join-Path $HOME ".agents\skills"),
    [string]$OpenClawHome = (Join-Path $HOME ".openclaw"),
    [string]$Workspace = (Get-Location).Path,
    [ValidateSet("All", "Codex", "ZCode")][string[]]$Targets = @("All"),
    [ValidateSet("auto", "Codex", "ZCode")][string]$OnboardingRuntime = "auto",
    [ValidateSet("auto", "zh-CN", "en")][string]$OnboardingLanguage = "auto",
    [int]$OnboardingTimeoutSeconds = 300,
    [switch]$SkipOnboarding,
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
$HarnessHome = Join-Path $BraveCowHome "harness"
$MemoryHome = Join-Path $BraveCowHome "memories"
$CodexSkillsHome = Join-Path $CodexHome "skills"
$ZCodeSkillsHome = Join-Path $ZCodeHome "skills"
$CodexAgentProfilesHome = Join-Path $CodexHome "agents"
$RunStamp = Get-Date -Format "yyyyMMdd-HHmmss"
$TargetSet = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::OrdinalIgnoreCase)
foreach ($target in $Targets) {
    if ($target -eq "All") {
        [void]$TargetSet.Add("Codex")
        [void]$TargetSet.Add("ZCode")
    } else {
        [void]$TargetSet.Add($target)
    }
}

if ($Force) {
    Write-Warning "-Force is deprecated. It maps to -UpdateRuntime -MigrateConfig and never replaces user memory."
    $UpdateRuntime = $true
    $MigrateConfig = $true
}
if ($ReplaceUserData) {
    $InitializeMemory = $true
}
$HasExplicitOperation = [bool]($UpdateRuntime -or $MigrateConfig -or $InitializeMemory -or $ReplaceUserData -or $Force)
if (-not $HasExplicitOperation) {
    $UpdateRuntime = $true
    $MigrateConfig = $true
    $InitializeMemory = $true
}
if (-not $BackupRoot) {
    $BackupRoot = Join-Path $HarnessHome ("backups\" + $RunStamp)
}

function Write-Plan {
    param([Parameter(Mandatory = $true)][string]$Message)
    if ($DryRun) { Write-Host "DRY-RUN: $Message" } else { Write-Host $Message }
}

function Ensure-Dir {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (Test-Path -LiteralPath $Path) { return }
    if ($DryRun) { Write-Plan "Create directory: $Path"; return }
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

function Get-ContentHash {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
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
    if (-not (Test-Path -LiteralPath $Destination -PathType Leaf)) { return }
    $backup = Get-BackupPath $Destination
    if ($DryRun) { Write-Plan "Backup file: $Destination -> $backup"; return }
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
    if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) { throw "Missing source file: $Source" }
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
    if ($exists) { Backup-File $Destination }
    if ($DryRun) { Write-Plan "Write [$Category]: $Destination"; return }
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
    if (-not (Test-Path -LiteralPath $Source -PathType Container)) { return }
    Ensure-Dir $Destination
    $sourceRoot = [System.IO.Path]::GetFullPath($Source).TrimEnd("\", "/")
    Get-ChildItem -LiteralPath $Source -Recurse -File -Force |
        Where-Object { $_.Name -notlike "*.pyc" -and $_.FullName -notlike "*\__pycache__\*" } |
        ForEach-Object {
            $relative = $_.FullName.Substring($sourceRoot.Length).TrimStart("\", "/")
            Copy-ManagedFile $_.FullName (Join-Path $Destination $relative) $AllowOverwrite $Category
        }
}

function Ensure-DirectoryAlias {
    param(
        [Parameter(Mandatory = $true)][string]$Alias,
        [Parameter(Mandatory = $true)][string]$Target,
        [string]$Category = "runtime-link"
    )
    if (Test-Path -LiteralPath $Alias) {
        $item = Get-Item -LiteralPath $Alias -Force
        if ($item.LinkType -in @("Junction", "SymbolicLink")) {
            Write-Host "Keep existing [$Category]: $Alias"
        } else {
            Write-Warning "Existing directory is not replaced [$Category]: $Alias"
        }
        return
    }
    Ensure-Dir (Split-Path -Parent $Alias)
    if ($NoJunctions) {
        Write-Host "Skip directory link because -NoJunctions is set: $Alias"
        return
    }
    if ($DryRun) { Write-Plan "Create junction: $Alias -> $Target"; return }
    New-Item -ItemType Junction -Path $Alias -Target $Target | Out-Null
    Write-Host "Created junction: $Alias -> $Target"
}

function Ensure-NeutralRoot {
    param(
        [Parameter(Mandatory = $true)][string]$NeutralPath,
        [Parameter(Mandatory = $true)][string]$LegacyPath,
        [Parameter(Mandatory = $true)][string]$Category
    )
    if (Test-Path -LiteralPath $NeutralPath) { return }
    Ensure-Dir (Split-Path -Parent $NeutralPath)
    if ((Test-Path -LiteralPath $LegacyPath -PathType Container) -and -not $NoJunctions) {
        if ($DryRun) { Write-Plan "Create neutral junction [$Category]: $NeutralPath -> $LegacyPath"; return }
        New-Item -ItemType Junction -Path $NeutralPath -Target $LegacyPath | Out-Null
        Write-Host "Adopted existing Codex data through neutral path [$Category]: $NeutralPath"
        return
    }
    Ensure-Dir $NeutralPath
    if (Test-Path -LiteralPath $LegacyPath -PathType Container) {
        Copy-ManagedTree $LegacyPath $NeutralPath $false "legacy-$Category"
    }
}

function Ensure-SkillRuntimeEntry {
    param(
        [Parameter(Mandatory = $true)][string]$SkillName,
        [Parameter(Mandatory = $true)][string]$SharedSkillTarget,
        [Parameter(Mandatory = $true)][string]$RuntimeSkillsHome
    )
    $target = Join-Path $RuntimeSkillsHome $SkillName
    if (Test-Path -LiteralPath $target) {
        $item = Get-Item -LiteralPath $target -Force
        if ($item.LinkType -in @("Junction", "SymbolicLink")) {
            Write-Host "Keep existing runtime skill link: $target"
        } elseif ($UpdateRuntime) {
            Copy-ManagedTree $SharedSkillTarget $target $true "runtime"
        } else {
            Write-Host "Keep existing runtime skill: $target"
        }
        return
    }
    Ensure-Dir $RuntimeSkillsHome
    if ($NoJunctions) {
        Copy-ManagedTree $SharedSkillTarget $target $true "runtime"
    } elseif ($DryRun) {
        Write-Plan "Create junction: $target -> $SharedSkillTarget"
    } else {
        try {
            New-Item -ItemType Junction -Path $target -Target $SharedSkillTarget | Out-Null
            Write-Host "Created junction: $target -> $SharedSkillTarget"
        } catch {
            Write-Warning "Junction failed, copying skill instead: $($_.Exception.Message)"
            Copy-ManagedTree $SharedSkillTarget $target $true "runtime"
        }
    }
}

function Update-AgentsSnippet {
    param([Parameter(Mandatory = $true)][string]$Destination)
    $snippetPath = Join-Path $RepoRoot "templates\AGENTS.snippet.md"
    $snippet = Get-Content -Raw -Encoding UTF8 $snippetPath
    Ensure-Dir (Split-Path -Parent $Destination)
    if (-not (Test-Path -LiteralPath $Destination -PathType Leaf)) {
        if ($DryRun) { Write-Plan "Create AGENTS.md: $Destination" } else {
            Set-Content -LiteralPath $Destination -Value $snippet -Encoding UTF8
            Write-Host "Created AGENTS.md: $Destination"
        }
        return
    }
    $existing = Get-Content -Raw -Encoding UTF8 $Destination
    $startMarker = "<!-- BraveCow Harness: start -->"
    $endMarker = "<!-- BraveCow Harness: end -->"
    $legacyStart = "<!-- BraveCow Harness Codex: start -->"
    $legacyEnd = "<!-- BraveCow Harness Codex: end -->"
    $updated = $existing
    if ($existing.Contains($startMarker) -and $existing.Contains($endMarker)) {
        $pattern = "(?s)" + [regex]::Escape($startMarker) + ".*?" + [regex]::Escape($endMarker)
        $updated = [regex]::Replace($existing, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($match) $snippet }, 1)
    } elseif ($existing.Contains($legacyStart) -and $existing.Contains($legacyEnd)) {
        $pattern = "(?s)" + [regex]::Escape($legacyStart) + ".*?" + [regex]::Escape($legacyEnd)
        $updated = [regex]::Replace($existing, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($match) $snippet }, 1)
    } else {
        $updated = $existing.TrimEnd() + "`r`n`r`n" + $snippet
    }
    if ($updated -eq $existing) { Write-Host "Up to date [config]: $Destination"; return }
    Backup-File $Destination
    if ($DryRun) { Write-Plan "Update managed AGENTS.md block: $Destination" } else {
        Set-Content -LiteralPath $Destination -Value $updated -Encoding UTF8
        Write-Host "Updated managed AGENTS.md block: $Destination"
    }
}

function Resolve-OnboardingRuntime {
    if ($OnboardingRuntime -ne "auto") { return $OnboardingRuntime }
    if ($env:BRAVECOW_CALLER_RUNTIME -match "^(?i)zcode$") { return "ZCode" }
    if ($env:BRAVECOW_CALLER_RUNTIME -match "^(?i)codex$") { return "Codex" }
    if ($TargetSet.Count -eq 1) { return @($TargetSet)[0] }
    try {
        $pidCursor = $PID
        for ($index = 0; $index -lt 8 -and $pidCursor; $index++) {
            $process = Get-CimInstance Win32_Process -Filter "ProcessId = $pidCursor" -ErrorAction Stop
            $name = [string]$process.Name
            if ($name -match "(?i)zcode") { return "ZCode" }
            if ($name -match "(?i)codex|chatgpt") { return "Codex" }
            $pidCursor = [int]$process.ParentProcessId
        }
    } catch { }
    if (Get-Command codex -ErrorAction SilentlyContinue) { return "Codex" }
    return "ZCode"
}

Ensure-NeutralRoot $HarnessHome (Join-Path $CodexHome "harness") "harness"
Ensure-NeutralRoot $MemoryHome (Join-Path $CodexHome "memories") "memory"
foreach ($path in @($BraveCowHome, $HarnessHome, (Join-Path $HarnessHome "catalog"), (Join-Path $HarnessHome "reports"), (Join-Path $HarnessHome "vendor"), (Join-Path $HarnessHome "onboarding"), $MemoryHome, $SharedSkillsHome)) {
    Ensure-Dir $path
}

Copy-ManagedFile (Join-Path $RepoRoot "harness\README.md") (Join-Path $HarnessHome "README.md") ([bool]$UpdateRuntime) "runtime"
Copy-ManagedTree (Join-Path $RepoRoot "harness\scripts") (Join-Path $HarnessHome "scripts") ([bool]$UpdateRuntime) "runtime"
Get-ChildItem -LiteralPath (Join-Path $RepoRoot "harness\catalog") -Filter "*.example.*" -File | ForEach-Object {
    Copy-ManagedFile $_.FullName (Join-Path $HarnessHome ("catalog\" + $_.Name)) ([bool]$UpdateRuntime) "runtime"
}

Get-ChildItem -LiteralPath (Join-Path $RepoRoot "skills") -Directory | ForEach-Object {
    $sharedTarget = Join-Path $SharedSkillsHome $_.Name
    Copy-ManagedTree $_.FullName $sharedTarget ([bool]$UpdateRuntime) "runtime"
    if ($TargetSet.Contains("Codex")) { Ensure-SkillRuntimeEntry $_.Name $sharedTarget $CodexSkillsHome }
    if ($TargetSet.Contains("ZCode")) { Ensure-SkillRuntimeEntry $_.Name $sharedTarget $ZCodeSkillsHome }
}

Get-ChildItem -LiteralPath (Join-Path $RepoRoot "templates\memories") -Filter "*.md" | ForEach-Object {
    $destination = Join-Path $MemoryHome $_.Name
    if ((Test-Path -LiteralPath $destination -PathType Leaf) -or $InitializeMemory) {
        Copy-ManagedFile $_.FullName $destination ([bool]$ReplaceUserData) "memory"
    } else {
        Write-Host "Skip missing memory (use -InitializeMemory): $destination"
    }
}

if ($TargetSet.Contains("Codex")) {
    Ensure-Dir $CodexHome
    Ensure-DirectoryAlias (Join-Path $CodexHome "harness") $HarnessHome
    Ensure-DirectoryAlias (Join-Path $CodexHome "memories") $MemoryHome
    Ensure-Dir $CodexAgentProfilesHome
    Get-ChildItem -LiteralPath (Join-Path $RepoRoot "templates\agents") -Filter "*.toml" | ForEach-Object {
        Copy-ManagedFile $_.FullName (Join-Path $CodexAgentProfilesHome $_.Name) ([bool]$MigrateConfig) "config"
    }
    Update-AgentsSnippet (Join-Path $CodexHome "AGENTS.md")
}
if ($TargetSet.Contains("ZCode")) {
    Ensure-Dir $ZCodeHome
    Ensure-DirectoryAlias (Join-Path $ZCodeHome "harness") $HarnessHome
    Ensure-DirectoryAlias (Join-Path $ZCodeHome "memories") $MemoryHome
    Ensure-Dir (Join-Path $ZCodeHome "commands")
    Copy-ManagedFile (Join-Path $RepoRoot "templates\zcode\commands\bravecow-onboarding.md") (Join-Path $ZCodeHome "commands\bravecow-onboarding.md") $true "zcode-command"
    Update-AgentsSnippet (Join-Path $ZCodeHome "AGENTS.md")
}
if (-not $NoWorkspaceAgents -and $Workspace) {
    Ensure-Dir $Workspace
    Update-AgentsSnippet (Join-Path $Workspace "AGENTS.md")
}

if (-not $SkipAudit -and -not $DryRun) {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $python) { $python = Get-Command python3 -ErrorAction SilentlyContinue }
    if ($null -eq $python) {
        Write-Warning "Python was not found. Skipping inventory and audit generation."
    } else {
        $saved = @{
            BRAVECOW_HOME = $env:BRAVECOW_HOME; BRAVECOW_HARNESS_HOME = $env:BRAVECOW_HARNESS_HOME
            BRAVECOW_MEMORY_HOME = $env:BRAVECOW_MEMORY_HOME; CODEX_HOME = $env:CODEX_HOME
            ZCODE_HOME = $env:ZCODE_HOME; SHARED_SKILLS_HOME = $env:SHARED_SKILLS_HOME; OPENCLAW_HOME = $env:OPENCLAW_HOME
        }
        try {
            $env:BRAVECOW_HOME = $BraveCowHome
            $env:BRAVECOW_HARNESS_HOME = $HarnessHome
            $env:BRAVECOW_MEMORY_HOME = $MemoryHome
            $env:CODEX_HOME = $CodexHome
            $env:ZCODE_HOME = $ZCodeHome
            $env:SHARED_SKILLS_HOME = $SharedSkillsHome
            $env:OPENCLAW_HOME = $OpenClawHome
            & $python.Source (Join-Path $HarnessHome "scripts\build_skill_inventory.py")
            if ($LASTEXITCODE -ne 0) { throw "Skill inventory failed." }
            & $python.Source (Join-Path $HarnessHome "scripts\harness_audit.py")
            if ($LASTEXITCODE -ne 0) { throw "Harness audit failed." }
        } finally {
            foreach ($key in $saved.Keys) { Set-Item -Path ("Env:" + $key) -Value $saved[$key] }
        }
    }
}

$resolvedOnboardingRuntime = Resolve-OnboardingRuntime
if ($SkipOnboarding) {
    Write-Host "Onboarding: skipped by -SkipOnboarding"
} elseif ($DryRun) {
    Write-Plan "Create a new $resolvedOnboardingRuntime task and start the 12-lesson BraveCow onboarding course"
} elseif (-not $TargetSet.Contains($resolvedOnboardingRuntime)) {
    Write-Warning "Onboarding runtime $resolvedOnboardingRuntime was not installed; skipping task launch."
} else {
    $launcher = Join-Path $HarnessHome "scripts\start_onboarding.ps1"
    & powershell -NoProfile -ExecutionPolicy Bypass -File $launcher `
        -Runtime $resolvedOnboardingRuntime `
        -Workspace $Workspace `
        -SkillPath (Join-Path $SharedSkillsHome "bravecow-onboarding\SKILL.md") `
        -ReceiptPath (Join-Path $HarnessHome "onboarding\last-launch.json") `
        -Language $OnboardingLanguage `
        -TimeoutSeconds $OnboardingTimeoutSeconds
    if ($LASTEXITCODE -ne 0) { throw "Harness installed, but automatic onboarding task launch failed." }
}

Write-Host ""
Write-Host "BraveCow Harness install/update completed."
Write-Host "Shared home: $BraveCowHome"
Write-Host "Targets: $([string]::Join(', ', @($TargetSet)))"
Write-Host "Shared skills: $SharedSkillsHome"
Write-Host "Runtime update: $([bool]$UpdateRuntime)"
Write-Host "Config migration: $([bool]$MigrateConfig)"
Write-Host "Initialize missing memory: $([bool]$InitializeMemory)"
Write-Host "User data replacement: $([bool]$ReplaceUserData)"
if ($DryRun) {
    Write-Host "Mode: dry-run (no files or tasks changed)"
} else {
    Write-Host "Backup root (used only for overwritten files): $BackupRoot"
    if ($SkipAudit) { Write-Host "Harness audit: skipped" } else { Write-Host "Harness audit: $(Join-Path $HarnessHome 'reports\agent-harness-audit.md')" }
}
