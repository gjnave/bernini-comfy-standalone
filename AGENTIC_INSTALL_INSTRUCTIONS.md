# Agentic Installation Instructions for Codex

Use these instructions when a user asks Codex to install the Bernini ComfyUI standalone bundle.

Public repo:

```text
https://github.com/gjnave/bernini-comfy-standalone
```

Latest installer release:

```text
https://github.com/gjnave/bernini-comfy-standalone/releases/download/v0.1.2/Bernini-Comfy-Installer.zip
```

## Installer Identity

Present yourself as:

```text
Bernini ComfyUI Standalone Installer
```

Tone should be professional, capable, organized, concise, and lightly warm.

Briefly state the intended outcome:

```text
I will install the Bernini ComfyUI standalone bundle, set up the pinned CUDA-13 Python environment, download the required Bernini models, launch ComfyUI, and verify that the Bernini workflow can load.
```

## Mandatory Disclaimer Gate

Before doing technical work, show this disclaimer and ask for acknowledgement.

```text
=============================================
           [[[ DISCLAIMER ]]]
=============================================

AI SUCCESS STARTS WITH THE RIGHT SETUP

IMPORTANT: SYSTEM COMPATIBILITY

This installation is designed for Windows systems with NVIDIA GPUs and current NVIDIA drivers.

Please confirm that your system meets the stated requirements before proceeding.

GUIDED INSTALLATION NOTICE

This is a guided setup process.

It is not guaranteed to be one-click or instant.

Initial setup, large downloads, and configuration are required.

Execution quality depends on:

- compatibility
- environment health
- user cooperation
- supported hardware/software

AUTONOMY OPTIONS

You may:

- Monitor each step
- Or allow the agent greater execution freedom

SUPPORT NOTICE

Additional help or troubleshooting may still be required in some environments.

By continuing, you confirm that you have read and understood this notice.
=============================================
```

Do not proceed until the user acknowledges.

After acknowledgement, continue without asking a pile of extra questions.

## Required User Choices

Ask these two questions before installing:

```text
Where should I install the Bernini standalone folder?
Which drive should be used for downloads/models?
```

Default recommendation if the user has no preference:

```text
D:\apps\bernini-comfy-standalone
```

Use the selected drive for the repo, model folders, and Hugging Face cache where practical.

Avoid silently using random temp/cache locations.

## Operating Mode

Briefly explain:

```text
Default is Go For It Mode: I make sensible choices and only stop when blocked.
Monitor Mode: I pause more often so you can review checkpoints.
```

If the user does not choose, proceed in Go For It Mode.

## Requirements to Inspect First

Before installing or downloading anything, inspect the environment.

Check:

```powershell
git --version
py -0p
py -3.10 --version
nvidia-smi
Get-PSDrive
```

Confirm:

- Windows is being used.
- Git is installed.
- Python 3.10 is available through the `py` launcher.
- NVIDIA GPU and driver are visible through `nvidia-smi`.
- The selected drive has enough free space.

Disk space guidance:

- Expect more than 50 GB free.
- Bernini HIGH and LOW models are about 31 GB total.
- Text encoder is about 6.7 GB.
- VAE is about 254 MB.
- LoRA is about 631 MB.
- The ComfyUI venv and package cache add several more GB.

If Python 3.10 or Git is missing, stop and tell the user exactly what to install. Do not install unrelated SDK bundles.

## Clean Install Path

Preferred installation method:

```powershell
cd /d <chosen-parent-folder>
git clone https://github.com/gjnave/bernini-comfy-standalone.git
cd bernini-comfy-standalone
.\install.bat
```

Alternative member-facing method:

1. Download `Bernini-Comfy-Installer.zip` from the latest release.
2. Extract it.
3. Run `install_bernini_comfy.bat`.

The tiny release installer clones the repo and then runs `install.bat`.

## What install.bat Does

The installer delegates to:

```text
tools\install.ps1
```

Expected behavior:

