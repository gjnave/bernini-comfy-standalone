# Bernini ComfyUI Standalone

Experimental one-click-ish Bernini ComfyUI bundle for Windows/NVIDIA users.

This repo is intentionally small. It installs ComfyUI, creates a Python venv, installs the pinned CUDA-13 runtime stack, installs the required custom nodes, downloads the required model files, then launches the Bernini workflow with a source video and reference image.

## Quick Install

For members, use the tiny installer:

1. Download/extract `Bernini-Comfy-Installer.zip` from the GitHub release.
2. Run `install_bernini_comfy.bat`.
3. After install finishes, run `run.bat` inside the cloned `bernini-comfy-standalone` folder.

The installer clones this repo, builds the runtime, and downloads the models.

## Requirements

- Windows
- NVIDIA GPU with current drivers
- Git for Windows
- Python 3.10 with the `py` launcher
- A lot of free disk space. The Bernini HIGH/LOW models alone are roughly 31 GB total.

## Manual Install

```bat
git clone https://github.com/gjnave/bernini-comfy-standalone.git
cd bernini-comfy-standalone
install.bat
run.bat
```

If port `8188` is busy:

```bat
run.bat --port 8199
```

## Runtime Pins

- ComfyUI commit: `ba9ffa0a2b70250a2945e7cdca5d72febc53df51`
- Python: `3.10`
- Torch: `2.9.1+cu130`
- Torchvision: `0.24.1+cu130`
- Torchaudio: `2.9.1+cu130`
- xformers: `0.0.33.post2` from the PyTorch CUDA 13.0 index
- SageAttention: `2.2.0+cu130torch2.9.0andhigher.post4`
- comfy-kitchen: `0.2.10`
- ComfyUI-KJNodes commit: `a8fd39cbe6e03249463131f0a407d89729c266e4`
- ComfyUI-VideoHelperSuite commit: `4ee72c065db22c9d96c2427954dc69e7b908444b`

## Models Downloaded

The installer downloads:

- `models/unet/Bernini_HIGH_fp8_e4m3fn_scaled.safetensors`
- `models/unet/Bernini_LOW_fp8_e4m3fn_scaled.safetensors`
- `models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors`
- `models/vae/Wan2_1_VAE_bf16.safetensors`
- `models/loras/lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank64_bf16.safetensors`

The Bernini model files are downloaded from Kijai's Hugging Face repo under their current `Wan22_Bernini_*` filenames and copied into the legacy filenames expected by this workflow.

## Workflow

Included workflow:

```text
workflows/Bernini_testing_video_edit_02.json
```

Sample inputs:

```text
input/LTXVideo_ComfyUI_20-12-2024_221208_00001.mp4
input/2024-09-11_15-29-58_8526.png
```

Outputs go to:

```text
output/
```

## Current Status

Functional generation was proven from the local standalone copy, but the full 145-frame workflow is still slower than the reported ~70 second target on the test machine. The CUDA-13 installer stack fixes the earlier disabled comfy-kitchen CUDA/Triton backend issue, but this is still an experimental bundle.

Smoke logs from the source build are kept in `logs/` locally and are not committed.
