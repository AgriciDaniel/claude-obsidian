---
type: entity
title: "OpenAI GPT Series"
created: 2026-07-17
updated: 2026-07-17
tags:
  - entity
  - openai
  - gpt
  - o1
  - o3
status: seed
address: c-000015
related:
  - "[[AI大模型知识点全景图-home]]"
  - "[[AI Large Model Architecture]]"
  - "[[LLM Training Methods]]"
  - "[[LLM Reasoning Methods]]"
---

# OpenAI GPT Series

OpenAI 从 GPT-1 到 GPT-4o/o1/o3 的模型进化史，是大模型领域最关键的发展线索。

## 模型进化时间线

| 模型 | 发布时间 | 参数量 | 关键创新 |
|------|----------|--------|----------|
| GPT-1 | 2018-06 | 117M | Transformer Decoder-only 路线确立 |
| GPT-2 | 2019-02 | 1.5B | Zero-shot 能力、文本生成质量飞跃 |
| GPT-3 | 2020-06 | 175B | In-context learning、Few-shot 能力 |
| GPT-3.5 | 2022-03 | 175B | InstructGPT (SFT + RLHF) |
| GPT-4 | 2023-03 | ~1.8T (推测) | 多模态输入、推理能力大幅提升 |
| GPT-4 Turbo | 2023-11 | ~1.8T | 128K 上下文、更低价格 |
| GPT-4o | 2024-05 | 未公开 | 原生多模态（文本+图像+音频） |
| o1 | 2024-09 | 未公开 | Test-time compute、推理链（隐藏） |
| o3 | 2024-12 | 未公开 | 更强推理、ARC Prize 高分 |
| GPT-4.1 | 2025-04 | 未公开 | 1M 上下文、API 改进 |
| GPT-4.1 nano | 2025-04 | 未公开 | 低价轻量 API 模型 |

## GPT-4 架构（已知信息）

- **架构**: Dense Transformer（推测非 MoE），Decoder-only
- **参数量**: 未公开。业界推测约 1.8T 参数（但可能使用了 MoE 或混合激活）
- **上下文**: 8K（基础版）/ 32K（long context）/ 128K（Turbo）
- **训练**: SFT + RLHF (PPO)，Alignment 训练的标杆
- **多模态**: GPT-4V（视觉输入），GPT-4o（原生多模态）

## o1 / o3 推理模型

### o1（2024-09）
- 在推理时内部产生推理链（Chain-of-Thought）
- 推理 tokens 对用户隐藏（安全性、竞争力原因）
- AIME（数学竞赛）：GPT-4 得分 ~12%，o1 ~74%
- GPQA（科学推理）：o1 达到人类 PhD 水平
- **推理预算控制**: o1-preview（低）→ o1（中）→ o1-pro（高）

### o3（2024-12）
- ARC-AGI 基准：o3 得分 87.5%（人类 85%）
- AIME 2024：o3 接近满分
- 计算预算：高算力模式比低算力模式多 100× 计算
- 标志着 Test-time compute scaling 成为现实

## API 产品线（2025）

| 模型 | 特点 | 定价（比 GPT-4 低 90%+） |
|------|------|--------------------------|
| GPT-4.1 | 1M 上下文、编码能力强 | 输入 $2/M tokens |
| GPT-4.1 mini | 小模型版 | 输入 $0.4/M tokens |
| GPT-4.1 nano | 最便宜 | 输入 $0.1/M tokens |
| o3 | 最强推理 | 按推理层级定价 |
| o4-mini | 快速推理 | 较低价格 |

## Source
- [[AI大模型知识点全景图]] — 源文件
- [[AI大模型知识点全景图-home]] — Article Home
- Attention Is All You Need (Vaswani et al., 2017)
- Language Models are Few-Shot Learners (GPT-3, Brown et al., 2020)
- Training language models to follow instructions with human feedback (InstructGPT, OpenAI, 2022)
- GPT-4 Technical Report (OpenAI, 2023)
- Learning to Reason with LLMs (OpenAI o1, 2024)
