---
type: entity
title: "Anthropic Claude Series"
created: 2026-07-17
updated: 2026-07-17
tags:
  - entity
  - anthropic
  - claude
  - constitutional-ai
status: seed
address: c-000016
related:
  - "[[AI大模型知识点全景图-home]]"
  - "[[AI Large Model Architecture]]"
  - "[[Model Alignment and Safety]]"
  - "[[LLM Training Methods]]"
---

# Anthropic Claude Series

Anthropic 是由前 OpenAI 员工 Dario Amodei 和 Daniela Amodei 联合创立的 AI 安全公司。Claude 系列以安全对齐（Constitutional AI）著称。

## 模型进化时间线

| 模型 | 发布时间 | 关键特性 |
|------|----------|----------|
| Claude 1 | 2023-03 | 首批以安全为中心的大模型 |
| Claude 2 | 2023-07 | 100K 上下文、代码能力增强 |
| Claude 2.1 | 2023-11 | 200K 上下文、降低幻觉 |
| Claude 3 Haiku | 2024-03 | 快速、便宜、接近 GPT-3.5 |
| Claude 3 Sonnet | 2024-03 | 中端、编码强 |
| Claude 3 Opus | 2024-03 | 最强（MMLU 86.8%，接近 GPT-4） |
| Claude 3.5 Sonnet | 2024-06 | 编码能力显著提升、性价比之王 |
| Claude 3.5 Haiku | 2024-10 | 快速版更新 |
| Claude Opus 4 | 2025-03 | MMLU-Pro ~95%、SWE-bench 领先 |
| Claude Sonnet 4 | 2025-03 | 中高端、编码和推理增强 |
| Claude 5* | 2025 | 最新一代（在发布时） |

## 核心技术特色

### Constitutional AI（宪法 AI）
- 核心理念：用一套宪法原则（principles）指导模型行为
- 不依赖大量人工标注偏好
- **两阶段训练**:
  1. SL-CAI：模型自我修订 → SFT 训练
  2. RL-CAI：模型生成修订对 → 偏好学习
- 优势：更可解释的对齐

### Claude 的关键优势
- **长上下文**: Claude 2 首发 100K，Claude 3 支持 200K
- **安全对齐**: Constitutional AI 使 Claude 在安全评测中通常领先
- **编码能力**: Claude 3.5 Sonnet 在 SWE-bench 上曾长期领先
- **诚实性**: 比其他模型更倾向于说"不知道"而非幻觉
- **Harmlessness**: 拒绝有害请求的同时，不过度拒绝

## 产品线结构

### 按能力分层（Claude 3+）

```
Opus（旗舰）: 最强推理、分析、长文本理解
Sonnet（中端）: 编码、写作、性价比最优
Haiku（轻量）: 快速响应、性价比高、适合大规模调用
```

## 关键能力对比

| 维度 | Claude 3 Opus | Claude 3.5 Sonnet | GPT-4o | Gemini 1.5 Pro |
|------|--------------|-------------------|--------|----------------|
| MMLU | 86.8% | 88.7% | 88.7% | 85.9% |
| GSM8K | 95% | 96% | 97% | 94% |
| HumanEval | 84.9% | 93.7% | 92% | 86% |
| 上下文 | 200K | 200K | 128K | 1M |
| 安全评分 | 领先 | 领先 | 一般 | 一般 |

## Source
- [[AI大模型知识点全景图]] — 源文件
- [[AI大模型知识点全景图-home]] — Article Home
- Constitutional AI: Harmlessness from AI Feedback (Anthropic, 2022)
- The Claude Model Family (Anthropic, 2024)
