Bernini ComfyUI Standalone POC
==============================

Status: FAIL

This is a proof-of-concept standalone Bernini ComfyUI bundle built from the existing working setup at:

  D:\comfyUI

The bundle is intentionally single-purpose: it includes the ComfyUI runtime, the Bernini workflow, the required Bernini/KJ/VHS custom nodes, the referenced models, and the source video/reference image used by the workflow.


How to run
----------

Double-click:

  run.bat

Default URL:

  http://127.0.0.1:8188

If 8188 is already in use:

  run.bat --port 8199

Logs are written to:

  logs\

Outputs are written to:

  output\


Workflow and inputs
-------------------

Workflow:

  workflows\Bernini_testing_video_edit_02.json

Persistent workflow copy:

  ComfyUI\user\default\workflows\Bernini_testing_video_edit_02.json

The installer and launcher sync the repo workflow into ComfyUI's user workflow folder so the standalone keeps a persistent copy of the Bernini graph.

The active GUI for this standalone is ComfyUI on:

  http://127.0.0.1:8188

The Bernini custom node pack also exposes the workflow as a ComfyUI workflow template and now auto-loads that Bernini workflow on startup when the canvas is blank.

Original source workflow:

  D:\comfyUI\Bernini_testing_video_edit_02.json

Input video:

  input\LTXVideo_ComfyUI_20-12-2024_221208_00001.mp4

Input/reference image:

  input\2024-09-11_15-29-58_8526.png

The workflow uses Bernini video editing with a source video and an expanded reference image input:

  reference_images.reference_image_0


Included models
---------------

Models are stored at the bundle root and mapped into ComfyUI by:

  ComfyUI\extra_model_paths.yaml

Included files:

  models\unet\Bernini_HIGH_fp8_e4m3fn_scaled.safetensors
  models\unet\Bernini_LOW_fp8_e4m3fn_scaled.safetensors
  models\text_encoders\umt5_xxl_fp8_e4m3fn_scaled.safetensors
  models\vae\Wan2_1_VAE_bf16.safetensors
  models\loras\lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank64_bf16.safetensors


Included custom nodes
---------------------

  ComfyUI-RH-Bernini
  ComfyUI-KJNodes
  ComfyUI-VideoHelperSuite

Known source versions:

  ComfyUI: v0.24.1, source commit ba9ffa0a2b70250a2945e7cdca5d72febc53df51
  ComfyUI-KJNodes: a8fd39cbe6e03249463131f0a407d89729c266e4
  ComfyUI-VideoHelperSuite: 4ee72c065db22c9d96c2427954dc69e7b908444b
  ComfyUI-RH-Bernini: copied folder from existing setup; no local .git checkout was present.


Python/runtime versions
-----------------------

  Python: 3.10.11
  Active venv: ComfyUI\venv-cu130
  Fallback/source-copy venv: ComfyUI\venv
  Torch: 2.9.1+cu130
  Torchvision: 0.24.1+cu130
  Torchaudio: 2.9.1+cu130
  CUDA reported by Torch: 13.0
  xformers: 0.0.33.post2 from the PyTorch cu130 index
  sageattention: 2.2.0+cu130torch2.9.0andhigher.post4 wheel
  flash-attn: intentionally removed from venv-cu130 because the copied 2.8.2 wheel was built for the old Torch/CUDA stack and broke xformers.ops imports
  comfyui_frontend_package: 1.44.19
  comfyui_workflow_templates: 0.9.98
  comfyui_embedded_docs: 0.5.2
  comfy-kitchen: 0.2.10
  numpy: 2.2.6
  pillow: 11.3.0
  av: 17.0.0
  imageio-ffmpeg: 0.6.0
  transformers: 5.6.2
  diffusers: git f7fd76adcd288494a1a13c82d06e37579170aaf3

The original copied source venv remains at ComfyUI\venv and is still usable by launching with:

  set BERNINI_VENV=venv
  run.bat --port 8199

That fallback venv uses Torch 2.8.0+cu129 and was functionally proven, but it disables ComfyUI's optimized comfy-kitchen CUDA backend and is much too slow for the expected timing.


