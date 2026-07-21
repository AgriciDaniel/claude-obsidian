---
type: concept
title: "AI Agent Systems"
created: 2026-07-17
updated: 2026-07-17
tags:
  - concept
  - agent
  - tool-use
  - function-calling
  - moa
status: seed
address: c-000009
related:
  - "[[AI大模型知识点全景图-home]]"
  - "[[LLM Reasoning Methods]]"
  - "[[RAG and Retrieval]]"
  - "[[Model Alignment and Safety]]"
---

# AI Agent Systems

AI Agent（智能体）是大模型能力的"执行层"：让模型不仅能回答问题，还能调用工具、执行任务、自主规划。

## Agent 的核心范式

### 标准循环
```
Observe（感知环境）→ Think（思考/规划）→ Act（执行动作）→ Observe（观察结果）→ ...
```

### 关键能力
1. **规划 (Planning)**: 分解复杂任务、制定执行步骤
2. **工具调用 (Tool Use)**: 调用 API、运行代码、访问数据库
3. **记忆 (Memory)**: 短期上下文 + 长期知识
4. **反思 (Reflection)**: 评估执行结果、修正错误

## Function Calling / Tool Use

### 实现方式
- **原生 Function Calling**: 模型输出结构化函数调用请求（OpenAI、Claude、Qwen 等均支持）
- **JSON Mode**: 输出格式强制为 JSON，解析为函数调用
- **代码解释器**: 模型直接生成代码执行（如 GPT-4 Code Interpreter）

### 工具类型
| 工具类型 | 示例 | 说明 |
|----------|------|------|
| 搜索引擎 | Web Search、Wikipedia | 获取实时/外部信息 |
| 代码执行 | Python REPL、Sandbox | 运行计算、生成图表 |
| 数据库 | SQL Query、向量检索 | 结构化/非结构化数据查询 |
| 外部 API | 天气、日历、邮件 | 接入第三方服务 |
| 文件处理 | 读取、写入、解析 | 支持各种文件格式 |
| 多模态 | 文字转图像、语音合成 | 使用生成模型作为工具 |

### MCP（Model Context Protocol）
- Anthropic 推出的标准化工具协议
- 定义统一的工具注册和调用接口
- 让 Agent 可以动态发现和使用多种工具
- 类似"AI 的 USB 协议"

## Agent 架构模式

### 1. 单 Agent（ReAct 模式）
```
用户 → Agent（LLM + Tools）→ 回复
```
最简单的模式。一个模型思考 → 调用工具 → 思考 → 输出。

适合场景：简单任务、单一工具链

### 2. Multi-Agent（多智能体协作）
```
                 ┌──────────┐
                 │ 协调者   │ ← 分发任务 + 汇总结果
                 └────┬─────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
    ┌────▼───┐  ┌────▼───┐  ┌────▼───┐
    │ Agent A│  │ Agent B│  │ Agent C│
    │ 研究    │  │ 编码    │  │ 检查    │
    └────────┘  └────────┘  └────────┘
```

适合场景：复杂工作流、多角色协作

### 3. Mixture of Agents（MoA）
- 多个 Agent 各自生成回答 → 聚合器汇总最优结果
- 类似 MoE 的 Agent 版本
- 提升推理和生成质量

### 4. 分层 Agent
- 高层 Agent 负责战略规划
- 低层 Agent 负责具体执行
- 适合：长期任务、企业级工作流

## 主流 Agent 框架

| 框架 | 开发方 | 特点 |
|------|--------|------|
| **LangChain/LangGraph** | LangChain | 最流行、生态最丰富 |
| **AutoGPT** | Significant Gravitas | 自主 Agent 先驱 |
| **CrewAI** | CrewAI | 多 Agent 协作，简单易用 |
| **OpenAI Assistants API** | OpenAI | 托管 Agent、内置工具 |
| **Claude Agents / MCP** | Anthropic | 安全优先、MCP 协议 |
| **MetaGPT** | 清华/开源 | 软件公司模拟（PM/架构师/工程师） |
| **Dify** | 开源 | 可视化 Agent 编排 |
| **Coze (扣子)** | 字节跳动 | 国内最流行的 Agent 平台 |

## 安全性挑战

### 关键风险
- **工具权限控制**: Agent 可调用外部 API，权限如何设定？
- **Prompt 注入**: 外部输入可能劫持 Agent 行为
- **数据泄露**: Agent 可能将敏感信息传递给外部服务
- **不可逆操作**: Agent 执行了发送邮件、删除文件等操作后无法回滚
- **幻觉传播**: Agent 的幻觉通过工具调用变成真实操作

### 安全最佳实践
- 最小权限原则（只给 Agent 完成任务所需的最少工具）
- Human-in-the-loop（关键操作需人工确认）
- 沙盒执行（代码/脚本在隔离环境运行）
- 工具调用审计日志

## 实际应用场景

| 场景 | 示例 | 价值 |
|------|------|------|
| 代码开发 | Cursor、Windsurf、GitHub Copilot | AI 编程助手，10x 开发效率 |
| 科研辅助 | 文献检索、实验设计、数据分析 | 加速研究周期 |
| 客服 | 自动问答、工单处理、知识库检索 | 7×24 自动化服务 |
| 数据分析 | SQL 生成、可视化、报告自动生成 | 降低数据使用门槛 |
| 工作流自动化 | Zapier 类、邮件处理、日程管理 | 减少重复劳动 |
| 金融分析 | 市场研究、风险评估、报告生成 | 提高分析效率 |

## Source
- [[AI大模型知识点全景图]] — 源文件
- [[AI大模型知识点全景图-home]] — Article Home
- ReAct: Synergizing Reasoning and Acting in Language Models (Yao et al., 2022)
- MCP Specification (Anthropic, 2024)
