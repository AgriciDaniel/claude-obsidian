---
type: concept
title: "LLM Training Methods"
created: 2026-07-17
updated: 2026-07-17
tags:
  - concept
  - training
  - pretraining
  - sft
  - rlhf
status: seed
address: c-000004
related:
  - "[[AI大模型知识点全景图-home]]"
  - "[[Model Alignment and Safety]]"
  - "[[AI Large Model Architecture]]"
  - "[[Model Optimization]]"
---

# LLM Training Methods

大模型标准训练流水线：**Pre-training → SFT → RLHF/DPO**。三个阶段各有不同的目标、数据和计算要求。

## 三阶段流水线总览

```
第一阶段：预训练（Pre-training）
  目标：学习语言知识、世界知识
  数据：海量无标注文本（万亿 tokens）
  损失：Next-token prediction (NTP) / Causal LM
  算力：最大（万卡集群 × 数月）
  ↓

第二阶段：指令微调（SFT / Instruction Tuning）
  目标：学会遵循指令、对话能力
  数据：高质量指令-回复对（百万级）
  损失：NTP（但只在回复部分计算）
  算力：中（单卡或小集群 × 数天）
  ↓

第三阶段：对齐（Alignment）
  目标：符合人类偏好、安全无害
  方法：RLHF / DPO / GRPO / Constitutional AI
  数据：人类偏好标注 / AI 偏好标注
  算力：中低（主要是推理开销）
```

## 1. 预训练（Pre-training）

### 目标函数
- **Next-token prediction**: 给定前 t 个 token，预测第 t+1 个 token
- **Causal masking**: 只能看到左侧上下文（auto-regressive）
- **上下文长度逐渐扩展**: 2K → 4K → 8K → 32K → 128K → 1M+

### 关键方法
- **学习率调度**: Warmup + Cosine decay
- **批次大小调度**: 逐渐增大 batch size
- **数据配比**: 网页（CommonCrawl）/ 书籍 / 代码 / 学术论文的混合比例
- **数据去重**: MinHash、模糊去重减少记忆化
- **Pile / RedPajama / Dolma**: 常见预训练数据集

### 持续预训练（Continual Pre-training）
- 在通用预训练后，用领域数据继续训练
- 用于：代码增强、领域适应、知识更新
- 风险：灾难性遗忘（通过 replay 缓解）

## 2. 监督微调（SFT / Instruction Tuning）

### 数据要求
- **格式**: `(instruction, input, output)` 三元组或对话多轮数据
- **关键维度**: 多样性 > 数量、质量 > 数量
- **常见数据集**: OpenAssistant、ShareGPT、LIMA（"Less Is More for Alignment"）
- **合成数据**: 用强模型（GPT-4、Claude）生成 SFT 数据

### 技巧
- **损失屏蔽（Loss Masking）**: 只计算 assistant 回答部分的 loss，不计算用户输入 / 系统提示
- **多轮对话打包**: 将多轮对话组织成统一格式（如 ChatML）
- **数据配比**: 通用指令 + 代码 + 数学 + 工具的混合比例

## 3. RLHF（Reinforcement Learning from Human Feedback）

### 标准流程（InstructGPT/GPT-4）
```
Step 1: SFT 微调 → 得到 SFT 模型
Step 2: 训练奖励模型（Reward Model, RM）
  输入: prompt + response
  输出: 一个标量分数
  数据: 人类对多个回答的排序
  损失: Bradley-Terry 偏好模型

Step 3: PPO 强化学习
  策略: SFT 模型（需要微调的）
  奖励: Reward Model 的打分
  约束: KL 散度惩罚（防止偏离 SFT 太远）
  价值模型: 与策略共享部分参数
```

### PPO 训练的关键问题
- Reward hacking：模型学会迎合 RM 而非真正变好
- KL 散度系数需要仔细调节
- 训练不稳定（PPO 本身就有这个问题）
- 需要同时加载 4 个模型（策略、参考、奖励、价值）

## 4. DPO（Direct Preference Optimization）

### 核心思想
- **不需要单独训练 Reward Model**
- 直接用偏好对 `(chosen, rejected)` 优化策略
- 数学等价：将 RLHF 的 two-stage 合并为 one-stage

### DPO vs RLHF

| 维度 | RLHF | DPO |
|------|------|-----|
| 复杂度 | 高（4 个模型） | 低（2 个模型） |
| 稳定性 | 较差 | 较好 |
| 数据效率 | 可处理任意偏好 | 需要成对偏好数据 |
| 可解释性 | 可分析 RM 行为 | 隐式 reward |
| 主流采用 | GPT-4、Claude | LLaMA 2/3、Zephyr |

### 变体
- **KTO**: 不需要成对数据，只需要"好/坏"二分类信号
- **ORPO**: 将 SFT + DPO 合并为一步
- **SimPO**: 用生成概率替代 reward model
- **IPO**: 信息论角度的偏好优化

## 5. GRPO（Group Relative Policy Optimization）

### DeepSeek 的创新
- 用于训练 DeepSeek-R1 推理模型
- **核心思路**: 用一组采样输出的相对质量替代 Reward Model
- 不需要额外训练 RM，降低训练成本

### GRPO 流程
```
1. 对同一个 prompt 采样 N 个输出
2. 用规则 / 评分函数对 N 个输出打分（如：数学答案是否正确）
3. 用组内相对优劣计算优势函数 Advantage
4. PPO 风格的策略更新，但去掉价值模型
5. KL 散度约束仍在
```

### 关键优势
- 不需要人工标注偏好
- 不需要训练 Reward Model
- 规则评分（如代码是否通过测试、数学答案是否正确）可自动生成
- 特别适合**推理任务**（数学、代码、逻辑推理）

## 6. Constitutional AI（Anthropic）

Anthropic 的替代对齐方法：

1. **阶段一：监督学习**（SL-CAI）
   - 用 AI 模型根据宪法原则生成无害回复
   - 训练 SFT 模型

2. **阶段二：强化学习**（RL-CAI）
   - 替代 RLHF 中的 RM 训练
   - AI 自我修订：模型生成回复 → 根据宪法原则自我评价修改 → 偏好对（修改前 vs 修改后）
   - 用这个偏好对训练偏好模型（或直接 DPO）

**优势**: 不依赖人类标注偏好，对齐更可解释

## 训练数据配比经验法则

| 模型 | 预训练 tokens | SFT 数据 | 对齐方法 |
|------|---------------|----------|----------|
| GPT-3 | 300B | - | - |
| LLaMA 1 | 1.0T | - | - |
| LLaMA 2 | 2.0T | ~100K | RLHF + DPO |
| LLaMA 3 | 15T+ | ~1M | DPO |
| DeepSeek V3 | 14.8T | - | - |
| Qwen 2.5 | 18T+ | 混合 | RLHF + DPO |
| Phi-3 | 3.3T | 高质量合成 | DPO |

## Source
- [[AI大模型知识点全景图]] — 源文件
- [[AI大模型知识点全景图-home]] — Article Home
- Training language models to follow instructions with human feedback (InstructGPT, OpenAI 2022)
- Direct Preference Optimization: Your Language Model is Secretly a Reward Model (Rafailov et al., 2023)
- Constitutional AI: Harmlessness from AI Feedback (Anthropic, 2022)
- DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning (DeepSeek, 2025)
