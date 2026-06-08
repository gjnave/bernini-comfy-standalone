from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "workflows" / "Bernini_testing_video_edit_02.json"
LOGS = ROOT / "logs"


def request_json(base_url: str, path: str, payload: dict | None = None) -> dict:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(base_url.rstrip("/") + path, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        body = response.read().decode("utf-8")
    return json.loads(body) if body else {}


def wait_for_server(base_url: str, timeout: int) -> None:
    deadline = time.time() + timeout
    last_error = None
    while time.time() < deadline:
        try:
            request_json(base_url, "/system_stats")
            return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(2)
    raise RuntimeError(f"ComfyUI did not respond within {timeout}s: {last_error}")


def build_prompt() -> dict:
    positive = (
        "You are a helpful assistant specialized in video editing with reference. "
        "A beautiful cogirl smiles at the camera"
    )
    return {
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["9", 0], "text": positive},
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["9", 0], "text": "bad video"},
        },
        "5": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "Bernini_HIGH_fp8_e4m3fn_scaled.safetensors",
                "weight_dtype": "default",
            },
        },
        "7": {
            "class_type": "VAELoader",
            "inputs": {"vae_name": "Wan2_1_VAE_bf16.safetensors"},
        },
        "9": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
                "type": "wan",
                "device": "default",
            },
        },
        "11": {
            "class_type": "LoraLoaderModelOnly",
            "inputs": {
                "model": ["13", 0],
                "lora_name": "lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank64_bf16.safetensors",
                "strength_model": 3,
            },
        },
        "12": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "Bernini_LOW_fp8_e4m3fn_scaled.safetensors",
                "weight_dtype": "default",
            },
        },
        "13": {
            "class_type": "PathchSageAttentionKJ",
            "inputs": {"model": ["5", 0], "sage_attention": "auto", "allow_compile": False},
        },
        "14": {
            "class_type": "PathchSageAttentionKJ",
            "inputs": {"model": ["12", 0], "sage_attention": "auto", "allow_compile": False},
        },
        "15": {
            "class_type": "SamplerCustom",
            "inputs": {
                "model": ["29", 0],
                "add_noise": False,
                "noise_seed": 0,
                "cfg": 1,
                "positive": ["50", 0],
                "negative": ["50", 1],
                "sampler": ["27", 0],
                "sigmas": ["17", 1],
                "latent_image": ["19", 0],
            },
        },
        "16": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["15", 0], "vae": ["7", 0]},
        },
        "17": {
            "class_type": "SplitSigmas",
            "inputs": {"sigmas": ["18", 0], "step": 3},
        },
        "18": {
            "class_type": "BasicScheduler",
            "inputs": {"model": ["12", 0], "scheduler": "simple", "steps": 6, "denoise": 1},
        },
        "19": {
            "class_type": "SamplerCustom",
            "inputs": {
                "model": ["11", 0],
                "add_noise": True,
                "noise_seed": 0,
                "cfg": 1,
                "positive": ["50", 0],
                "negative": ["50", 1],
                "sampler": ["27", 0],
                "sigmas": ["17", 0],
                "latent_image": ["50", 2],
            },
        },
        "27": {
            "class_type": "KSamplerSelect",
            "inputs": {"sampler_name": "res_multistep"},
        },
        "29": {
            "class_type": "LoraLoaderModelOnly",
            "inputs": {
                "model": ["14", 0],
                "lora_name": "lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank64_bf16.safetensors",
                "strength_model": 1.5,
            },
        },
        "31": {
            "class_type": "LoadImage",
            "inputs": {"image": "2024-09-11_15-29-58_8526.png"},
        },
        "45": {
            "class_type": "CreateVideo",
            "inputs": {"images": ["16", 0], "fps": ["48", 2]},
        },
        "46": {
            "class_type": "SaveVideo",
            "inputs": {
                "video": ["45", 0],
                "filename_prefix": "video/ComfyUI",
                "format": "auto",
                "codec": "auto",
            },
        },
        "47": {
            "class_type": "LoadVideo",
            "inputs": {"file": "LTXVideo_ComfyUI_20-12-2024_221208_00001.mp4"},
        },
        "48": {
            "class_type": "GetVideoComponents",
            "inputs": {"video": ["47", 0]},
        },
        "50": {
            "class_type": "BerniniConditioning",
            "inputs": {
                "positive": ["3", 0],
                "negative": ["4", 0],
                "vae": ["7", 0],
                "width": 480,
                "height": 832,
                "length": 145,
                "batch_size": 1,
                "source_video": ["48", 0],
                "reference_images.reference_image_0": ["31", 0],
                "ref_max_size": 848,
            },
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8188")
    parser.add_argument("--wait", type=int, default=180)
    parser.add_argument("--timeout", type=int, default=3600)
    args = parser.parse_args()

    LOGS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = LOGS / f"smoke-{stamp}.json"

    report: dict = {
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "base_url": args.url,
        "workflow": str(WORKFLOW),
        "status": "FAIL",
        "checks": {},
        "events": [],
    }

    def event(message: str, **extra: object) -> None:
        item = {"time": datetime.now().isoformat(timespec="seconds"), "message": message}
        item.update(extra)
        report["events"].append(item)
        print(message, flush=True)

    try:
        wait_for_server(args.url, args.wait)
        event("ComfyUI HTTP server responded.")

        stats = request_json(args.url, "/system_stats")
        report["system_stats"] = stats

        object_info = request_json(args.url, "/object_info")
        required_nodes = [
            "BerniniConditioning",
            "PathchSageAttentionKJ",
            "LoadVideo",
            "CreateVideo",
            "GetVideoComponents",
            "SaveVideo",
            "VHS_VideoCombine",
        ]
        missing = [node for node in required_nodes if node not in object_info]
        report["checks"]["required_nodes_present"] = {"missing": missing}
        if missing:
            raise RuntimeError(f"Missing required node definitions: {missing}")
        event("Required node definitions are present, including BerniniConditioning.")

        workflow = json.loads(WORKFLOW.read_text(encoding="utf-8"))
        report["workflow_node_types"] = sorted({n.get("type") for n in workflow.get("nodes", []) if n.get("type")})
        report["workflow_inputs"] = {
            "video": "LTXVideo_ComfyUI_20-12-2024_221208_00001.mp4",
            "image": "2024-09-11_15-29-58_8526.png",
        }

        prompt = build_prompt()
        payload = {
            "prompt": prompt,
            "client_id": f"bernini-smoke-{stamp}",
            "extra_data": {"extra_pnginfo": {"workflow": workflow}},
        }
        queued = request_json(args.url, "/prompt", payload)
        prompt_id = queued.get("prompt_id")
        report["prompt_response"] = queued
        if not prompt_id:
            raise RuntimeError(f"No prompt_id returned: {queued}")
        event("Prompt queued.", prompt_id=prompt_id)

        deadline = time.time() + args.timeout
        while time.time() < deadline:
            history = request_json(args.url, f"/history/{prompt_id}")
            item = history.get(prompt_id)
            if item:
                report["history"] = item
                status = item.get("status", {})
                if status.get("completed"):
                    report["status"] = "PASS"
                    event("Prompt completed successfully.", prompt_id=prompt_id)
                    break
                messages = status.get("messages") or []
                if any(message and message[0] == "execution_error" for message in messages):
                    event("Prompt failed with execution_error.", prompt_id=prompt_id)
                    break
            time.sleep(5)
        else:
            raise RuntimeError(f"Prompt did not finish within {args.timeout}s")

        if report["status"] != "PASS":
            raise RuntimeError("Smoke prompt did not complete successfully.")

    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        report["http_error"] = {"status": exc.code, "body": body}
        print(body, file=sys.stderr)
    except Exception as exc:  # noqa: BLE001
        report["error"] = repr(exc)
        print(f"Smoke test failed: {exc}", file=sys.stderr, flush=True)
    finally:
        report["finished_at"] = datetime.now().isoformat(timespec="seconds")
        log_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Smoke log: {log_path}", flush=True)

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
