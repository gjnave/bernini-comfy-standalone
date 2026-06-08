# ComfyUI-RH-Bernini

[![RunningHub 中国站](https://img.shields.io/badge/RunningHub-%E4%B8%AD%E5%9B%BD%E7%AB%99%20Online%20Platform-2f80ed?labelColor=333333)](https://www.runninghub.cn/?inviteCode=rh-v1367)
[![RunningHub 国际站](https://img.shields.io/badge/RunningHub-%E5%9B%BD%E9%99%85%E7%AB%99%20Online%20Platform-2f80ed?labelColor=333333)](https://www.runninghub.ai/?inviteCode=rh-v1367)

ComfyUI-RH-Bernini 是一个面向 Wan 2.2 工作流的 ComfyUI 自定义节点包，用于 Bernini 风格的 in-context conditioning。它回迁了 ComfyUI PR #14216 的核心运行时逻辑，并加入从 ByteDance 官方 Bernini 仓库适配来的提示词增强辅助节点。

本插件不是 ByteDance Bernini 官方推理管线的完整转写。它用于 ComfyUI 原生 Wan 2.2 工作流，模型加载、文本编码、采样、高低噪调度和视频输出仍由现有 ComfyUI 节点完成。

## 作者

本自定义节点包作者与维护者为 [flybirdxx](https://github.com/flybirdxx)。

## 代码来源

本插件代码 fork 并回迁自 [Comfy-Org/ComfyUI#14216](https://github.com/Comfy-Org/ComfyUI/pull/14216)。该 PR 为 ComfyUI 增加 Bernini in-context conditioning 支持；本插件中的运行时 patch 代码来源于该 PR，用于在目标 ComfyUI 运行环境尚未包含该 PR 时，以独立自定义节点包的方式使用。

## 节点

- **Bernini Conditioning**：把源视频、参考视频和参考图编码为正向/反向 conditioning 上的 `context_latents`。运行时 patch 会让 Wan 模型把这些 clean latents 作为 in-context token 追加进去，并为每路输入设置独立 RoPE source ID。
- **Bernini Prompt Enhancer**：根据官方 Bernini prompt enhancer 构造任务感知的提示词增强请求。节点输出适合外部 LLM 节点的 `system_prompt` 和 `user_prompt`，同时保留 `llm_prompt`、`api_prompt` 和 `json_mode`。
- **Bernini Prompt Result Parser**：把外部 LLM 的返回解析为最终增强提示词。JSON 模式会优先读取 `rewritten_text`。

## 环境要求

- 支持 `comfy_api.latest` 的新版 ComfyUI。
- ComfyUI 内已有 Wan 2.2 工作流支持。
- Bernini 兼容的 Wan 2.2 权重。
- 本节点包不需要额外 Python 依赖。

不要通过本插件安装或替换 `torch`、`torchvision`、`torchaudio`、CUDA 或 NVIDIA 包。请使用 ComfyUI 运行环境中已有的版本。

## 模型放置

插件不会自动下载或加载模型。请使用工作流里的 Wan 2.2 模型加载节点。

推荐模型来源：

- Wan2.2 base 模型：https://huggingface.co/Wan-AI/Wan2.2-T2V-A14B-Diffusers
- ByteDance 官方 Bernini 权重：https://huggingface.co/ByteDance/Bernini
- Kijai 的 ComfyUI 兼容 Bernini 权重：https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/tree/main/Bernini

如果在 ComfyUI 环境中使用 Hugging Face 下载模型，请根据你的 Wan 加载节点要求，把模型放到 ComfyUI `models` 目录下。

示例手动准备命令：

```bash
cd /workspace/ComfyUI/models
hf download ByteDance/Bernini --local-dir Bernini
```

具体目标路径取决于工作流中使用的 Wan 加载节点。

## 使用方法

1. 先搭建 Wan 2.2 ComfyUI 工作流，包括 Bernini 兼容 checkpoint、VAE、文本编码器、采样器和视频输出节点。
2. 添加 **Bernini Conditioning**，分类为 `conditioning/video_models`。
3. 连接 `positive`、`negative`、`vae`，并设置 `width`、`height`、`length` 和 `batch_size`。
4. 根据任务连接可选媒体输入：

| 已连接输入 | 任务 |
| --- | --- |
| 无 | t2v |
| `source_video` | v2v |
| `source_video` + `reference_images` | rv2v |
| 仅 `reference_images` | r2v |
| `source_video` + `reference_video` | 视频插入 / ads2v |

5. 使用节点的 `latent` 输出作为采样的空 latent。

## 提示词增强工作流

官方 Bernini 推理脚本推荐使用 prompt enhancement。本插件不会在节点内部调用任何 API。

推荐接线：

1. 添加 **Bernini Prompt Enhancer**。
2. 将 `system_prompt` 接到外部 LLM 节点的系统提示词输入。
3. 将 `user_prompt` 接到同一 LLM 节点的用户输入或 message 输入。
4. 如果是视觉任务，并且 LLM 节点支持视觉输入，把同一份 `source_video`、`source_image` 或 `reference_images` 接给 LLM 节点。
5. 将 LLM 文本输出接到 **Bernini Prompt Result Parser**。
6. 对于 `r2v`、`r2i`、`rv2v`、`vrc2v`，把 enhancer 的 `json_mode` 接到 parser 的 `json_mode`。
7. 使用 parser 的 `enhanced_prompt` 输出进行文本编码。

如果你的 LLM 节点只支持一个 prompt 输入，可以改用 `llm_prompt`。`api_prompt` 是官方原始请求文本，保留用于兼容和调试。

## 示例

API 格式示例位于 `examples/`。

- `examples/bernini_prompt_enhancer_api.json`：最小提示词增强和解析示例。请替换占位提示词和占位 LLM 返回；在完整工作流中，也可以把 enhancer 输出接到外部 LLM 节点。

## 限制

- 本插件只 patch PR #14216 所需的 Wan 相关 ComfyUI 运行时逻辑。
- 不包含官方 Bernini 单卡或多卡推理脚本。
- 不包含官方模型权重或示例素材。
- 不在节点内部调用 LLM API，请接入外部 API 节点。

## 来源与相关链接

- 项目作者与维护者：https://github.com/flybirdxx
- ByteDance Bernini 官方仓库：https://github.com/bytedance/Bernini
- 代码 fork 与回迁来源，ComfyUI Bernini PR：https://github.com/Comfy-Org/ComfyUI/pull/14216
- Kijai Bernini 分支：https://github.com/kijai/ComfyUI/tree/bernini
- Bernini 论文：https://arxiv.org/abs/2605.22344
- Bernini 项目页：https://bytedance.github.io/Bernini
- ByteDance 官方 Bernini 权重：https://huggingface.co/ByteDance/Bernini
- Wan2.2 base 模型：https://huggingface.co/Wan-AI/Wan2.2-T2V-A14B-Diffusers
- Kijai ComfyUI 兼容权重：https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/tree/main/Bernini
- ByteDance Bernini 协议：https://github.com/bytedance/Bernini/blob/main/LICENSE
- ComfyUI 协议：https://github.com/comfyanonymous/ComfyUI/blob/master/LICENSE

## 协议

本自定义节点包基于 GPL-3.0-only 分发，因为它回迁并 patch 了 ComfyUI 运行时代码。从 ByteDance Bernini 适配的提示词增强模板归属上游 Apache-2.0 项目。详见 `LICENSE`。
