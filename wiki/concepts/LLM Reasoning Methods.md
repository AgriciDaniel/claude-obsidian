---
type: concept
title: "LLM Reasoning Methods"
created: 2026-07-17
updated: 2026-07-17
tags:
  - concept
  - reasoning
  - cot
  - test-time-compute
  - o1
status: seed
address: c-000006
related:
  - "[[AI大模型知识点全景图-home]]"
  - "[[AI Large Model Architecture]]"
  - "[[AI Agent Systems]]"
  - "[[LLM Training Methods]]"
---

# LLM Reasoning Methods

大模型推理能力的增强经历了从"更好的提示"到"更聪明的思考方式"再到"推理时计算"的进化。

## 推理方法谱系

```
          思考方式增强                      训练时增强
  ┌─────────────────────┐          ┌─────────────────────┐
  │ CoT (Chain-of-Thought)          │ Process Reward Model │
  │ ToT (Tree-of-Thought)           │ Outcome Reward Model │
  │ GoT (Graph-of-Thought)          │ PRM 训练             │
  │ Self-Consistency                │ RL 训练推理链        │
  │ ReAct                           │                      │
  │ Reflexion                       │  推理时计算增强      │
  │ Self-Ask                        │ ┌──────────────────┐ │
  │ Least-to-Most                   │ │ o1/o3           │ │
  │ Zero-shot CoT                   │ │ DeepSeek-R1     │ │
  │                                 │ │ o1-pro          │ │
  │                                 │ │ QwQ (Qwen推理)  │ │
  └─────────────────────┘          │ │ Gemini Thinking │ │
                                    │ └──────────────────┘ │
                                    └─────────────────────┘
```

## 1. Chain-of-Thought（CoT）

### 起源
- "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" (Wei et al., 2022)

### 原理
- 要求模型在给出最终答案前，生成中间推理步骤
- 将复杂推理问题分解为多个简单步骤

### 变体
| 变体 | 描述 | 适用场景 |
|------|------|----------|
| **Zero-shot CoT** | 加 "Let's think step by step" | 通用 |
| **Few-shot CoT** | 给出推理链示例 | 需要格式控制 |
| **Auto-CoT** | 自动生成推理示例 | 无需人工标注 |
| **Least-to-Most** | 先分解子问题，逐步解决 | 复杂组合推理 |

### 效果
- 数学模型（GSM8K）：55% → 95%+（CoT 带来的提升）
- 在知识类任务（MMLU）上提升较小
- 在需要多步逻辑推理的任务上提升显著

### 局限性
- 增加输出长度（Token 成本 × 3-10 倍）
- 模型可能产生"合理但不正确"的推理
- 对不需要推理的任务可能有副作用

## 2. Tree-of-Thought（ToT）

### 核心思想
- 将推理过程视为**树状搜索**
- 在每个推理步上生成多个可能的后续分支
- 使用 BFS/DFS + 评估函数探索最优路径

### 相比 CoT 的优势
- 探索多条推理路径（发现最优路径）
- 可回溯错误分支（纠错能力）
- 有前瞻性（评估"这条路径的潜力"）

### 局限
- Token 消耗巨大（探索所有分支）
- 搜索策略（BFS/DFS 深度、宽度）需要调参
- 评估函数的质量直接影响效果

## 3. 进一步的推理增强

### Graph-of-Thought（GoT）
- 将推理建模为**有向图**：允许从任意状态跳转到任意其他状态
- 支持"合并"操作：多个推理链的结论可以合并
- 比 ToT 更灵活但更复杂

### Self-Consistency
- 多次采样推理链（temperature > 0）
- 通过投票/多数决策聚合多个推理路径
- 简单但有效：提升数学推理 5-15%

### ReAct（Reasoning + Acting）
- 推理 + 工具调用循环：Think → Act → Observe → Repeat
- 每次推理（Think）后可以调用工具（Act）获取信息（Observe）
- 为 Agent 模式奠定基础

### Reflexion
- 模型在执行任务后自我评估
- 从错误中学习，在下一轮改进
- Verbal reinforcement learning（语言强化学习）

## 4. 推理时计算（Test-Time Compute Scaling）

### 核心范式转变
- 传统：训练时花算力提高能力 → 推理时固定成本
- 新范式：**推理时也可以花算力**来提高输出质量

### o1 / o3（OpenAI 2024-2025）

**o1 的突破：**
- 在推理时内部产生"思维链"（隐藏的 reasoning tokens）
- 在数学、代码、科学推理上达到 PhD 级别
- GSM8K 接近完美，AIME（数学竞赛）大幅超越 GPT-4
- 技术细节未完全公开，但推测使用了类似 AlphaGo 的 RL 搜索

**o3（2025 进一步升级）：**
- 更高的推理时计算预算
- ARC Prize（抽象推理挑战）达到 87.5%（人类 85%）
- 在 GPQA（研究生级科学推理）上达到专家水平

### DeepSeek-R1

**关键创新：**
- 用 **GRPO**（Group Relative Policy Optimization）训练推理能力
- 不使用人工标注的推理链数据
- 模型自主学会"思考"（internal reasoning chain）
- **开源**: 开源推理模型的标杆

**能力：**
- 数学推理接近 o1
- 代码生成接近 GPT-4
- 支持长推理链（最多 32K reasoning tokens）
- 推理成本低于 o1 约 90%

### 计算预算的调节
- **思考预算 (Think Budget)**: 控制推理时计算的内存量（token 数）
- **最佳 N (Best-of-N)**: 采样 N 个候选，选最佳
- **验证器 (Verifier)**: 对候选输出评分（PRM / ORM）
- **搜索树**: MCTS（Monte Carlo Tree Search）用于推理

## 推理方法选择指南

| 场景 | 推荐方法 | 原因 |
|------|----------|------|
| 简单问答 | 直接生成 | CoT 无益且浪费 token |
| 数学推理 | CoT + Self-Consistency | 性价比最优 |
| 复杂逻辑 | ToT / CoT-SC | 需要探索多条路径 |
| 需要外部信息 | ReAct | 工具调用不可或缺 |
| 高难度推理 | o1 / R1 / QwQ | 推理时计算的收益最大 |
| 自我改进 | Reflexion | 从错误中学习 |

## Source
- [[AI大模型知识点全景图]] — 源文件
- [[AI大模型知识点全景图-home]] — Article Home
- Chain-of-Thought Prompting Elicits Reasoning in Large Language Models (Wei et al., 2022)
- Tree of Thoughts: Deliberate Problem Solving with Large Language Models (Yao et al., 2023)
- DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning (DeepSeek, 2025)
- ReAct: Synergizing Reasoning and Acting in Language Models (Yao et al., 2022)
