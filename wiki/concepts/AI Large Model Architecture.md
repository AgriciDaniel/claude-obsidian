---
type: concept
title: "AI Large Model Architecture"
created: 2026-07-17
updated: 2026-07-17
tags:
  - concept
  - ai-architecture
  - transformer
  - moe
status: seed
address: c-000003
related:
  - "[[AI大模型知识点全景图-home]]"
  - "[[LLM Training Methods]]"
  - "[[Model Optimization]]"
  - "[[Model Scaling and Emergence]]"
---

# AI Large Model Architecture

核心架构演变：从 Transformer 到 MoE，从 MHA 到 GQA/MQA，注意力机制的持续优化是大模型架构创新的主线。

## Transformer Foundation（2017）

- **论文**: "Attention Is All You Need" (Vaswani et al., 2017)
- **核心创新**: 自注意力（Self-Attention）替代 RNN 的循环结构
- **两大变体路线**:
  - **Encoder-only**: BERT（双向上下文理解）
  - **Decoder-only**: GPT 系列（自回归生成）— 当前主流

### 核心组件
| 组件 | 功能 | 演化方向 |
|------|------|----------|
| Multi-Head Attention (MHA) | 多头并行注意力计算 | → GQA → MLA |
| Positional Encoding | 注入位置信息 | → RoPE（旋转位置编码） |
| Feed-Forward Network | 非线性变换 | → SwiGLU、MoE FFN |
| Layer Normalization | 训练稳定性 | → Pre-Norm、RMSNorm |
| Residual Connection | 梯度流动 | → Pre-Norm 更优 |

## Attention 机制演变

### MHA → GQA → MQA → MLA

```
MHA（Multi-Head Attention）:
  • 每个头有独立的 K、V 矩阵
  • 参数量大，推理时 KV-cache 占用高
  → 被大多数现代大模型改进

GQA（Grouped Query Attention）:
  • 多个 Query 头共享同一组 Key/Value 头
  • LLaMA 2/3、Mistral 采用
  • 在质量与推理速度间取得平衡

MQA（Multi-Query Attention）:
  • 所有 Query 头共享同一组 Key/Value
  • 推理最快，但质量略降（PaLM 采用）

MLA（Multi-Latent Attention / DeepSeek）:
  • DeepSeek V2 提出：低秩压缩 KV-cache
  • 大幅减少推理内存占用
  • 性能接近 MHA，效率接近 MQA
```

### FlashAttention
- IO-aware 注意力计算算法（Dao et al., 2022）
- 减少 HBM（高带宽内存）读写次数
- FlashAttention-2: 进一步优化并行度
- FlashAttention-3: FP8 支持（Hopper GPU）
- 所有现代大模型训练和推理的事实标准

## Positional Encoding 演变

| 方法 | 特点 | 使用模型 |
|------|------|----------|
| Sinusoidal | 固定频率，无学习参数 | 原始 Transformer |
| Learned | 可训练的位置嵌入 | BERT、GPT-2 |
| RoPE (Rotary PE) | 旋转矩阵编码相对位置 | LLaMA、GLM、Qwen |
| ALiBi | 线性偏置，可外推更长序列 | MPT、Bloom |
| No Positional Encoding | 推理时直接推理位置 | 部分新架构实验 |

**RoPE 是当前主流**，几乎被所有 2023 年后的模型采用。

## MoE（Mixture of Experts）

### 原理
- 将 FFN 层替换为多个"专家"（Expert）子网络
- 路由（Router/Gate）为每个 token 选择 Top-K 专家
- 每个 token 只激活部分参数，推理成本不随总参数量线性增长

### 关键变体

| 方法 | 特点 | 代表模型 |
|------|------|----------|
| Top-2 Routing | 每个 token 激活 2 个专家 | Mixtral 8x7B |
| Top-1 Routing | 每个 token 激活 1 个专家 | 更高效但质量或降 |
| Switch Transformer | 简化 Top-1 + 负载均衡 loss | Google Switch Transformer |
| Soft MoE | 软分配 token 到专家 | Google Soft MoE |
| DeepSeek MoE | 细粒度专家切分 + 共享专家 | DeepSeek V2/V3 |
| Qwen MoE | 激活部分专家 + 路由优化 | Qwen2.5-MoE |

### MoE 的关键挑战
- **负载均衡**: 防止部分专家过载（auxiliary loss）
- **通信开销**: All-to-All 通信（分布式训练）
- **微调困难**: 路由可能崩溃（全部流向少数专家）
- **推理部署**: 需要动态加载、专家并行

## 主流架构对比（2025）

| 模型 | 架构 | Attention | 激活参数 | 总参数量 |
|------|------|-----------|----------|----------|
| GPT-4 | Dense Transformer | MHA（推测） | ~1T | ~1.8T |
| LLaMA 3 | Dense Transformer | GQA | 8B/70B/405B | 8B/70B/405B |
| DeepSeek V3 | MoE Transformer | MLA | 37B | 671B |
| Mixtral 8x7B | MoE Transformer | GQA | 12.9B | 46.7B |
| Qwen 2.5 | Dense/MoE | GQA | 7B-72B | 7B-236B |
| GLM-4 | Dense Transformer | RoPE | 130B | 130B |
| Gemini 1.5 | MoE（推测） | 多头注意力 | 未知 | 未知 |
| Claude 3/4 | Dense（推测） | 自研注意力 | 未知 | 未知 |

## Source
- [[AI大模型知识点全景图]] — 源文件
- [[AI大模型知识点全景图-home]] — Article Home
- Attention Is All You Need (Vaswani et al., 2017)
- Efficient Memory Management for Large Language Model Serving with PagedAttention (Kwon et al., 2023)
