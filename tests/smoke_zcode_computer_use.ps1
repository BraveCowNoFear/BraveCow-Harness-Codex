#requires -Version 5.1
[CmdletBinding()]
param([switch]$KeepArtifacts)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$TempParent = [System.IO.Path]::GetTempPath().TrimEnd("\")
$TempRoot = Join-Path $TempParent ("bravecow-zcode-computer-use-" + [guid]::NewGuid().ToString("N"))

try {
    New-Item -ItemType Directory -Path $TempRoot -Force | Out-Null
    $BraveCowHome = Join-Path $TempRoot ".bravecow"
    $ZCodeHome = Join-Path $TempRoot ".zcode"
    $SharedSkillsHome = Join-Path $TempRoot ".agents\skills"
    $LocalSource = Join-Path (Split-Path -Parent $RepoRoot) "desktop-control-for-windows"
    $SourceArguments = @()
    if (Test-Path -LiteralPath (Join-Path $LocalSource ".git") -PathType Container) {
        $SourceArguments = @("-ZCodeComputerUseSource", $LocalSource)
    }

    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "install.ps1") `
        -BraveCowHome $BraveCowHome `
        -CodexHome (Join-Path $TempRoot ".codex") `
        -ZCodeHome $ZCodeHome `
        -SharedSkillsHome $SharedSkillsHome `
        -Workspace (Join-Path $TempRoot "workspace") `
        -Targets ZCode -UpdateRuntime -MigrateConfig -InitializeMemory `
        -NoJunctions -NoWorkspaceAgents -SkipAudit -SkipOnboarding @SourceArguments
    if ($LASTEXITCODE -ne 0) { throw "Installer exited with code $LASTEXITCODE" }

    $SkillPath = Join-Path $ZCodeHome "skills\bravecow-windows-computer-use"
    $VenvPython = Join-Path $SkillPath ".venv\Scripts\python.exe"
    $Controller = Join-Path $SkillPath "scripts\ui_control.py"
    $ReceiptPath = Join-Path $BraveCowHome "harness\catalog\zcode-computer-use-install.json"
    foreach ($Path in @($VenvPython, $Controller, $ReceiptPath)) {
        if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Missing E2E artifact: $Path" }
    }

    & $VenvPython $Controller --help | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Controller help verification failed." }
    & $VenvPython $Controller status --windows | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Read-only controller status verification failed." }

    $Receipt = Get-Content -LiteralPath $ReceiptPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($Receipt.status -ne "installed") { throw "Install receipt did not report installed." }
    if ($Receipt.commit -notmatch "^[0-9a-f]{40}$") { throw "Install receipt has an invalid commit." }
    Write-Host "OK: Windows ZCode Computer Use install and read-only controller verification passed"
} finally {
    if ($KeepArtifacts) {
        Write-Host "Kept E2E artifacts: $TempRoot"
    } elseif (Test-Path -LiteralPath $TempRoot) {
        $ResolvedTempRoot = (Resolve-Path -LiteralPath $TempRoot).Path
        $ResolvedTempParent = (Resolve-Path -LiteralPath $TempParent).Path.TrimEnd("\")
        if ((Split-Path -Parent $ResolvedTempRoot) -ne $ResolvedTempParent -or
            (Split-Path -Leaf $ResolvedTempRoot) -notlike "bravecow-zcode-computer-use-*") {
            throw "Refusing to remove unexpected E2E path: $ResolvedTempRoot"
        }
        Remove-Item -LiteralPath $ResolvedTempRoot -Recurse -Force
    }
}
