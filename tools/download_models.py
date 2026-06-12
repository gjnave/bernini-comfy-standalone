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
        "repo_id": "Kijai/WanVideo_comfy",
        "filename": "Wan2_1_VAE_bf16.safetensors",
        "dest": "models/vae/Wan2_1_VAE_bf16.safetensors",
    },
    {
        "repo_id": "Kijai/WanVideo_comfy",
        "filename": "Lightx2v/lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank64_bf16.safetensors",
        "dest": "models/loras/lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank64_bf16.safetensors",
    },
]

MODEL_ALIASES = [
    {
        "source": "models/vae/Wan2_1_VAE_bf16.safetensors",
        "dest": "models/vae/wan_2.1_vae_Comfy-Org.safetensors",
    },
    {
        "source": "models/loras/lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank64_bf16.safetensors",
        "dest": "models/loras/wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors",
    },
    {
        "source": "models/loras/lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank64_bf16.safetensors",
        "dest": "models/loras/wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors",
    },
]


def ensure_model_aliases(root: Path, force: bool = False) -> None:
    for alias in MODEL_ALIASES:
        source = root / alias["source"]
        dest = root / alias["dest"]
        if not source.exists() or source.stat().st_size == 0:
            print(f"WARNING missing alias source: {source.relative_to(root)}")
            continue

        if dest.exists():
            if dest.stat().st_size > 0 and not force:
                print(f"OK alias exists: {dest.relative_to(root)}")
                continue
            dest.unlink()

        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            dest.hardlink_to(source)
            print(f"Linked alias {dest.relative_to(root)} -> {source.relative_to(root)}")
        except OSError:
            shutil.copy2(source, dest)
            print(f"Copied alias {dest.relative_to(root)} -> {source.relative_to(root)}")


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

    ensure_model_aliases(root, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
