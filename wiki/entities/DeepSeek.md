---
type: entity
title: "DeepSeek"
created: 2026-07-17
updated: 2026-07-17
tags:
  - entity
  - deepseek
  - reasoning
  - moe
  - chinese-ai
status: seed
address: c-000017
related:
  - "[[AI大模型知识点全景图-home]]"
  - "[[Chinese AI Model Ecosystem]]"
  - "[[LLM Training Methods]]"
  - "[[LLM Reasoning Methods]]"
---

# DeepSeek

DeepSeek（深度求索）是由幻方量化投资团队创立的 AI 公司。凭借一系列技术突破（MoE 架构、GRPO 训练、极低的训练成本），成为 2024-2025 年中国大模型的技术标杆。

## 模型时间线

| 模型 | 发布时间 | 参数 | 核心创新 |
|------|----------|------|----------|
| DeepSeek LLM | 2023-11 | 7B/67B | 首个通用模型 |
| DeepSeek-V2 | 2024-05 | 236B (21B active) | MLA（Multi-Latent Attention）大幅降低 KV-cache |
| DeepSeek-Coder | 2024-06 | 1.3B-33B | 代码专用模型 |
| DeepSeek-V2.5 | 2024-09 | 236B | 通用 + 代码能力融合 |
| DeepSeek-V3 | 2024-12 | 671B (37B active) | MoE 架构、极低的训练成本 |
| DeepSeek-R1 | 2025-01 | 671B | 推理模型、GRPO、开源推理模型标杆 |

## 核心技术突破

### 1. Multi-Latent Attention（MLA）
- DeepSeek V2 提出
- 用低秩压缩（Latent）表示 KV-cache
- **效果**: KV-cache 占用减少 90%+，推理成本大幅降低
- 比 GQA/MQA 更激进的内存优化

### 2. DeepSeek MoE 架构
- 细粒度的专家切分
- 共享专家 + 路由专家的混合设计
- 路由负载均衡：专家负载保持均匀
- 辅助 loss 控制负载

### 3. DeepSeek-V3 训练效率
- **训练成本仅 ~$5.6M**（约 GPT-4 的 1/10）
- 2048 块 GPU，训练约 2 个月
- 14.8T tokens 训练数据
- 创新点：FP8 混合精度训练、多 token 预测（MTP）

### 4. GRPO（Group Relative Policy Optimization）
- 用于训练 DeepSeek-R1 推理模型
- **不依赖 Reward Model**：用组内对比替代人工偏好
- **不依赖人工标注**：用规则（如答案是否正确）自动评分
- 大幅降低对齐成本

## DeepSeek-R1 的意义

- **开源推理模型标杆**: 接近 o1 的推理能力，完全开源
- **关键能力**:
  - 数学：接近 o1（AIME/MATH）
  - 代码：接近 GPT-4
  - 支持 32K+ 推理 tokens
- **成本**: 推理成本约为 o1 的 1/10
- **冲击**: 证明了"低成本 + 开源"可以接近闭源最先进水平

## 产品线

| 产品 | 类型 | 特点 |
|------|------|------|
| DeepSeek Chat | 对话助手 | 免费、长上下文 |
| DeepSeek API | API 服务 | 极低价格（行业最低之一） |
| DeepSeek R1 | 推理 API | 按推理层级定价 |

## Source
- [[AI大模型知识点全景图]] — 源文件
- [[AI大模型知识点全景图-home]] — Article Home
- DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model (DeepSeek, 2024)
- DeepSeek-V3 Technical Report (DeepSeek, 2024)
- DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning (DeepSeek, 2025)
