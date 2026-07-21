---
type: concept
title: "Model Scaling and Emergence"
created: 2026-07-17
updated: 2026-07-17
tags:
  - concept
  - scaling
  - emergence
  - scaling-laws
  - context-window
status: seed
address: c-000011
related:
  - "[[AI大模型知识点全景图-home]]"
  - "[[AI Large Model Architecture]]"
  - "[[LLM Training Methods]]"
  - "[[LLM Reasoning Methods]]"
---

# Model Scaling and Emergence

模型规模与能力涌现的关系是大模型最核心的科学问题之一。

## Scaling Laws（规模定律）

### 原始 Scaling Laws（Kaplan et al., 2020, OpenAI）
- **核心发现**: LLM 的性能（loss）随**模型参数、数据量、算力**的幂律增长而可预测地提升
- **关键公式**: $$L(N, D) \propto N^{-\alpha} + D^{-\beta} + C$$
  - N = 模型参数，D = 数据量
  - α ≈ 0.076, β ≈ 0.103（原始估计）
  - 模型应同时 scaling 参数和数据

### Chinchilla Scaling Laws（Hoffmann et al., 2022, DeepMind）
- 修正了原始 Scaling Laws：对于给定的算力预算，**数据和参数应同步扩展**
- **Chinchilla Optimal**: 每增加 1 个参数，需要约 20 个训练 token
- 核心影响：很多大模型"数据不足"（over-parameterized）

### 实际影响
| 模型 | 参数量 | 训练 Tokens | 是否 Chinchilla Optimal |
|------|--------|-------------|-------------------------|
| GPT-3 | 175B | 300B | 否（数据不足） |
| LLaMA 1 | 65B | 1.0T | 接近（数据更多） |
| LLaMA 3 | 405B | 15T+ | 是（大量数据） |
| DeepSeek V3 | 671B (37B active) | 14.8T | 是 |
| Qwen 2.5 | 72B | 18T+ | 是 |

## 涌现能力（Emergent Abilities）

涌现能力是指：**模型达到一定规模后突然出现的、小模型完全没有的能力**。

### 主要涌现能力
| 能力 | 涌现阈值 | 说明 |
|------|----------|------|
| **上下文学习 (ICL)** | ~1B params | 从上下文示例中学习新任务 |
| **思维链 (CoT)** | ~100B params | 多步推理能力 |
| **指令遵循** | ~10B params | 理解并执行复杂指令 |
| **代码生成** | ~10B params | 生成可用代码 |
| **多语言泛化** | ~1B params | 跨语言能力 |
| **工具使用** | ~10B+ params | 调用外部工具 |

### 涌现的争议
- **是真正的涌现还是评测方式导致的假象？**
  - 使用连续指标（如 Brier Score）时，许多"涌现"变得连续可预测
  - 涌现可能部分来自**评测的离散性**（0/1 判定模糊边界为"突然出现"）
- 但部分能力（如 CoT）在参数低于 100B 时确实几乎观察不到

## 上下文窗口演进

| 时间 | 代表模型 | 上下文长度 | 技术 |
|------|----------|-----------|------|
| 2017 | Transformer | 512 | 固定位置编码 |
| 2018-2021 | GPT/BERT | 512-2048 | 位置编码限制 |
| 2022 | GPT-3.5 | 4K (4096) | OpenAI 首次 |
| 2023 | GPT-4 | 8K / 32K | 改进位置编码 |
| 2023 | Claude 2 | 100K | Anthropic |
| 2024 | GPT-4 Turbo | 128K | 进一步扩展 |
| 2024 | Gemini 1.5 Pro | 1M (1,048,576) | Google | 
| 2024 | Kimi/Moonshot | 200K+ | 长上下文专业户 |
| 2024 | Claude 3 | 200K | Anthropic |
| 2025 | Gemini 1.5 Flash | 1M | Google |
| 2025 | GPT-4.1 | 1M | OpenAI |
| 2025+ | 无限上下文？ | 实验性 | Ring Attention 等 |

### 长上下文的关键技术
- **RoPE 扩展**: NTK-aware、YaRN、PI（位置编码外推）
- **Ring Attention**: 分布式注意力计算（突破单 GPU 内存限制）
- **滑动窗口**: StreamingLLM、Window Attention（固定窗口）
- **压缩**: LLMLingua、Selective Context（减少冗余 token）
- **RAG + 长上下文**: 互补策略

### 长上下文的实际局限
- "Needle-in-a-Haystack" 测试之外，长上下文的真实利用率仍不高
- **Lost-in-the-Middle**: 模型倾向于使用开头和结尾的信息，忽略中间
- 推理成本与上下文长度成正比（注意力 O(n²)）
- 即使能处理长文本，提取精确信息的准确率也随长度下降

## Scaling 的新方向

### 超越参数 Scaling
1. **数据 Scaling**: 高质量数据比大参数更重要（Chinchilla 法则）
2. **训练计算 Scaling**: 更多训练数据和更长训练（而非更大的模型）
3. **推理时计算 Scaling**: o1/o3 风格 — 推理时花更多计算

### 关于 Scaling Law 是否见顶的争论
- **"Scaling is all you need" 派**: 更大模型 + 更多数据 = 更强能力
- **"Scaling law 已显疲态" 派**: 收益递减，架构创新和数据质量更关键
- **现实**: 两者都正确。Scaling 还在产生收益，但收益递减已出现
- **新焦点**: Test-time compute scaling 作为新的增长维度

## Source
- [[AI大模型知识点全景图]] — 源文件
- [[AI大模型知识点全景图-home]] — Article Home
- Scaling Laws for Neural Language Models (Kaplan et al., 2020)
- Training Compute-Optimal Large Language Models (Hoffmann et al., 2022, Chinchilla)
- Are Emergent Abilities of Large Language Models a Mirage? (Schaeffer et al., 2023)
