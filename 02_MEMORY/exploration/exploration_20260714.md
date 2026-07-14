# Exploration Report: Local LLM Optimization / Quantization

**Date**: 2026-07-14

**Topic ID**: T-008

**Why for ACE**: Ollama 是 ACE Provider 之一，需要持续跟踪本地模型优化技术

## Findings

这些项目围绕本地 LLM 推理与量化展开，核心是 C/C++ 高效实现（llama.cpp）及其语言绑定（llama‑cpp‑python），以及面向特定硬件的加速库（intel/ipex-llm）。h2ogpt 与 local-deep-research 展示了在私有化、跨模型、检索增强等上层应用的完整生态。整体来看，llama.cpp 为所有本地部署提供底层算子与量化支持，是 Ollama 依赖的关键组件；ipex-llm 则提供 Intel GPU/NPU 的专属加速，值得关注硬件多样化趋势。

## Question for ACE

> 为什么要在 ACE 的本地模型优化路线中同时关注通用 C++ 实现和硬件专属加速（如 Intel ipex-llm），是否应该建立统一的抽象层以兼容多种加速后端？

## Recommendation

**ABSORB** — llama.cpp 是 Ollama 的核心依赖，直接影响推理性能与量化方案；结合 ipex-llm 的硬件加速可以提升 ACE 在多平台部署的竞争力，值得纳入研究议程。

## Projects Found

| Project | Stars | Language | Updated | Description |
|---|---|---|---|---|
| [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp) | 120248 | C++ | 2026-07-13 | LLM inference in C/C++ |
| [h2oai/h2ogpt](https://github.com/h2oai/h2ogpt) | 11976 | Python | 2026-07-12 | Private chat with local GPT with document, images, video, etc. 100% private, Apa |
| [abetlen/llama-cpp-python](https://github.com/abetlen/llama-cpp-python) | 10481 | Python | 2026-07-13 | Python bindings for llama.cpp |
| [intel/ipex-llm](https://github.com/intel/ipex-llm) | 8863 | Python | 2026-07-13 | Accelerate local LLM inference and finetuning (LLaMA, Mistral, ChatGLM, Qwen, De |
| [LearningCircuit/local-deep-research](https://github.com/LearningCircuit/local-deep-research) | 8709 | Python | 2026-07-13 |  ~95% on SimpleQA (e.g. Qwen3.6-27B on a 3090). Supports all local and cloud LLM |
