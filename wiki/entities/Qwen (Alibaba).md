---
type: entity
title: "Qwen (Alibaba)"
created: 2026-07-17
updated: 2026-07-17
tags:
  - entity
  - qwen
  - alibaba
  - chinese-ai
  - open-source
status: seed
address: c-000018
related:
  - "[[AI大模型知识点全景图-home]]"
  - "[[Chinese AI Model Ecosystem]]"
  - "[[AI Large Model Architecture]]"
  - "[[AI Agent Systems]]"
---

# Qwen (Alibaba)

Qwen（通义千问）是阿里巴巴的通义大模型系列。作为国内全面开源的代表，Qwen 在综合能力、多模态、Agent 生态方面均有出色表现。

## 模型时间线

| 模型 | 发布时间 | 参数 | 关键特性 |
|------|----------|------|----------|
| Qwen | 2023-08 | 7B/14B/72B | 首个系列，中英双语 |
| Qwen 1.5 | 2024-02 | 0.5B-72B | 更丰富参数规格 |
| Qwen 2 | 2024-06 | 0.5B-72B | 更强推理、32K 上下文 |
| Qwen 2.5 | 2024-09 | 0.5B-72B | 18T+ 训练数据、Agent 增强 |
| Qwen 2.5-Coder | 2024-11 | 1.5B-32B | 代码专项 |
| Qwen 2.5-VL | 2025-01 | 72B | 视觉语言模型 |
| Qwen 2.5-MoE | 2024 | A2.7B-14B | MoE 架构轻量版 |

## 技术特色

### 架构
- Dense Transformer / MoE 两种路线
- GQA (Grouped Query Attention)
- RoPE (Rotary Position Embedding)
- SwiGLU 激活函数

### 开源策略
- Qwen 是国内最积极的开源模型系列之一
- 完整模型权重 + 技术报告
- ModelScope + Hugging Face 双平台发布
- 商业使用需申请

### Agent / Tool Use
- Qwen Agent 框架：Function Calling 原生支持
- Qwen-Agent: 开源智能体框架
- 支持代码解释器、搜索、API 调用

## 多模态路线

| 模型 | 能力 | 基础 |
|------|------|------|
| Qwen-VL | 图像理解、OCR、视觉 QA | Qwen 2.5 |
| Qwen-Audio | 语音理解 | Qwen |
| Qwen-VL-Max | 最强视理解 | Qwen 2.5 |

## 关键能力

- **综合能力强**: MMLU ~85%+（72B），中文 C-Eval 领先
- **编码**: Qwen 2.5-Coder 在代码基准上接近 GPT-4
- **长上下文**: 支持 32K-128K tokens
- **Agent**: Tool Use 和 Function Calling 生态完善

## Source
- [[AI大模型知识点全景图]] — 源文件
- [[AI大模型知识点全景图-home]] — Article Home
- Qwen Technical Report (Alibaba, 2023-2025)
- Qwen2.5 Technical Report (Alibaba, 2024)
