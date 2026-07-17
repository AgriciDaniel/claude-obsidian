---
type: entity
title: "Google Gemini Series"
created: 2026-07-17
updated: 2026-07-17
tags:
  - entity
  - google
  - gemini
  - multimodal
status: seed
address: c-000020
related:
  - "[[AI大模型知识点全景图-home]]"
  - "[[Multimodal AI]]"
  - "[[AI Large Model Architecture]]"
  - "[[Model Scaling and Emergence]]"
---

# Google Gemini Series

Google DeepMind 的 Gemini 系列是 Google 在 AI 大模型领域的最新旗舰。以原生多模态和极致的长上下文（1M tokens）为特色。

## 模型时间线

| 模型 | 发布时间 | 层级 | 关键特性 |
|------|----------|------|----------|
| Gemini 1.0 | 2023-12 | Nano/Pro/Ultra | 首个原生多模态模型 |
| Gemini 1.5 Pro | 2024-02 | Pro | 1M 上下文窗口（突破性） |
| Gemini 1.5 Flash | 2024-05 | Flash | 快速、低成本、1M 上下文 |
| Gemini 2.0 Flash | 2024-12 | Flash | 新一代、Agent 功能 |
| Gemini 2.0 Pro | 2025-02 | Pro | 更强推理能力 |
| Gemini 2.5 Pro | 2025-03 | Pro | 深度推理 + 长上下文 |

## 核心技术特色

### 原生多模态（Native Multimodal）
- 与传统 VLM（视觉编码器 + LLM 拼接）不同
- Gemini 从训练开始就同时处理文本、图像、音频、视频
- **优势**: 跨模态信息融合更好，无信息损失

### 1M 上下文窗口
- Gemini 1.5 Pro 首发 1M token 上下文
- 2025 年进一步扩展到更高长度
- Needle-in-a-Haystack 测试接近完美
- 可处理：整部代码库、数小时的视频、数百页 PDF

### 推理能力（Gemini 2.5）
- Gemini 2.5 Pro 引入类似 o1 的"思考"能力
- 推理时自动选择是否进行深度推理
- 在数学和科学推理上大幅提升

## 产品线

| 层级 | 特点 | 适用场景 |
|------|------|----------|
| **Gemini Ultra** | 旗舰 | 最复杂推理、科研 |
| **Gemini Pro** | 中高端 | 企业级应用、长上下文需求 |
| **Gemini Flash** | 高效快速 | 大规模部署、实时应用 |
| **Gemini Nano** | 端侧模型 | Pixel 手机设备端推理 |

## 关键能力

- **长上下文**: 行业最强（1M+ tokens），唯一能处理整本小说的模型系列
- **多模态**: 原生多模态，文本、图像、音频、视频统一处理
- **Google 生态集成**: Google Workspace、Search、Android
- **Agent 能力**: Gemini 2.0 Flash 引入 Tool Use 和 Agent 框架

## Source
- [[AI大模型知识点全景图]] — 源文件
- [[AI大模型知识点全景图-home]] — Article Home
- Gemini: A Family of Highly Capable Multimodal Models (Google DeepMind, 2023)
- Gemini 1.5: Unlocking multimodal understanding across millions of tokens of context (Google DeepMind, 2024)
