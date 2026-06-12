param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $ComfyArgs
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Comfy = Join-Path $Root "ComfyUI"
$Logs = Join-Path $Root "logs"
$WorkflowSource = Join-Path $Root "workflows\Bernini_testing_video_edit_02.json"
$PersistentWorkflowDir = Join-Path $Comfy "user\default\workflows"
New-Item -ItemType Directory -Force -Path $Logs | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Root "input"), (Join-Path $Root "output"), (Join-Path $Comfy "user") | Out-Null

function Sync-PersistentWorkflow() {
    if (-not (Test-Path $WorkflowSource)) {
        throw "Missing workflow source file: $WorkflowSource"
    }
    New-Item -ItemType Directory -Force -Path $PersistentWorkflowDir | Out-Null
    Copy-Item -Path $WorkflowSource -Destination (Join-Path $PersistentWorkflowDir (Split-Path -Leaf $WorkflowSource)) -Force
}

Sync-PersistentWorkflow

$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$LogFile = Join-Path $Logs "run-$Stamp.log"

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:BERNINI_LAST_LOG = $LogFile

$BaseArgs = @(
    "main.py",
    "--listen", "127.0.0.1",
    "--input-directory", (Join-Path $Root "input"),
    "--output-directory", (Join-Path $Root "output"),
    "--user-directory", (Join-Path $Comfy "user")
)

if (($ComfyArgs -notcontains "--port") -and ($ComfyArgs -notcontains "-p")) {
    $BaseArgs += @("--port", "8188")
}

if ($ComfyArgs -notcontains "--enable-triton-backend") {
    $BaseArgs += @("--enable-triton-backend")
}

Write-Host "Bernini ComfyUI standalone"
Write-Host "Root: $Root"
Write-Host "Log:  $LogFile"
Write-Host "URL:  http://127.0.0.1:8188 unless overridden with --port"
Write-Host "Workflow: $PersistentWorkflowDir"
Write-Host ""

Set-Location $Comfy

function Quote-CmdArg([string] $Value) {
    if ($Value -match '[\s"]') {
        return '"' + ($Value -replace '"', '\"') + '"'
    }
    return $Value
}

$VenvName = if ($env:BERNINI_VENV) { $env:BERNINI_VENV } elseif (Test-Path (Join-Path $Comfy "venv-cu130\Scripts\python.exe")) { "venv-cu130" } else { "venv" }
$Python = Join-Path $Comfy "$VenvName\Scripts\python.exe"
Write-Host "Python: $Python"
$AllArgs = @($BaseArgs + $ComfyArgs) | ForEach-Object { Quote-CmdArg $_ }
$CommandLine = '"' + $Python + '" ' + ($AllArgs -join " ") + " 2>&1"
& cmd.exe /d /s /c $CommandLine | Tee-Object -FilePath $LogFile
