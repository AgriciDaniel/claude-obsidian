---
type: concept
title: "LLM Evaluation"
created: 2026-07-17
updated: 2026-07-17
tags:
  - concept
  - evaluation
  - benchmarks
  - mmlu
  - gsm8k
status: seed
address: c-000010
related:
  - "[[AI大模型知识点全景图-home]]"
  - "[[LLM Training Methods]]"
  - "[[LLM Reasoning Methods]]"
  - "[[Model Alignment and Safety]]"
---

# LLM Evaluation

LLM 评测是衡量模型能力的标尺。典型的评测体系覆盖知识、推理、代码、安全、多模态等维度。

## 评测维度总览

```
知识理解 ───── MMLU、C-Eval、GPQA
数学推理 ───── GSM8K、MATH、AIME
代码生成 ───── HumanEval、MBPP、SWE-bench、BigCodeBench
逻辑推理 ───── BBH、ARC、LogiQA
语言理解 ───── GLUE、SuperGLUE、CLUE
长上下文 ───── Needle-in-a-Haystack、LongBench、L-Eval、RULER
Agent 能力 ──── AgentBench、GAIA、ToolBench
安全评测 ───── TruthfulQA、HHH、RTP、SafetyBench
多模态 ─────── MMMU、MMBench、SEED-Bench、MM-Vet
对话评估 ───── MT-Bench、AlpacaEval、Arena Elo
```

## 核心 Benchmark 详解

### 知识理解
| Benchmark | 说明 | 当前最佳（2025） |
|-----------|------|-----------------|
| **MMLU** | 57 学科多任务，5-shot | GPT-4o ~90% |
| **MMLU-Pro** | MMLU 扩展版，更难的题目 | Claude 4 ~95% |
| **GPQA** | 研究生级科学推理（生物/物理/化学） | o3 ~87%（专家级） |
| **C-Eval** | 中文多学科评测 | Qwen 2.5 ~92% |
| **CMMLU** | 中文 MMLU 扩展 | GLM-4 ~90% |

### 数学推理
| Benchmark | 说明 | 当前最佳 |
|-----------|------|----------|
| **GSM8K** | 小学数学应用题（8.5K 题） | o1 ~97% |
| **MATH** | 高中数学竞赛 | o1 ~95% |
| **AIME 2024** | 美国数学邀请赛（最难） | o3 ~97%（新 SOTA） |
| **AMC** | 美国数学竞赛 | o1 ~80% |

### 代码生成
| Benchmark | 说明 | 当前最佳 |
|-----------|------|----------|
| **HumanEval** | Python 函数生成（164 题） | GPT-4 ~95% |
| **MBPP** | Python 编程问题 | GPT-4 ~85% |
| **SWE-bench Verified** | 真实 GitHub Issue 修复 | Claude 3.5 ~50% (2024) → 更高（2025） |
| **BigCodeBench** | 更复杂的编程任务 | 标杆持续提升 |
| **CodeXGLUE** | 代码补全、翻译、缺陷检测 | |

### 长上下文
| Benchmark | 说明 | 代表模型 |
|-----------|------|----------|
| **Needle-in-a-Haystack** | 在海量文本中找一句话 | Gemini 1.5 Pro (1M tokens) 接近完美 |
| **LongBench** | 多任务长上下文评测 | Kimi k1.5 / Gemini 1.5 |
| **L-Eval** | 长文档 QA、摘要、推理 | 长上下文模型不断刷新 |
| **RULER** | 更严格的长上下文评测 | 发现当前长上下文能力被高估 |

## 评测方法学

### Few-shot vs Zero-shot
- Few-shot: 提供几个示例（通常 3-5 个），能更好地适应任务格式
- Zero-shot: 不给示例，直接测试泛化能力
- 主流：MMLU 用 5-shot，GSM8K 用 8-shot，HumanEval 用 0-shot

### 涌现能力与评测饱和
- 当所有模型在 MMLU 上都达到 90%+，MMLU 不再是区分的评测
- **Benchmark 饱和现象**: 部分基准在顶尖模型上已无区分度
- 新基准不断出现：MMLU-Pro → GPQA → SWE-bench → ARC-AGI

### 评测方法论争议
- **数据污染 (Data Contamination)**: Benchmark 可能出现在训练数据中
- **Cheating**: 模型可能学会"通过考试"而非真正理解
- **多语种偏差**: 主流 Benchmark 以英文为主，非英文模型缺乏公平对比
- **单次 vs 多次采样**: 不同采样策略影响评测结果

## 人类评估

### Chatbot Arena（LMSYS）
- 真实用户匿名对战投票
- Elo 评分系统（类似国际象棋等级分）
- 优点：反映真实用户体验
- 缺点：慢、用户偏好有偏差

### MT-Bench
- 80 道多轮对话测试题
- GPT-4 作为裁判（LLM-as-a-Judge）
- 打分维度：有用性、相关性、准确性、深度、创造力

### AlpacaEval
- 自动评估：用 GPT-4 对比生成回答
- 关注"胜率"而非绝对分数
- 缺点：存在 length bias（GPT-4 倾向于更长的回答）

## 国内评测体系

| Benchmark | 发布方 | 说明 |
|-----------|--------|------|
| **C-Eval** | 上海交大/清华 | 中文多学科评测，52 科目 |
| **CMMLU** | 创新工场 | 中文 MMLU，67 科目 |
| **SuperCLUE** | CLUE 团队 | 综合性中文评测 |
| **FlagEval** | 智源研究院 | 多维度评测平台 |
| **AGIEval** | 微软 | 中文考试为基础的评测 |
| **C-Eval Hard** | C-Eval 扩展 | 更难的中文评测 |

## 评测的局限性

1. **基准不能代表一切**: 在某个 benchmark 上 SOTA 不意味着实际使用更好
2. **仅测试能力下限**: 基准测试的是"最少能力"，不是"最大能力"
3. **静态基准 vs 动态能力**: 模型能力在快速提升，基准需要持续更新
4. **忽略关键维度**: 创造力、常识推理、情感理解的评测远远不够

## Source
- [[AI大模型知识点全景图]] — 源文件
- [[AI大模型知识点全景图-home]] — Article Home
- MMLU: Measuring Massive Multitask Language Understanding (Hendrycks et al., 2020)
- GSM8K: Training Verifiers to Solve Math Word Problems (Cobbe et al., 2021)
- SWE-bench: Can Language Models Resolve Real-World GitHub Issues? (Jimenez et al., 2023)
- Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena (Zheng et al., 2023)
