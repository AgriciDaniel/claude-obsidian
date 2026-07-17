---
type: article-home
title: "AI大模型知识点全景图-home"
source_title: "AI 大模型知识点全景图"
source_url: "file:///Users/ggsk/Desktop/AI相关/AI大模型知识点全景图-73页.pdf"
author: "未知（国内AI知识图谱创作者）"
date_published: "2025"
created: 2026-07-17
updated: 2026-07-17
tags:
  - article-home
  - ai-large-models
  - knowledge-map
status: seed
reading_priority: high
related:
  - "[[AI大模型知识点全景图]]"
  - "[[AI Large Model Architecture]]"
  - "[[LLM Training Methods]]"
  - "[[Model Alignment and Safety]]"
  - "[[Chinese AI Model Ecosystem]]"
sources:
  - "[[.raw/AI大模型知识点全景图-2026-07-17.md]]"
---

# AI 大模型知识点全景图 — Article Home

## 1. 先说结论

**这是一份极其全面的 AI 大模型知识地图（73页全图），值得仔细研读。** 

这份全景图以思维导图的形式，系统性地梳理了 AI 大模型领域的方方面面：从基础架构（Transformer、MoE）到训练方法（预训练、SFT、RLHF、DPO），从主流模型家族（国内外 20+ 系列）到关键技术（RAG、CoT、量化、Agent），从评测基准到安全对齐，再到多模态、产业生态和未来趋势。

**为什么值得读：**
- 覆盖面极广——73页的系统化梳理，几乎涵盖 2024-2025 年大模型领域所有重要方向
- 双重视角——同时覆盖国际（OpenAI、Anthropic、Google、Meta）和国内（DeepSeek、Qwen、GLM、Baichuan 等）生态
- 结构清晰——以思维导图组织，适合作为知识体系建设的骨架
- 时效性好——包含至 2025 年初的最新技术进展（DeepSeek-R1、o1/o3、Claude 4/5 等）

**不足之处：**
- 扫描版 PDF，无文本层，部分细节图片中文字较小
- 部分数据可能截至 2025 年初，对于快速迭代的领域有滞后
- 思维导图形式对深度不够——每个方向点到即止，需结合其他资料深入学习

---

## 2. 目录地图

这份全景图内容极其庞杂。建议按以下顺序阅读，从宏观到微观：

```
├── 第一阶段：俯瞰全局
│   ├── 第 1-5 页：大模型整体架构与分类
│   ├── 第 6-10 页：Transformer 原理与变体
│   └── 第 11-15 页：模型规模与能力涌现
│
├── 第二阶段：训练方法论
│   ├── 第 16-22 页：预训练范式
│   ├── 第 23-28 页：SFT 与指令微调
│   └── 第 29-35 页：RLHF / DPO / GRPO 对齐技术
│
├── 第三阶段：关键技术纵深
│   ├── 第 36-42 页：Prompt Engineering、RAG、CoT
│   ├── 第 43-48 页：量化、蒸馏、LoRA、KV-cache 优化
│   └── 第 49-53 页：Agent、Function Calling、MoA
│
├── 第四阶段：模型生态
│   ├── 第 54-60 页：国际模型家族（GPT、Claude、LLaMA、Gemini、Mistral）
│   ├── 第 61-67 页：国内模型家族（DeepSeek、Qwen、GLM、Baichuan、Yi 等）
│   └── 第 68-70 页：开源 vs 闭源、产业格局
│
└── 第五阶段：安全与未来
    ├── 第 71-72 页：安全对齐、红队测试、Jailbreak
    └── 第 73 页：多模态、AI for Science、未来趋势
```

---

## 3. 像人讲一遍

想象你是一位 AI 研究者，需要向刚入行的朋友介绍整个大模型领域。你会从哪里开始？

**"大模型的核心，是 Transformer 架构 + 海量数据 + 大规模算力这三个要素的化学反应。"**

2007 年，"Attention Is All You Need" 论文提出了 Transformer，它用自注意力机制替代了 RNN 的循环结构，让并行训练成为可能。从此，模型规模的增长呈指数级——从 GPT-1 的 1.17 亿参数到 GPT-4 的万亿级参数，不过 6 年时间。

但大参数不等于大智能。真正的突破来自于三个层面：

**第一层：训练方法的进化。** 早期模型只是做"下一个词预测"（预训练），后来发现需要"教它理解指令"（SFT），再后来发现需要"让它符合人类偏好"（RLHF）。DeepSeek-R1 更进一步，在推理时通过强化学习让模型学会"思考"（GRPO + test-time compute scaling）。o1/o3 系列则把推理时计算推向了新的高度。

**第二层：技术能力的扩展。** 模型不是孤立的。RAG 让模型可以查阅外部知识库，CoT 让模型可以分步推理，Function Calling 让模型可以调用工具和 API，Agent 框架让模型可以自主规划和执行任务。MoE 架构让模型可以在保持高质量的同时控制推理成本。