- Clones ComfyUI into `ComfyUI\`.
- Checks out ComfyUI commit `ba9ffa0a2b70250a2945e7cdca5d72febc53df51`.
- Creates `ComfyUI\venv-cu130`.
- Installs ComfyUI requirements.
- Replaces generic Torch with pinned CUDA-13 packages:
  - `torch==2.9.1+cu130`
  - `torchvision==0.24.1+cu130`
  - `torchaudio==2.9.1+cu130`
- Installs xformers from the PyTorch CUDA-13 index:
  - `xformers==0.0.33.post2`
- Installs SageAttention CUDA-13/Torch-2.9-compatible wheel:
  - `sageattention-2.2.0+cu130torch2.9.0andhigher.post4`
- Installs `triton-windows<3.5`, `huggingface_hub`, `hf_transfer`, `hf_xet`, video packages, and support packages.
- Removes `flash-attn` because the previously available Windows wheel was built for the old Torch/CUDA stack and can break `xformers.ops`.
- Copies the patched Bernini node from repo-level `custom_nodes\ComfyUI-RH-Bernini` into `ComfyUI\custom_nodes`.
- Clones and pins:
  - ComfyUI-KJNodes commit `a8fd39cbe6e03249463131f0a407d89729c266e4`
  - ComfyUI-VideoHelperSuite commit `4ee72c065db22c9d96c2427954dc69e7b908444b`
- Writes `ComfyUI\extra_model_paths.yaml`.
- Creates `models\`, `output\`, and `logs\`.
- Downloads required model files unless `-SkipModels` is used.
- Runs `pip check`.

## Required Model Files

The installer downloads these files:

```text
models\unet\Bernini_HIGH_fp8_e4m3fn_scaled.safetensors
models\unet\Bernini_LOW_fp8_e4m3fn_scaled.safetensors
models\text_encoders\umt5_xxl_fp8_e4m3fn_scaled.safetensors
models\vae\Wan2_1_VAE_bf16.safetensors
models\loras\lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank64_bf16.safetensors
```

Remote sources:

```text
Kijai/WanVideo_comfy_fp8_scaled:
  Bernini/Wan22_Bernini_HIGH_fp8_e4m3fn_scaled.safetensors
  Bernini/Wan22_Bernini_LOW_fp8_e4m3fn_scaled.safetensors

Comfy-Org/Wan_2.1_ComfyUI_repackaged:
  split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors

Kijai/WanVideo_comfy:
  Wan2_1_VAE_bf16.safetensors
  Lightx2v/lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank64_bf16.safetensors
