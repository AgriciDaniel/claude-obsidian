---
type: concept
title: "Prompt Engineering"
created: 2026-07-17
updated: 2026-07-17
tags:
  - concept
  - prompt
  - prompting
  - prompt-engineering
status: seed
address: c-000014
related:
  - "[[AI大模型知识点全景图-home]]"
  - "[[LLM Reasoning Methods]]"
  - "[[RAG and Retrieval]]"
  - "[[AI Agent Systems]]"
---

# Prompt Engineering

提示词工程是与 LLM 交互的基础技能。本质是：如何用自然语言编写指令，让大模型产生想要的输出。

## 提示词的核心维度

```
角色 (Role)     ──── "你是一个资深软件工程师..."
上下文 (Context) ──── "这是我们的代码库：...，现有架构是：..."
任务 (Task)     ──── "请重构这个函数，目标是提高可读性"
示例 (Example)  ──── 给 1-5 个输入→输出示例
格式 (Format)   ──── "请用 JSON 格式回复：{key: value}"
约束 (Constraint) ─── "不要解释，只输出代码"
```

## Prompt 方法谱系

### 基础方法
| 方法 | 描述 | 适用场景 |
|------|------|----------|
| **Zero-shot** | 直接给出指令，不给示例 | 简单、通用的任务 |
| **Few-shot** | 给 1-5 个输入-输出的示例 | 需要格式控制的场景 |
| **System Prompt** | 设定角色、规则和限制 | 对话场景、安全边界 |
| **Chain-of-Draft** | 用最简短的推理标记思考过程 | 需要推理但 token 有限 |

### 进阶方法
| 方法 | 描述 | 适用场景 |
|------|------|----------|
| **Chain-of-Thought** | "Let's think step by step" | 数学、逻辑、推理 |
| **Self-Consistency** | 多次采样 + 投票 | 数学推理、需要可靠答案 |
| **ReAct** | 推理 + 行动交替 | Agent、工具调用 |
| **Self-Ask** | 自问自答分解问题 | 需要多步推理 |
| **Tree-of-Thought** | 树状探索推理路径 | 复杂规划、决策 |
| **Role Prompting** | 赋予特定角色身份 | 需要特定视角 |

### 结构化提示
```
[SYSTEM]
你是一个专业翻译。请严格遵循：1) 保留原文格式；2) 专业术语不翻译；3) 分句对应。

[USER]
Translate: "Attention is all you need."

[ASSISTANT]
注意力就是一切。

[USER]
Translate: "Scale is not the only lever."
```

**框架**: LangChain Prompt Templates、Guidance、LMQL、Outlines

## 关键技巧

### 1. 清晰度
- 用具体描述替代模糊指示
- ❌ "写得专业一点"
- ✅ "使用正式语气，无缩略语，每条论点附带一个引用来源"

### 2. 格式控制
- **Structured Output**: "请用 JSON 格式，字段为：name, age, occupation"
- **Markdown 格式**: "使用 ## 二级标题，引用用 > "
- **XML 标签**: `<thinking>...</thinking><answer>...</answer>`

### 3. 约束前置
- 将关键约束放在 prompt 开头（系统提示）
- ❌ "...哦还有，不要解释"（用户已在其他信息中淹没）
- ✅ "不解释，只返回代码"（在最前面）

### 4. 分解复杂任务
- 将大任务拆为小步骤
- 用 CoT 分解推理链
- 用顺序 prompt（多个独立调用）替代长 prompt

### 5. 负面提示
- 告诉模型不想要什么
- "不要道歉"、"不要解释"、"不要用列表"

## 系统提示最佳实践

```
# 角色
你是一个 [角色名]。你有以下知识：[领域知识]。

# 规则
1. [规则1]
2. [规则2]
3. [规则3]

# 输出格式
[期望的输出格式]

# 限制
- 不要 [不可接受行为]
- 如果 [条件]，回复 [指定回复]
```

## Prompt 安全

- **Prompt 注入**: 用户输入可能覆盖系统指令
- **越狱 (Jailbreak)**: 用户输入可能试图绕过安全约束
- **Leakage**: 用户可能试图提取系统提示内容

### 防御措施
- 分离系统指令和用户输入（明确的边界标记）
- 输入验证和过滤
- 使用守卫模型（Guardrails）
- 限制输出内容

## 工具与框架

| 工具 | 说明 |
|------|------|
| **LangChain Prompt Hub** | Prompt 模板共享平台 |
| **Anthropic Console** | Prompt 生成器、测试平台 |
| **OpenAI Playground** | 系统提示测试 |
| **Guidance** | 结构化 prompt 生成框架 |
| **LMQL** | LLM 查询语言 |
| **Outlines** | 结构化生成框架 |

## Source
- [[AI大模型知识点全景图]] — 源文件
- [[AI大模型知识点全景图-home]] — Article Home
- Chain-of-Thought Prompting Elicits Reasoning in Large Language Models (Wei et al., 2022)
- A Prompt Pattern Catalog to Enhance Prompt Engineering with ChatGPT (White et al., 2023)
- Universal and Transferable Adversarial Attacks on Aligned Language Models (Zou et al., 2023)
