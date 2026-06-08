param(
    [switch] $SkipModels,
    [switch] $ForceModels,
    [string] $PythonVersion = "3.10"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Comfy = Join-Path $Root "ComfyUI"
$Venv = Join-Path $Comfy "venv-cu130"
$Python = Join-Path $Venv "Scripts\python.exe"
$RepoCustomNodes = Join-Path $Root "custom_nodes"
$ComfyCustomNodes = Join-Path $Comfy "custom_nodes"

$ComfyCommit = "ba9ffa0a2b70250a2945e7cdca5d72febc53df51"
$KJCommit = "a8fd39cbe6e03249463131f0a407d89729c266e4"
$VHSCommit = "4ee72c065db22c9d96c2427954dc69e7b908444b"

function Run($File, [string[]] $CommandArgs, [string] $WorkingDirectory = $Root) {
    Write-Host ""
    Write-Host "> $File $($CommandArgs -join ' ')"
    $p = Start-Process -FilePath $File -ArgumentList $CommandArgs -WorkingDirectory $WorkingDirectory -Wait -NoNewWindow -PassThru
    if ($p.ExitCode -ne 0) {
        throw "Command failed with exit code $($p.ExitCode): $File $($CommandArgs -join ' ')"
    }
}

function Copy-Directory($Source, $Destination) {
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    robocopy $Source $Destination /E /XD __pycache__ .git /XF *.pyc /NFL /NDL /NJH /NJS /NP /R:2 /W:2 | Out-Host
    if ($LASTEXITCODE -gt 7) {
        throw "robocopy failed with exit code $LASTEXITCODE"
    }
}

Write-Host "Bernini ComfyUI standalone install"
Write-Host "Root: $Root"

Run "git" @("--version")
Run "py" @("-$PythonVersion", "--version")

if (-not (Test-Path $Comfy)) {
    Run "git" @("clone", "https://github.com/comfyanonymous/ComfyUI.git", $Comfy)
}

Run "git" @("fetch", "--tags", "--depth", "1", "origin", $ComfyCommit) $Comfy
Run "git" @("checkout", $ComfyCommit) $Comfy

if (-not (Test-Path $Python)) {
    Run "py" @("-$PythonVersion", "-m", "venv", $Venv)
}

Run $Python @("-m", "pip", "install", "--upgrade", "pip")
Run $Python @("-m", "pip", "install", "-r", (Join-Path $Comfy "requirements.txt"))
Run $Python @("-m", "pip", "install", "--force-reinstall", "--no-deps", "torch==2.9.1+cu130", "torchvision==0.24.1+cu130", "torchaudio==2.9.1+cu130", "--index-url", "https://download.pytorch.org/whl/cu130")
Run $Python @("-m", "pip", "install", "--force-reinstall", "--no-deps", "xformers==0.0.33.post2", "--index-url", "https://download.pytorch.org/whl/cu130")
Run $Python @("-m", "pip", "install", "--force-reinstall", "https://github.com/woct0rdho/SageAttention/releases/download/v2.2.0-windows.post4/sageattention-2.2.0%2Bcu130torch2.9.0andhigher.post4-cp39-abi3-win_amd64.whl")
Run $Python @("-m", "pip", "install", "triton-windows<3.5", "onnx", "onnxruntime", "onnxruntime-gpu", "accelerate", "huggingface_hub", "hf_transfer", "hf_xet", "imageio-ffmpeg", "av", "pillow<12,>=9.2.0")
Run $Python @("-m", "pip", "uninstall", "-y", "flash-attn")

New-Item -ItemType Directory -Force -Path $ComfyCustomNodes | Out-Null
Copy-Directory (Join-Path $RepoCustomNodes "ComfyUI-RH-Bernini") (Join-Path $ComfyCustomNodes "ComfyUI-RH-Bernini")

$KJ = Join-Path $ComfyCustomNodes "ComfyUI-KJNodes"
if (-not (Test-Path $KJ)) {
    Run "git" @("clone", "https://github.com/kijai/ComfyUI-KJNodes.git", $KJ)
}
Run "git" @("fetch", "--depth", "1", "origin", $KJCommit) $KJ
Run "git" @("checkout", $KJCommit) $KJ
Run $Python @("-m", "pip", "install", "-r", (Join-Path $KJ "requirements.txt"))

$VHS = Join-Path $ComfyCustomNodes "ComfyUI-VideoHelperSuite"
if (-not (Test-Path $VHS)) {
    Run "git" @("clone", "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git", $VHS)
}
Run "git" @("fetch", "--depth", "1", "origin", $VHSCommit) $VHS
Run "git" @("checkout", $VHSCommit) $VHS
Run $Python @("-m", "pip", "install", "-r", (Join-Path $VHS "requirements.txt"))

@"
bernini:
  base_path: $Root
  diffusion_models: models/unet
  text_encoders: models/text_encoders
  loras: models/loras
  vae: models/vae
"@ | Set-Content -Path (Join-Path $Comfy "extra_model_paths.yaml") -Encoding UTF8

New-Item -ItemType Directory -Force -Path (Join-Path $Root "models\unet"), (Join-Path $Root "models\text_encoders"), (Join-Path $Root "models\loras"), (Join-Path $Root "models\vae"), (Join-Path $Root "output"), (Join-Path $Root "logs") | Out-Null

if (-not $SkipModels) {
    $env:HF_HUB_ENABLE_HF_TRANSFER = "1"
    $downloadArgs = @((Join-Path $Root "tools\download_models.py"), "--root", $Root)
    if ($ForceModels) {
        $downloadArgs += "--force"
    }
    Run $Python $downloadArgs
} else {
    Write-Host "Skipping model downloads. Put required files in models\ before running."
}

Run $Python @("-m", "pip", "check")

Write-Host ""
Write-Host "Install complete."
Write-Host "Launch with: run.bat"
