---
type: source
title: "AI 大模型知识点全景图"
source_type: scanned_pdf
original_file: "AI大模型知识点全景图-73页.pdf"
date_published: "2025"
created: 2026-07-17
updated: 2026-07-17
pages: 73
language: zh-CN
tags:
  - source
  - ai-large-models
  - knowledge-map
  - chinese-ai
address: c-000002
related:
  - "[[AI大模型知识点全景图-home]]"
  - "[[AI Large Model Architecture]]"
  - "[[LLM Training Methods]]"
  - "[[Model Alignment and Safety]]"
  - "[[Chinese AI Model Ecosystem]]"
topics:
  - Foundation Models
  - LLM Architecture
  - Training Methods
  - Model Families
  - AI Ecosystem
  - Multimodal AI
  - AI Safety
---

# AI 大模型知识点全景图

> 一份 73 页的系统化 AI 大模型知识地图，以思维导图形式覆盖模型架构、训练方法、模型家族、关键技术、多模态、安全对齐、评测与产业生态。
>
> **Article Home:** [[AI大模型知识点全景图-home]]

## Source Details

- **Type:** 扫描版 PDF（图片格式，无文本层）
- **Pages:** 73 页
- **Format:** 思维导图（Knowledge Map / Mind Map）
- **Language:** 中文
- **Coverage Period:** 截至 2025 年初

## Content Structure

此全景图分为六大知识域：

### 1. 基础模型与架构
Transformer 架构详解（Attention、Multi-Head Attention、Positional Encoding）、MoE（混合专家）、模型规模与能力涌现、上下文窗口演进（4K → 8K → 32K → 128K → 1M+）

### 2. 训练方法论
预训练范式（Next-token prediction、Causal LM）、SFT（指令微调）、RLHF（奖励模型 + PPO）、DPO（直接偏好优化）、GRPO（DeepSeek 的组相对策略优化）、Constitutional AI（Anthropic）

### 3. 关键技术
Prompt Engineering（Zero-shot/Few-shot/CoT）、RAG 流水线、Function Calling / Tool Use、量化（GPTQ/AWQ/GGUF）、知识蒸馏、LoRA/QLoRA、KV-cache 优化（MHA→GQA→MQA）、Speculative Decoding、模型融合（Model Soup/TIES/DARE）

### 4. 推理能力增强
Chain-of-Thought、Tree-of-Thought、Graph-of-Thought、Self-Consistency、ReAct、Reflexion、Mixture of Agents、Test-time compute scaling（o1/o3、DeepSeek-R1）

### 5. 模型生态
**国际：** GPT 系列、Claude 系列、LLaMA 系列、Gemini 系列、Mistral 系列、Grok 系列、Phi 系列

**国内：** DeepSeek（V2/V3/R1）、Qwen（1.5/2/2.5）、GLM（130B/4/ChatGLM）、Baichuan（7B/13B/2/3）、Yi（34B/VL/Large）、InternLM（7B/20B/2）、MiniMax、Skywork、ERNIE（文心）、SenseChat（日日新）、Step（阶跃星辰）、Kimi/Moonshot AI

### 6. 安全、评测与未来
Red teaming、Jailbreak 攻防、Content moderation、Watermarking、评测基准体系（MMLU/GSM8K/HumanEval/C-Eval/SWE-bench 等）、多模态视觉语言模型、Text-to-Image/Video/Audio、AI for Science、Scaling Law 的未来

## Key Insights

1. **Transformer 是所有大模型的共享基础**，但架构创新（MoE、GQA、Multi-Latent Attention）正成为差异化竞争点
2. **训练流水线已标准化**：Pre-training → SFT → RLHF/DPO，但 GRPO 和 test-time compute 正在打破这一范式
3. **国内模型在数学和代码上已接近国际水平**，DeepSeek-R1 在推理任务上与 o1 抗衡
4. **RAG 和长上下文不是替代关系**，而是互补——RAG 提供事实性和可更新性，长上下文提供更好的语境理解
5. **开源生态正快速缩小与闭源的差距**，LLaMA + Qwen + DeepSeek 三足鼎立

## Related Wiki Pages

- Article Home: [[AI大模型知识点全景图-home]]
- Concepts: See `related` field above
- Entities: [[OpenAI GPT Series]], [[Anthropic Claude Series]], [[DeepSeek]], [[Meta LLaMA Series]], [[Google Gemini Series]], [[Qwen (Alibaba)]], [[GLM (Zhipu AI)]], [[Moonshot AI (Kimi)]]
