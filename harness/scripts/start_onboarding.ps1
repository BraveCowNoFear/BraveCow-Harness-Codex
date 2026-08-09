#requires -Version 5.1
[CmdletBinding()]
param(
    [ValidateSet("Codex", "ZCode")][string]$Runtime,
    [Parameter(Mandatory = $true)][string]$Workspace,
    [Parameter(Mandatory = $true)][string]$SkillPath,
    [Parameter(Mandatory = $true)][string]$ReceiptPath,
    [ValidateSet("auto", "zh-CN", "en")][string]$Language = "auto",
    [int]$TimeoutSeconds = 300
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-LaunchReceipt {
    param([hashtable]$Data)
    $Data.recorded_at = [DateTimeOffset]::UtcNow.ToString("o")
    $parent = Split-Path -Parent $ReceiptPath
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
    $Data | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $ReceiptPath -Encoding UTF8
}

if ($Runtime -eq "Codex") {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $python) { $python = Get-Command python3 -ErrorAction SilentlyContinue }
    if ($null -eq $python) {
        Write-LaunchReceipt @{ status = "failed"; runtime = "Codex"; method = "app-server"; error = "Python is required for the Codex App Server launcher." }
        Write-Error "Python is required to create the Codex onboarding task."
    }
    & $python.Source (Join-Path $PSScriptRoot "start_onboarding.py") --workspace $Workspace --skill-path $SkillPath --receipt $ReceiptPath --language $Language --timeout $TimeoutSeconds
    exit $LASTEXITCODE
}

$zcode = Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match "(?i)zcode" } | Select-Object -First 1
if ($null -eq $zcode) {
    $candidates = @(
        $env:ZCODE_EXECUTABLE,
        (Join-Path $env:LOCALAPPDATA "Programs\ZCode\ZCode.exe"),
        (Join-Path $env:LOCALAPPDATA "ZCode\ZCode.exe"),
        (Join-Path $env:ProgramFiles "ZCode\ZCode.exe")
    ) | Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Leaf) }
    if ($candidates.Count -gt 0) {
        Start-Process -FilePath $candidates[0]
        Start-Sleep -Seconds 3
        $zcode = Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match "(?i)zcode" } | Select-Object -First 1
    }
}
if ($null -eq $zcode) {
    Write-LaunchReceipt @{ status = "failed"; runtime = "ZCode"; method = "keyboard-shortcut"; error = "ZCode is not running and no executable was found." }
    Write-Error "ZCode was not found. Open ZCode and run /bravecow-onboarding to start the course."
}

$shell = New-Object -ComObject WScript.Shell
if (-not $shell.AppActivate($zcode.Id)) {
    Write-LaunchReceipt @{ status = "failed"; runtime = "ZCode"; method = "keyboard-shortcut"; error = "Could not activate the ZCode window." }
    Write-Error "Could not activate ZCode. Run /bravecow-onboarding in a new task."
}
$savedClipboard = $null
$hadClipboard = $false
try {
    try { $savedClipboard = Get-Clipboard -Raw; $hadClipboard = $true } catch { }
    $prompt = if ($Language -eq "en") {
        '$bravecow-onboarding Start the interactive beginner course as the teacher named by the skill. Teach warmly, directly, and respectfully without sounding childish. Use at most five short sentences, one example, and one question per normal lesson. Avoid restating the learner, unnecessary sample answers, or repeated summaries.'
    } else {
        '$bravecow-onboarding Start the interactive beginner course in Simplified Chinese as the teacher named by the skill. Teach warmly, directly, and respectfully without sounding childish. Use at most five short sentences, one example, and one question per normal lesson. Avoid restating the learner, unnecessary sample answers, or repeated summaries, and wait for my reply.'
    }
    Set-Clipboard -Value $prompt
    $shell.SendKeys("^n")
    Start-Sleep -Milliseconds 800
    $shell.SendKeys("^v")
    Start-Sleep -Milliseconds 200
    $shell.SendKeys("{ENTER}")
    Write-LaunchReceipt @{ status = "started"; runtime = "ZCode"; method = "keyboard-shortcut"; shortcut = "Ctrl+N" }
    Write-Host "Started ZCode onboarding task."
} finally {
    if ($hadClipboard) { Set-Clipboard -Value $savedClipboard }
}
