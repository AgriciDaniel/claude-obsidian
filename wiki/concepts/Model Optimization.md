---
type: concept
title: "Model Optimization"
created: 2026-07-17
updated: 2026-07-17
tags:
  - concept
  - optimization
  - quantization
  - distillation
  - lora
  - kv-cache
status: seed
address: c-000013
related:
  - "[[AI大模型知识点全景图-home]]"
  - "[[AI Large Model Architecture]]"
  - "[[LLM Training Methods]]"
  - "[[RAG and Retrieval]]"
---

# Model Optimization

大模型优化涵盖推理加速、模型压缩、高效微调、内存优化等多个层面。目标是：用更少的计算资源，获得更好的性能。

## 范式总览

```
推理优化 ──── Quantization ──── GPTQ / AWQ / GGUF
               KV-cache ─────── MQA / GQA / MLA / PagedAttention
               Speculative Decoding ──── Draft + Target 模型
               FlashAttention ──── IO-aware Attention
               Continuous Batching ──── vLLM 核心优化

训练优化 ──── LoRA / QLoRA ──── 参数高效微调
               Knowledge Distillation ──── Teacher → Student
               Model Merging ──── Model Soup / TIES / DARE
               FSDP / DeepSpeed ──── 分布式训练
```

## 1. 量化（Quantization）

将模型权重从 FP16/BF16 降低到更低精度（INT8/INT4/NF4），减少显存占用和推理延迟。

### 主要量化方法

| 方法 | 精度 | 特点 | 适用 |
|------|------|------|------|
| **GPTQ** | 4-bit / 3-bit / 2-bit | 后训练量化、基于 Hessian 矩阵 | GPU 推理 |
| **AWQ** | 4-bit | 激活感知量化、保留重要权重通道的精度 | GPU 推理 |
| **GGUF** | 2-8 bit 可调 | llama.cpp 生态、CPU 友好 | CPU/边缘设备 |
| **bitsandbytes** | 8-bit / 4-bit NF4 | Hugging Face 集成、QLoRA 训练 | 训练时量化 |
| **NF4** | 4-bit | 正态分布最优分桶、QLoRA 使用 | 训练友好 |
| **INT8** | 8-bit | 简单、精度损失小 | 通用场景 |

### 量化对显存的帮助

```
FP16 (16-bit): 1B 参数 ≈ 2GB VRAM
INT8 (8-bit):  1B 参数 ≈ 1GB VRAM
INT4 (4-bit):  1B 参数 ≈ 0.5GB VRAM
NF4 (4-bit):   1B 参数 ≈ 0.5GB VRAM
```

例如：70B 模型 FP16 需要 ~140GB VRAM，4-bit 量化后仅需 ~35GB。

## 2. KV-cache 优化

在自回归生成中，每个推理步的 Key 和 Value 矩阵被缓存（KV-cache）以避免重复计算。随着序列增长，KV-cache 成为显存瓶颈。

### 优化路线图

```
MHA（每个头独立的 K/V） → GQA（分组共享 K/V） → MQA（所有头共享 K/V） → MLA（低秩压缩 K/V）

MHA:    memory_heavy（最占用显存）
GQA:    balance（LLaMA 2/3、Mistral）
MQA:    lightweight（PaLM）
MLA:    ultra_efficient（DeepSeek V2/V3）
```

### PagedAttention（vLLM 核心创新）
- 将 KV-cache 分页管理（类操作系统虚拟内存）
- 消除 KV-cache 碎片化，接近 100% 利用率
- 支持 Copy-on-Write（同一 prompt 的多个生成共享 KV-cache）
- 推理吞吐量提升 2-4×

## 3. 投机解码（Speculative Decoding）

### 原理
- 用小模型（Draft Model）快速生成候选 token 序列
- 用大模型（Target Model）一次性验证候选序列
- 如果验证通过 → 大模型一 forward pass 接受多个 token
- 如果验证失败 → 退回重采样

### 加速比
- 通常 2-3× 的推理加速（无损质量）
- 依赖：小模型和大模型的分布足够接近
- 变体：自投机（Self-Speculative）、Staged Speculative、Medusa

## 4. LoRA / QLoRA（参数高效微调）

### LoRA（Low-Rank Adaptation）
- **核心思想**: 冻结原始权重，在权重矩阵旁插入低秩适配矩阵
- 更新量 ΔW = BA（A 和 B 是两个低秩矩阵）
- 只需训练 A 和 B（通常 rank=8~64）
- 训练参数总量：原始模型的 0.1-1%

### QLoRA
- 4-bit NF4 量化预训练权重
- LoRA 适配器保持 FP16
- 在单张 24GB GPU 上微调 70B 模型成为可能

### LoRA vs 全参数微调

| 维度 | 全参数微调 | LoRA |
|------|-----------|------|
| 训练参数量 | 100% | 0.1-1% |
| 显存需求 | 高（7B 模型 ≈ 56GB） | 低（7B 模型 ≈ 16GB） |
| 训练速度 | 慢 | 快（3-5×） |
| 部署 | 每个任务一个完整模型 | 基础模型 + 多个适配器 |
| 质量 | 高（容量大） | 接近全参数（特定任务） |

## 5. 知识蒸馏（Knowledge Distillation）

- Teacher 模型（大）生成 soft label（概率分布）
- Student 模型（小）学习接近 Teacher 的分布
- **损失函数**: KL 散度（soft target）+ 交叉熵（hard target）
- **温度 (Temperature)**: 控制 soft label 的信息密度

### 蒸馏的变体
- **白盒蒸馏**: 利用中间层的表示（深度蒸馏）
- **黑盒蒸馏**: 只使用 Teacher 的输出（安全蒸馏）
- **蒸馏 + 量化**: 先蒸馏再量化，最小化精度损失

### 代表模型
- Phi-3（微软）: 用 GPT-4 生成的数据训练小模型
- Orca（微软）: 从 GPT-4 蒸馏推理能力
- Gemma（Google）: Gemini 的知识蒸馏产物

## 6. 模型融合（Model Merging）

将多个微调后的模型合并为一个更强模型的技术。

| 方法 | 说明 |
|------|------|
| **Model Soup** | 简单的权重平均 |
| **TIES-Merging** | 解决权重冲突：修剪冗余 → 解决符号冲突 → 平均 |
| **DARE** | 随机丢弃 delta 参数，然后缩放合并 |
| **SLERP** | 球面线性插值合并两个模型 |
| **MoE 融合** | 将多个专家模块组合成 MoE |

## 7. 分布式训练框架

| 框架 | 特点 |
|------|------|
| **DeepSpeed** (Microsoft) | ZeRO 优化器（Stage 1/2/3）、ZeRO-Infinity |
| **FSDP** (PyTorch) | 全分片数据并行、与 torch 原生集成 |
| **Megatron-LM** (NVIDIA) | 张量并行 + 流水线并行 |
| **ColossalAI** | 多种并行策略自动化 |
| **Alpa** (UC Berkeley) | 自动化并行策略搜索 |

## Source
- [[AI大模型知识点全景图]] — 源文件
- [[AI大模型知识点全景图-home]] — Article Home
- LoRA: Low-Rank Adaptation of Large Language Models (Hu et al., 2021)
- QLoRA: Efficient Finetuning of Quantized Language Models (Dettmers et al., 2023)
- GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers (Frantar et al., 2022)
- Fast Inference from Transformers via Speculative Decoding (Leviathan et al., 2022)
- Efficient Memory Management for Large Language Model Serving with PagedAttention (Kwon et al., 2023)
- Model soups: averaging weights of multiple fine-tuned models improves accuracy (Wortsman et al., 2022)
