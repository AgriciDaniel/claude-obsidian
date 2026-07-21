---
type: concept
title: "Multimodal AI"
created: 2026-07-17
updated: 2026-07-17
tags:
  - concept
  - multimodal
  - vision
  - text-to-image
  - vlm
status: seed
address: c-000007
related:
  - "[[AI大模型知识点全景图-home]]"
  - "[[AI Large Model Architecture]]"
  - "[[LLM Training Methods]]"
---

# Multimodal AI

多模态 AI 是 LLM 从"语言模型"进化为"世界模型"的关键路径。涉及视觉、听觉、语音等多模态的理解与生成。

## 模式分类

| 模态 | 理解 (Understanding) | 生成 (Generation) |
|------|---------------------|-------------------|
| **文字 + 图像** | VLM（视觉语言模型） | Text-to-Image (T2I) |
| **文字 + 视频** | 视频理解 | Text-to-Video (T2V) |
| **文字 + 语音** | 语音识别 (ASR) | Text-to-Speech (TTS) |
| **文字 + 音频** | 音频理解 | Text-to-Audio |

## 视觉语言模型（VLM）

### 架构模式
```
┌────────┐    ┌───────────┐    ┌────────┐
│  Image  │ → │  Visual   │ → │  LLM   │ → Text
│ Encoder │   │  Projector│   │        │
└────────┘    └───────────┘    └────────┘
```

**关键组件:**
1. **视觉编码器**: CLIP ViT、SigLIP、DINOv2（图像 → 特征向量）
2. **连接器/投影器**: MLP、Q-Former、Resampler（特征对齐到 LLM 的嵌入空间）
3. **LLM 骨干**: Qwen2、LLaMA、Gemini（融合文本和视觉特征）
4. **输出**: 文本、Bounding Box、分割掩码

### 代表模型

| 模型 | 视觉编码器 | 连接器 | LLM 骨干 | 特点 |
|------|-----------|--------|----------|------|
| **CLIP** | ViT | - | - | 文本-图像对比学习，零样本分类基础 |
| **LLaVA** | CLIP ViT | MLP | LLaMA/Vicuna | 最简单的 VLM，效果好 |
| **LLaVA-NeXT** | CLIP ViT | MLP | LLaMA 3 | 动态高分辨率支持 |
| **Qwen-VL** | CLIP ViT | Q-Former | Qwen | 中英双语 VLM |
| **GPT-4V/4o** | 未公开 | 未公开 | GPT-4 | 多模态能力标杆 |
| **Claude 3.5 Vision** | 未公开 | 未公开 | Claude | 强视觉推理 |
| **Gemini 1.5 Pro** | 原生多模态 | 原生 | Gemini | 原生多模态训练 |
| **CogVLM** | ViT | 深度融合 | GLM 系列 | 视觉-语言深度融合 |

### 核心技术问题
- **高分辨率输入**: 如何处理超分辨率图像？切片？压缩？
- **细粒度理解**: OCR、表格、图表、文档分析
- **多图像/视频理解**: 跨帧推理、时序理解
- **幻觉**: VLM 比纯文本 LLM 更容易产生视觉幻觉

## Text-to-Image（T2I）

| 模型 | 类型 | 特点 |
|------|------|------|
| **DALL-E 3** (OpenAI) | Diffusion Transformer | 文本理解强，细节丰富 |
| **Stable Diffusion 3** | MM-DiT | 开源、可本地部署、ControlNet 生态 |
| **Midjourney V6** | Diffusion | 艺术风格最好，控制力有限 |
| **Flux** (Black Forest Lab) | Diffusion Transformer | 2024 年新秀，质量堪比 Midjourney |
| **Imagen 3** (Google) | Diffusion | 文本理解强 |
| **SDXL / SDXL Turbo** | Latent Diffusion | 渐进/快速生成 |

### 评估维度
- 文本-图像一致性（是否准确跟随 prompt）
- 图像质量（美学、清晰度、构图）
- 风格多样性
- 文字渲染（生成图像中的文字：多数模型仍较弱）

## Text-to-Video（T2V）

| 模型 | 公司 | 特点 |
|------|------|------|
| **Sora** | OpenAI | 高质量、物理世界理解、DiT 架构 |
| **Kling** | 快手（Kuaishou） | 国内顶级，中英文支持好 |
| **Vidu** | 生数科技（Shengshu） | 清华大学背景，高一致性 |
| **Gen-3 / Gen-3 Alpha** | Runway | 专业级视频工具集成 |
| **Pika 2.0** | Pika Labs | 易用、社区活跃 |
| **Emu Video** | Meta | 两阶段生成：图像 → 动画 |

### 关键挑战
- 时序一致性（长视频中保持角色/场景一致）
- 物理模拟（重力、碰撞、光照的准确性）
- 生成速度（视频生成远慢于图像生成）
- 运动合理性（避免畸形运动）

## Text-to-Speech & Voice

| 模型 | 特点 |
|------|------|
| **ElevenLabs** | 音色自然、情感丰富、多语言 |
| **CosVoice** (字节跳动) | 中文效果好、音色克隆 |
| **Fish Speech** | 开源 TTS，多语言 |
| **Bark** (Suno) | 开源，支持笑声/叹息等非语言声音 |
| **GPT-4o Voice** (OpenAI) | 端到端语音对话、情感理解 |
| **Whisper** (OpenAI) | 语音识别标杆 |

## 多模态的融合路线

### 拼接式（当前主流）
- 独立的模态编码器 + LLM 骨干
- 优势：训练高效，可复用已有 LLM
- 代表：LLaVA、Qwen-VL、GPT-4V

### 原生多模态（未来方向）
- 从零训练统一模型，所有模态共享表示空间
- 优势：跨模态无损融合
- 代表：Gemini 原生多模态、GPT-4o（推测）

## Source
- [[AI大模型知识点全景图]] — 源文件
- [[AI大模型知识点全景图-home]] — Article Home
- CLIP: Learning Transferable Visual Models From Natural Language Supervision (OpenAI, 2021)
- LLaVA: Visual Instruction Tuning (Liu et al., 2023)
- Sora: Video generation models as world simulators (OpenAI, 2024)
