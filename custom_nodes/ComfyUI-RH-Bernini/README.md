# ComfyUI-RH-Bernini

[![RunningHub China](https://img.shields.io/badge/RunningHub-China%20Online%20Platform-2f80ed?labelColor=333333)](https://www.runninghub.cn/?inviteCode=rh-v1367)
[![RunningHub International](https://img.shields.io/badge/RunningHub-International%20Online%20Platform-2f80ed?labelColor=333333)](https://www.runninghub.ai/?inviteCode=rh-v1367)

ComfyUI-RH-Bernini is a standalone ComfyUI custom node pack for Bernini-style in-context conditioning on Wan 2.2 workflows. It backports the core runtime behavior from ComfyUI PR #14216 and adds prompt-enhancement helper nodes adapted from the official ByteDance Bernini repository.

This package is not a full standalone port of the official ByteDance Bernini inference pipeline. It is intended for ComfyUI-native Wan 2.2 workflows where model loading, text encoding, sampling, high/low-noise scheduling, and video output are handled by existing ComfyUI nodes.

## Author

This custom node package is authored and maintained by [flybirdxx](https://github.com/flybirdxx).

## Code Origin

This code is forked and backported from [Comfy-Org/ComfyUI#14216](https://github.com/Comfy-Org/ComfyUI/pull/14216), which adds Bernini in-context conditioning support to ComfyUI. Runtime patch code in this package is derived from that PR so it can be used as a standalone custom node pack before the PR is available in the target ComfyUI runtime.

## Nodes

- **Bernini Conditioning**: encodes source video, reference video, and reference images into `context_latents` on positive and negative conditioning. The Wan model patch appends those clean latents as in-context tokens with per-stream RoPE source IDs.
- **Bernini Prompt Enhancer**: builds task-aware prompt-enhancement instructions from the official Bernini prompt enhancer. It outputs separate `system_prompt` and `user_prompt` strings for external LLM nodes, plus `llm_prompt`, `api_prompt`, and `json_mode`.
- **Bernini Prompt Result Parser**: parses the external LLM response into the final enhanced prompt. JSON mode looks for `rewritten_text`.

## Requirements

- Recent ComfyUI with V3 custom node support through `comfy_api.latest`.
- Wan 2.2 model workflow support in ComfyUI.
- Bernini-compatible Wan 2.2 weights.
- No extra Python packages are required by this node pack beyond the ComfyUI runtime.

Do not install or replace `torch`, `torchvision`, `torchaudio`, CUDA, or NVIDIA packages from this plugin. Use the versions already provided by your ComfyUI environment.

## Model Layout

The plugin does not download or load models directly. Use your existing ComfyUI Wan 2.2 model loaders.

Recommended model sources:

- Wan2.2 base model: https://huggingface.co/Wan-AI/Wan2.2-T2V-A14B-Diffusers
- Official Bernini weights: https://huggingface.co/ByteDance/Bernini
- Kijai ComfyUI-compatible Bernini weights: https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/tree/main/Bernini

If you use Hugging Face downloads in a ComfyUI environment, prepare models under your ComfyUI `models` directory according to the loader nodes used by your workflow.

Example manual preparation commands:

```bash
cd /workspace/ComfyUI/models
hf download ByteDance/Bernini --local-dir Bernini
```

The exact destination path depends on the Wan loader nodes in your workflow.

## Usage

1. Build a Wan 2.2 ComfyUI workflow with the Bernini-compatible checkpoint, VAE, text encoder, sampler, and video output nodes.
2. Add **Bernini Conditioning** under `conditioning/video_models`.
3. Connect `positive`, `negative`, `vae`, and set `width`, `height`, `length`, and `batch_size`.
4. Connect optional media inputs according to the task:

| Inputs connected | Task |
| --- | --- |
| none | t2v |
| `source_video` | v2v |
| `source_video` + `reference_images` | rv2v |
| `reference_images` only | r2v |
| `source_video` + `reference_video` | video insertion / ads2v |

5. Use the `latent` output as the empty latent for sampling.

## Prompt Enhancer Workflow

The official Bernini inference scripts recommend prompt enhancement. This plugin does not call any API internally.

Recommended graph:

1. Add **Bernini Prompt Enhancer**.
2. Connect `system_prompt` to an external LLM node's system input.
3. Connect `user_prompt` to the same LLM node's user or message input.
4. For vision tasks, also connect the same `source_video`, `source_image`, or `reference_images` to that LLM node if it supports visual input.
5. Connect the LLM text response to **Bernini Prompt Result Parser**.
6. Connect `json_mode` from the enhancer to `json_mode` on the parser for `r2v`, `r2i`, `rv2v`, and `vrc2v`.
7. Use the parser's `enhanced_prompt` output for text encoding.

If your LLM node only supports one prompt input, use `llm_prompt` instead. `api_prompt` is kept as the raw official prompt request for compatibility and debugging.

## Examples

API-format examples are stored in `examples/`.

- `examples/bernini_prompt_enhancer_api.json`: minimal prompt enhancer and parser graph. Replace the placeholder prompt and the placeholder LLM response with your own values or connect the outputs to an external LLM node in a full workflow.

## Limitations

- This plugin patches only Wan-related ComfyUI runtime behavior needed by PR #14216.
- It does not implement the official Bernini single-GPU or multi-GPU inference scripts.
- It does not include official model weights or example media.
- It does not provide a built-in LLM API call. Use an external API node.

## Source And Related Links

- Project author and maintainer: https://github.com/flybirdxx
- Official ByteDance Bernini repository: https://github.com/bytedance/Bernini
- Code fork and backport source, ComfyUI Bernini PR: https://github.com/Comfy-Org/ComfyUI/pull/14216
- Kijai Bernini branch used by the PR: https://github.com/kijai/ComfyUI/tree/bernini
- Bernini paper: https://arxiv.org/abs/2605.22344
- Bernini project page: https://bytedance.github.io/Bernini
- Official Bernini model weights: https://huggingface.co/ByteDance/Bernini
- Wan2.2 base model: https://huggingface.co/Wan-AI/Wan2.2-T2V-A14B-Diffusers
- Kijai ComfyUI-compatible weights: https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/tree/main/Bernini
- Official ByteDance Bernini license: https://github.com/bytedance/Bernini/blob/main/LICENSE
- ComfyUI license: https://github.com/comfyanonymous/ComfyUI/blob/master/LICENSE

## License

This custom node pack is distributed under GPL-3.0-only because it backports and patches ComfyUI runtime code. The prompt-enhancement templates adapted from ByteDance Bernini are attributed to the upstream Apache-2.0 project. See `LICENSE` for details.
