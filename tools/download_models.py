from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from huggingface_hub import hf_hub_download


MODELS = [
    {
        "repo_id": "Kijai/WanVideo_comfy_fp8_scaled",
        "filename": "Bernini/Wan22_Bernini_HIGH_fp8_e4m3fn_scaled.safetensors",
        "dest": "models/unet/Bernini_HIGH_fp8_e4m3fn_scaled.safetensors",
    },
    {
        "repo_id": "Kijai/WanVideo_comfy_fp8_scaled",
        "filename": "Bernini/Wan22_Bernini_LOW_fp8_e4m3fn_scaled.safetensors",
        "dest": "models/unet/Bernini_LOW_fp8_e4m3fn_scaled.safetensors",
    },
    {
        "repo_id": "Comfy-Org/Wan_2.1_ComfyUI_repackaged",
        "filename": "split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors",
        "dest": "models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors",
    },
    {
        "repo_id": "Comfy-Org/Wan_2.1_ComfyUI_repackaged",
        "filename": "split_files/vae/Wan2_1_VAE_bf16.safetensors",
        "dest": "models/vae/Wan2_1_VAE_bf16.safetensors",
    },
    {
        "repo_id": "Kijai/WanVideo_comfy",
        "filename": "Lightx2v/lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank64_bf16.safetensors",
        "dest": "models/loras/lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank64_bf16.safetensors",
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Download Bernini model files for the standalone bundle.")
    parser.add_argument("--root", default=".", help="Standalone repo root.")
    parser.add_argument("--force", action="store_true", help="Redownload/copy even when destination files exist.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    cache_dir = root / ".cache" / "hf"

    for model in MODELS:
        dest = root / model["dest"]
        if dest.exists() and dest.stat().st_size > 0 and not args.force:
            print(f"OK exists: {dest.relative_to(root)}")
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"Downloading {model['repo_id']}::{model['filename']}")
        downloaded = Path(
            hf_hub_download(
                repo_id=model["repo_id"],
                filename=model["filename"],
                local_dir=cache_dir,
                local_dir_use_symlinks=False,
            )
        )
        shutil.copy2(downloaded, dest)
        print(f"Wrote {dest.relative_to(root)} ({dest.stat().st_size / (1024 ** 3):.2f} GB)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
