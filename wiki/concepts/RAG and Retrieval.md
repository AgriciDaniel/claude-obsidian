---
type: concept
title: "RAG and Retrieval"
created: 2026-07-17
updated: 2026-07-17
tags:
  - concept
  - rag
  - retrieval
  - embedding
  - vector-database
status: seed
address: c-000012
related:
  - "[[AI大模型知识点全景图-home]]"
  - "[[AI Agent Systems]]"
  - "[[AI Large Model Architecture]]"
  - "[[Model Optimization]]"
---

# RAG and Retrieval

检索增强生成（RAG）是大模型连接外部知识的主要方式。RAG 让 LLM 可以访问训练数据之外的信息，并保持输出的事实性。

## RAG 流水线

```
用户问题
    │
    ▼
┌──────────────┐
│ Query 理解    │ ← 查询改写、分解、扩展
└──────┬───────┘
       │
       ▼
┌──────────────┐    ┌─────────────────┐
│ 检索 (Retrieval)│ → │ 知识库 / 索引     │
│ 稀疏检索/Dense  │   │ 向量库/倒排索引    │
└──────┬───────┘    └─────────────────┘
       │
       ▼
┌──────────────┐
│ 重排序 (Rerank)│ ← 交叉编码器精排 Top-K
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 生成 (Generation) │ ← 注入检索结果到 Prompt
└──────────────┘
```

## 检索策略

### 稀疏检索（Sparse Retrieval）
- **BM25**: 基于词频-逆文档频率，不可学习
- **SPLADE**: 可学习的稀疏检索
- 优势：精确的关键词匹配
- 劣势：语义鸿沟（同义词、近义词无法匹配）

### 密集检索（Dense Retrieval）
- **Embedding 模型**将文本转为向量，用余弦相似度检索
- 代表模型：text-embedding-3（OpenAI）、E5（微软）、BGE（BAAI）、GTE（阿里）
- 优势：语义理解能力强
- 劣势：对罕见实体不敏感、需要向量存储

### 混合检索（Hybrid）
- BM25 + Dense Embedding 加权融合
- 主流策略：稀疏确保查全率，密集确保查准率
- 权重调节：RRF（Reciprocal Rank Fusion）、Learning to Rank

## 重排序（Reranking）

- 第一轮：粗检（Top-100 或 Top-50）
- 第二轮：用交叉编码器（Cross-Encoder）精排
- 代表模型：Cohere Rerank、BGE Reranker、bge-reranker-v2
- 交叉编码器比双编码器（bi-encoder）更准但更慢

## Chunking（文本分块）

| 策略 | 说明 | 适用 |
|------|------|------|
| 固定长度切片 | 按字符/token 数切分 | 通用 |
| 语义分块 | 按段落/主题边界切分 | 质量高但慢 |
| 递归分块 | 从粗到细分块 | LangChain 默认 |
| Agentic Chunking | LLM 决定分块边界 | 最智能但成本高 |

### 分块经验
- 块大小：256-512 tokens（简单问答）或 512-1024 tokens（需要上下文的场景）
- 块重叠：10-20%（避免信息丢失在切分边界）
- 小分块 + 大上下文窗口窗口是一种激进但有效的策略

## Embedding 模型

| 模型 | 维度 | 最大输入 | 特点 |
|------|------|----------|------|
| text-embedding-3-small | 512/1536 | 8191 | 性价比高 |
| text-embedding-3-large | 256/1024/3072 | 8191 | 质量最高 |
| BGE (BAAI) | 1024 | 512/8192 | 中文好、开源 |
| GTE (Alibaba) | 768/1024 | 8192 | 中文好、多语言 |
| E5 (Microsoft) | 1024 | 512 | 通用、高质量 |
| jina-embeddings-v3 | 1024 | 8192 | 多语言、长文本 |
| nomic-embed-text | 768 | 8192 | 开源、本地可用 |

## 高级 RAG 模式

### 1. Query 理解增强
- **查询改写**: 将模糊问题重写为检索友好的形式
- **查询分解**: 将复杂问题分解为子查询
- **HyDE (Hypothetical Document Embeddings)**: 先让 LLM 生成假设的答案，再用答案检索

### 2. 多轮 RAG（Chat RAG）
- 在对话中，当前问题是对话历史相关的
- 需要 Contextual Retrieval：带上对话历史重新检索
- 或 Self-RAG：让模型判断是否需要检索，以及检索结果是否相关

### 3. Agentic RAG
- Agent 自主决定：是否检索、何时检索、用什么检索、如何整合
- RAPTOR: 递归摘要 + 分层检索
- Corrective RAG: 对检索结果进行验证和修正

### 4. Graph RAG
- 用知识图谱替代向量库
- 检索实体 + 关系 + 路径
- 微软 Graph RAG 方案：实体提取 → 社区摘要 → 分层检索
- 优势：跨文档的关系推理

## RAG vs 长上下文

| 维度 | RAG | 长上下文 (128K+) |
|------|-----|-------------------|
| 事实性 | 高（检索到源头） | 中等（可能"丢失中间"） |
| 成本 | 低（只检索相关片段） | 高（处理全部长上下文） |
| 实时性 | 高（随时更新知识库） | 低（静态预训练知识） |
| 实现复杂度 | 较高（需要检索系统） | 低（直接放 prompt） |
| 不受上下文限制 | 是（知识库可任意大） | 否（上下文窗口有限） |

**结论：RAG 和长上下文是互补关系，不是替代关系。**

## Source
- [[AI大模型知识点全景图]] — 源文件
- [[AI大模型知识点全景图-home]] — Article Home
- Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (Lewis et al., 2020)
- Lost in the Middle: How Language Models Use Long Contexts (Liu et al., 2023)
- Graph RAG: Unlocking LLM Discovery on Narrative Private Data (Microsoft, 2024)
