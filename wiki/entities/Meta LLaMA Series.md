---
type: entity
title: "Meta LLaMA Series"
created: 2026-07-17
updated: 2026-07-17
tags:
  - entity
  - meta
  - llama
  - open-source
status: seed
address: c-000019
related:
  - "[[AI大模型知识点全景图-home]]"
  - "[[AI Large Model Architecture]]"
  - "[[LLM Training Methods]]"
  - "[[Chinese AI Model Ecosystem]]"
---

# Meta LLaMA Series

Meta 的 LLaMA 系列是开源大模型的基石。LLaMA 开源后催生了全球范围内的模型微调、社区优化和衍生模型生态。

## 模型时间线

| 模型 | 发布时间 | 参数 | 训练数据 | 关键影响 |
|------|----------|------|----------|----------|
| LLaMA 1 | 2023-02 | 7B/13B/33B/65B | 1.0T tokens | 开源社区起点 |
| LLaMA 2 | 2023-07 | 7B/13B/70B | 2.0T tokens | 商用免费 + RLHF |
| Code LLaMA | 2023-08 | 7B/13B/34B | 代码专项 | 代码开源模型起点 |
| LLaMA 3 | 2024-04 | 8B/70B | 15T+ tokens | 质量飞跃、接近 GPT-4 |
| LLaMA 3.1 | 2024-07 | 8B/70B/405B | 15T+ | 405B 开源、长上下文 128K |

## 架构细节

### LLaMA 1 → 2 → 3 的架构演进

| 组件 | LLaMA 1 | LLaMA 2 | LLaMA 3 |
|------|---------|---------|---------|
| Attention | MHA | GQA (70B) | GQA (all) |
| Position Encoding | RoPE | RoPE | RoPE |
| Activation | SwiGLU | SwiGLU | SwiGLU |
| Normalization | Pre-RMSNorm | Pre-RMSNorm | Pre-RMSNorm |
| Vocabulary | BPE (32K) | BPE (32K) | Tiktoken (128K) |
| Context | 2K (4096) | 4K | 8K → 128K (3.1) |
| Training Data | 1.0T | 2.0T | 15T+ |
| Training | Fully Open | Fully Open | 405B: 3.8×10^25 FLOPs |

### LLaMA 3 的关键提升
- **Tokenization**: 改用 tiktoken（128K vocab），多语言能力增强
- **数据量**: 15T+ tokens（7× LLaMA 2）
- **代码数据**: 大幅增加代码比例（17%）
- **GQA 全覆盖**: 所有规格模型使用 GQA
- **长上下文**: 3.1 扩展到 128K

## LLaMA 生态影响力

LLaMA 开源后，衍生出庞大的生态：

### 微调变体
- **Alpaca**: 斯坦福基于 LLaMA 1 SFT 微调
- **Vicuna**: 基于 LLaMA 1 对话优化
- **Orca**: 微软基于 LLaMA + GPT-4 蒸馏
- **Zephyr**: 基于 LLaMA/Mistral 的 DPO 训练

### 工具链
- **llama.cpp**: CPU/边缘设备的推理框架（GGUF 格式）
- **Ollama**: 本地模型运行工具
- **vLLM**: 高性能推理框架
- **Hugging Face Transformers**: 官方集成

### 社区衍生模型
- **Nous Research**: Hermes、Capybara 系列
- **OpenBuddy**: 多语言对话
- **Chinese LLaMA**: 中文增强（LoRA 融合）

## LLaMA 405B 的意义
- 世界上最大的完全开源 Dense Transformer
- 128K 上下文
- 在多项基准上接近 GPT-4
- 证明了开源可以追赶闭源

## Source
- [[AI大模型知识点全景图]] — 源文件
- [[AI大模型知识点全景图-home]] — Article Home
- LLaMA: Open and Efficient Foundation Language Models (Meta, 2023)
- LLaMA 2: Open Foundation and Fine-Tuned Chat Models (Meta, 2023)
- The Llama 3 Herd of Models (Meta, 2024)