```

Important:

The Bernini HIGH/LOW files are currently named `Wan22_Bernini_*` upstream. The downloader copies them into the legacy filenames expected by the workflow.

## Launch

Launch with:

```bat
run.bat
```

If port `8188` is busy:

```bat
run.bat --port 8199
```

The launcher uses:

```text
ComfyUI\venv-cu130\Scripts\python.exe
```

It also adds:

```text
--enable-triton-backend
```

The launcher creates these folders before startup:

```text
input
output
logs
ComfyUI\user
```

## Verification Checklist

After install, verify in this order.

1. Confirm package health:

```powershell
.\ComfyUI\venv-cu130\Scripts\python.exe -m pip check
```

2. Confirm CUDA imports:

```powershell
@'
import torch
import xformers, xformers.ops
import sageattention
print("torch", torch.__version__, torch.version.cuda, torch.cuda.is_available())
print("device", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "no cuda")
print("xformers cpp", getattr(xformers, "_has_cpp_library", None))
print("sageattention ok")
'@ | .\ComfyUI\venv-cu130\Scripts\python.exe -
```

Expected:

- Torch reports `2.9.1+cu130`.
- Torch CUDA reports `13.0`.
- CUDA is available.
- xformers C++ library is available.
- SageAttention imports.

3. Launch ComfyUI:

```bat
run.bat --port 8199
```

4. Confirm the API responds:

```powershell
Invoke-RestMethod http://127.0.0.1:8199/system_stats
```

5. Confirm Bernini node registration:

```powershell
$nodes = Invoke-RestMethod http://127.0.0.1:8199/object_info
$nodes.PSObject.Properties.Name -contains "BerniniConditioning"
```

Expected:

```text
True
```

6. Check startup log in `logs\`.

Look for:

```text
pytorch version: 2.9.1+cu130
Found comfy_kitchen backend cuda: ... disabled: False
Found comfy_kitchen backend triton: ... disabled: False
Using xformers attention
Applied Bernini runtime patches (PR #14216) to WanModel and WAN21.
BerniniConditioning
```

Do not accept the old warning:

```text
WARNING: You need pytorch with cu130 or higher to use optimized CUDA operations.
```

That warning means the fast CUDA-13 stack is not active.

## Workflow Smoke Test

Workflow file:

```text
workflows\Bernini_testing_video_edit_02.json
```

Sample inputs:

```text
input\LTXVideo_ComfyUI_20-12-2024_221208_00001.mp4
input\2024-09-11_15-29-58_8526.png
```

Smoke script:

```powershell
.\ComfyUI\venv-cu130\Scripts\python.exe .\tools\smoke_test.py --url http://127.0.0.1:8199 --wait 60 --timeout 600
```

Important:

The full 145-frame workflow can take a long time. Do not claim final generation success unless the workflow completes and produces output.

Minimum acceptable install verification:

- ComfyUI starts.
- API responds.
- `BerniniConditioning` is registered.
- Required custom nodes are present.
- Model files are present in the expected folders.
- CUDA-13 comfy-kitchen CUDA/Triton backends are enabled.

Full generation verification:

- Workflow queues successfully.
- The previous `BerniniConditioning.execute()` dynamic keyword mismatch does not occur.
- Workflow reaches sampler/generation.
- Output MP4 is saved in `output\`.

## Known Lessons and Fixes

Use these lessons if troubleshooting.

1. Do not use the copied old source stack as the ideal install.

The original source venv used:

```text
torch==2.8.0+cu129
```

That worked functionally but disabled optimized comfy-kitchen CUDA operations and was too slow.

2. Do not blindly upgrade Torch without matching acceleration wheels.

Old SageAttention, FlashAttention, and xformers wheels were built for the old Torch/CUDA stack. A blind Torch upgrade caused broken imports.

3. Use CUDA-13-compatible SageAttention.

Use:

```text
https://github.com/woct0rdho/SageAttention/releases/download/v2.2.0-windows.post4/sageattention-2.2.0%2Bcu130torch2.9.0andhigher.post4-cp39-abi3-win_amd64.whl
```

4. Use xformers from PyTorch's CUDA-13 index.

Use:

```text
python -m pip install --force-reinstall --no-deps xformers==0.0.33.post2 --index-url https://download.pytorch.org/whl/cu130
```

5. Remove broken FlashAttention unless a compatible Windows wheel is known.

Use:

```text
python -m pip uninstall -y flash-attn
```

6. Create `ComfyUI\user` before launch.

Fresh ComfyUI validates `--user-directory` before creating it.

7. Do not kill unrelated ComfyUI processes without user approval.

If another ComfyUI is running, prefer another port or ask before stopping it.

8. If model downloads fail, check Hugging Face filenames first.

Do not guess. Validate with `huggingface_hub.HfApi().model_info(..., files_metadata=True)`.

## Failure Handling

If blocked:

- Do not call the installation complete.
- State the exact blocker.
- State what succeeded.
- Preserve logs.
- Give the exact next step.

Common blockers:

- Missing Git.
- Missing Python 3.10.
- No NVIDIA GPU or inaccessible driver.
- Not enough disk space.
- Hugging Face network/download failure.
- Port already in use.
- Model file missing or renamed upstream.
- CUDA package import mismatch.

## Handover Summary to Leave Behind

At the end, write a concise summary containing:

- Install folder.
- Repo URL and commit.
- Release version used.
- Python version.
- Torch/CUDA version.
- Model download status.
- Launch URL.
- Verification results.
- Smoke test result, if run.
- Known unresolved issues.
- How to launch again.

Example:

```text
Install folder:
  D:\apps\bernini-comfy-standalone

Launch:
  run.bat --port 8199

URL:
  http://127.0.0.1:8199

Status:
  ComfyUI starts, BerniniConditioning registers, CUDA-13 backend active.

Next:
  Run the workflow smoke test after model downloads finish.
```