**第三层：生态的繁荣。** 国际上 OpenAI、Anthropic、Google、Meta、Mistral 各领风骚；国内 DeepSeek、阿里 Qwen、智谱 GLM、百川、零一万物等也推出了极具竞争力的模型。开源生态（LLaMA、Qwen、DeepSeek）让全球研究者都能参与，闭源模型则在持续推动能力上限。

**安全对齐是贯穿这一切的底线。** RLHF、Constitutional AI、红队测试、Jailbreak 防御——这些技术确保模型既有能力又可控。

最后，多模态是未来方向。文本、图像、视频、音频——模型正在从"语言模型"进化为"世界模型"。

---

## 4. 上游与下游

**前置知识（上游）：**
- 深度学习基础：神经网络、反向传播、梯度下降
- NLP 基础：词嵌入、RNN/LSTM、Seq2Seq、Attention 机制
- 概率统计：贝叶斯、最大似然估计
- 编程基础：Python、PyTorch 基本使用

**延伸方向（下游）：**
- 具体模型论文精读（Attention Is All You Need、GPT、LLaMA、DeepSeek 技术报告）
- 动手实践：Hugging Face Transformers、vLLM 部署、LoRA 微调
- 专业方向：AI 安全可解释性、AI Agent 工程、多模态模型训练
- 产业应用：AI 编程助手、AI 搜索、企业级 RAG 系统

---

## 5. 关键概念怎么连起来

```
                         ┌─────────────────────┐
                         │   Transformer 架构   │
                         │ (Attention is All)   │
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
       ┌──────▼──────┐      ┌──────▼──────┐      ┌──────▼──────┐
       │  预训练范式  │      │  MoE 架构   │      │   模型家族   │
       │ (GPT/BERT)   │      │ (混合专家)  │      │ (20+系列)    │
       └──────┬──────┘      └──────┬──────┘      └──────┬──────┘
              │                     │                     │
       ┌──────▼──────┐      ┌──────▼──────┐              │
       │ SFT 指令微调│      │ 推理优化    │              │
       └──────┬──────┘      │ 量化/蒸馏   │              │
              │             │ KV-cache    │              │
       ┌──────▼──────┐      └─────────────┘              │
       │ RLHF/DPO    │                                    │
       │ 对齐训练    │                                    │
       └──────┬──────┘                                    │
              │                                           │
       ┌──────▼───────────────────────────────────────────▼──────┐
       │                   能力层                               │
       │  RAG  │  CoT/ToT  │  Function Calling  │  Agent  │  MoA  │
       └──────┬───────────────────────────────────────────────────┘
              │
       ┌──────▼──────┐      ┌─────────────────────┐
       │   多模态    │      │   安全与对齐         │
       │  VLM/TTS    │      │  红队/Jailbreak      │
       │  T2I/T2V    │      │  Constitutional AI   │
       └─────────────┘      └─────────────────────┘
```

核心关系：
- **Transformer** 是所有大模型的基石 → 衍生出 **GPT**（Decoder-only）和 **BERT**（Encoder-only）两条路线
- **预训练 + SFT + RLHF** 是标准训练流水线，但 **DPO / GRPO** 正在简化对齐过程
- **MoE** 让模型可以更大但推理不更贵 → 被 DeepSeek、Mixtral、Qwen 等广泛采用
- **RAG** 和 **Agent** 是模型能力的"外挂"——前者解决知识更新，后者解决自主执行
- **CoT / o1 系列** 代表"推理时计算"这个新范式——不在训练时花更多算力，而是在推理时

---

## 6. 值得沉淀的 wiki 页面

### Source
- [[AI大模型知识点全景图]] — 源文件摘要

### Concepts
- [[AI Large Model Architecture]] — Transformer 架构详解与变体（MHA/GQA/MQA、MoE）
- [[LLM Training Methods]] — 预训练、SFT、RLHF、DPO、GRPO
- [[Model Alignment and Safety]] — 对齐技术、红队测试、Jailbreak、Constitutional AI
- [[Model Scaling and Emergence]] — Scaling Laws、涌现能力、上下文窗口演进
- [[LLM Reasoning Methods]] — CoT、ToT、ReAct、Reflexion、o1/o3、test-time compute
- [[Multimodal AI]] — VLM、T2I、T2V、TTS、语音
- [[LLM Evaluation]] — 评测基准体系（MMLU、GSM8K、HumanEval、C-Eval 等）
- [[Chinese AI Model Ecosystem]] — 国内大模型生态
- [[AI Agent Systems]] — Agent 框架、Function Calling、MoA
- [[RAG and Retrieval]] — RAG 流水线、Embedding、检索策略
- [[Model Optimization]] — 量化、蒸馏、LoRA/QLoRA、KV-cache 优化、Speculative Decoding
- [[Prompt Engineering]] — 提示词工程方法体系