Runtime patch
-------------

The standalone Bernini node was patched to tolerate expanded dynamic reference-image inputs such as:

  reference_images.reference_image_0

This fixes the previous BerniniConditioning.execute() keyword mismatch for this workflow while preserving the normal reference_images input.

The Bernini runtime patch also applies ComfyUI PR #14216 behavior for Wan/Bernini in-context conditioning when the core runtime does not already include it. Startup log confirms:

  Applied Bernini runtime patches (PR #14216) to WanModel and WAN21.


What was excluded
-----------------

Excluded from the standalone bundle:

  unrelated custom nodes
  unrelated model files
  unrelated input media
  previous ComfyUI outputs
  ComfyUI git metadata
  top-level ComfyUI tests and examples
  installer/download helper scripts from D:\comfyUI

Kept intentionally:

  full copied Python venv, because the working source environment has many pinned binary/GPU packages and a minimal reinstall is not yet proven
  base ComfyUI runtime code, because pruning internal runtime modules was too risky for this first POC
  VideoHelperSuite, even though the active output path uses core SaveVideo, because the UI workflow still contains a disabled VHS node and should open without missing-node noise


Smoke test result
-----------------

Current smoke test: FAIL

Launch method used:

  run.bat --port 8199

Smoke script:

  tools\smoke_test.py --url http://127.0.0.1:8199 --wait 60 --timeout 600

Smoke log:

  logs\smoke-20260608-023323.json

Server run log:

  logs\run-20260608-023254.log

Prompt id:

  99a774c9-c3e5-46ba-a7bc-e5b853434847

Started:

  2026-06-08T02:33:23

Interrupted:

  2026-06-08T02:43:26 after the smoke script timeout

Result:

  Prompt did not finish within 600 seconds. It was manually interrupted after timeout.

Generated output:

  none from this CUDA-13 smoke attempt

The current smoke test confirmed:

  ComfyUI starts from this standalone folder
  BerniniConditioning is registered
  PathchSageAttentionKJ is registered
  VideoHelperSuite/VHS_VideoCombine is registered
  the workflow source video loads
  the workflow reference image loads
  the expanded reference image keyword mismatch is fixed
  comfy-kitchen CUDA backend is enabled
  comfy-kitchen Triton backend is enabled
  xformers attention is enabled
  SageAttention auto mode is reached
  the workflow reaches generation

The current smoke test did not confirm successful completion or MP4 output.

Performance notes from the CUDA-13 smoke:

  Workflow dimensions: 480 x 832
  Workflow length: 145 frames
  Scheduler steps: 6, split into a 3-step high pass and 3-step low pass
  Model initialization improved from about 142 seconds on the copied cu129 venv to about 52 seconds on venv-cu130.
  The first sampler pass still took several minutes; the log reached 2/3 steps at about 4:21, then remained running until interrupt.

Earlier functional baseline:

  logs\smoke-20260608-000309.json
  logs\run-20260608-000157.log
  output\video\ComfyUI_00001_.mp4

This earlier run completed successfully with the copied cu129 venv, but took about 42 minutes. It proves the bundle can generate, but it does not meet the expected approximately 70 second performance target.


Known issues / unfinished
-------------------------

  This is not a polished GGF app shell yet; it still exposes ComfyUI.
  The Python venv is large and not minimized.
  The launcher does not yet provide a simplified image/video picker UI.
  The default port is 8188; pass --port if another ComfyUI instance is already running.
  The active launcher now uses the CUDA-13 venv and enables the comfy-kitchen Triton backend.
  The intended workflow still does not complete near the reported 70 second timing on this machine.
  A separate ComfyUI process on port 8188 remained running during testing and retained about 10-11 GB of VRAM even after /free; it was not killed because it is outside this standalone bundle.
  A separate process on port 8201 also remained listening and refused termination from this session; it did not appear in nvidia-smi after cleanup.
  pip freeze reports invalid-distribution warnings for copied comfy packages, inherited from the source environment, but pip check reports no broken requirements and startup/import checks pass.