### Entities
- [[OpenAI GPT Series]] — OpenAI 模型进化史
- [[Anthropic Claude Series]] — Anthropic 与 Claude 系列
- [[DeepSeek]] — DeepSeek 模型家族与 GRPO 创新
- [[Meta LLaMA Series]] — LLaMA 开源生态
- [[Google Gemini Series]] — Gemini 系列
- [[Qwen (Alibaba)]] — 阿里 Qwen 系列
- [[GLM (Zhipu AI)]] — 智谱 GLM/ChatGLM
- [[Moonshot AI (Kimi)]] — Moonshot Kimi k1.5

---

## 7. 待补知识 / 红链候选

以下概念在 PDF 中被提及但尚未在本 wiki 中展开。留作后续建设：

**模型系列（红链）：**
- [[Mistral AI]] — Mistral 7B、Mixtral 8x7B（MoE）
- [[Grok (xAI)]] — xAI Grok 系列
- [[Phi (Microsoft)]] — 微软 Phi 小模型系列
- [[Baichuan]] — 百川智能模型系列
- [[Yi (01.AI)]] — 零一万物 Yi 系列
- [[InternLM]] — 上海 AI Lab InternLM
- [[MiniMax]] — MiniMax 模型系列
- [[ERNIE (Baidu)]] — 百度文心一言 ERNIE
- [[Step (Jieyue Stars)]] — 阶跃星辰 Step 系列

**技术概念（红链）：**
- [[Speculative Decoding]] — 投机解码加速推理
- [[Knowledge Distillation]] — 知识蒸馏技术
- [[Model Merging]] — 模型融合（Model Soup、TIES、DARE）
- [[Quantization]] — GPTQ、AWQ、GGUF 量化方法
- [[PagedAttention]] — vLLM 核心注意力优化
- [[FlashAttention]] — 高效注意力实现
- [[Continuous Batching]] — 持续批处理推理优化

**国内应用层（红链）：**
- [[Doubao (ByteDance)]] — 字节跳动豆包
- [[Hunyuan (Tencent)]] — 腾讯混元
- [[SenseTime SenseNova]] — 商汤日日新

**未来方向（红链）：**
- [[AI for Science]] — AI 在科学发现中的应用
- [[Mechanistic Interpretability]] — 机械可解释性
- [[Activation Steering]] — 激活操控

---

## 8. 后续可问的问题

从这份全景图可以自然延伸出以下问题，供后续深入研究：

1. **Scaling Law 是否已经触及天花板？** 还是说 test-time compute 是新的 scaling 方向？
2. **开源 vs 闭源：** 当前（2026 年中）的格局如何？DeepSeek-R1 的开源策略对闭源模型造成了多大冲击？
3. **安全对齐的困境：** 越 jailbreak 越安全（因为对抗训练），还是越 jailbreak 越危险？
4. **MoE 的极限：** MoE 能扩展到多少专家？路由策略（Top-K、Switch、Soft MoE）哪个更优？
5. **多模态的融合深度：** 是"拼接"（独立的视觉编码器 + LLM）还是"原生多模态"（从零训练统一模型）？
6. **Agent 的安全性：** 自主 Agent 的 Tool Use 权限如何控制？MCP 协议是答案吗？
7. **国内模型与国际模型的差距：** 在哪些维度上已经追平（数学、代码）？哪些维度还有差距（多模态、安全）？
8. **小模型的崛起：** Phi-3、Gemma 等 SLM 在多大程度上可以替代大模型？
9. **RAG vs 长上下文：** 随着上下文窗口扩展到 1M+ tokens，RAG 是否还有必要？
10. **推理时计算的成本：** o1/o3 和 DeepSeek-R1 的推理成本是否可接受？对实际应用有何影响？

---

## 9. 以后怎么查回来

当只记得模糊印象时，以下线索可以帮你找回这篇文章：

- **关键词：** AI 大模型 知识图谱 全景图 Transformer LLM 训练 RLHF MoE 多模态 安全对齐 评测 国内大模型 GPT Claude DeepSeek Qwen
- **文件名模式：** 文件名包含 `AI大模型`、`全景图`、`73页`
- **关联页面：** 所有 concept 和 entity 页面都通过 `related` 字段回链到本 Article Home
- **源文件：** `.raw/AI大模型知识点全景图-2026-07-17.md` 包含完整的内容摘要，是找回本文的最直接路径
- **索引页：** `wiki/index.md` 的 Sources 部分包含本文章的条目
- **日志页：** `wiki/log.md` 的日志条目包含本文章的创建记录

---

## 10. 人类判断区

*此区域预留给你（人类读者）填写自己的判断和思考。AI 不会在此区域写入内容。*

**你认为这份全景图的亮点/不足：**

-

**你关注的重点方向：**

-

**你的后续阅读计划：**

-

---

*此页面由 AI 基于 73 页扫描版 PDF 生成，导入日期 2026-07-17。如有错误或遗漏，欢迎补充修正。*
