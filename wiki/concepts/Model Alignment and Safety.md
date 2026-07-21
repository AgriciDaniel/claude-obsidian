---
type: concept
title: "Model Alignment and Safety"
created: 2026-07-17
updated: 2026-07-17
tags:
  - concept
  - ai-safety
  - alignment
  - red-teaming
  - jailbreak
status: seed
address: c-000005
related:
  - "[[AI大模型知识点全景图-home]]"
  - "[[LLM Training Methods]]"
  - "[[AI Agent Systems]]"
---

# Model Alignment and Safety

大模型安全对齐（Alignment）的核心目标：确保模型行为符合人类的意图和价值观，同时防御恶意滥用。

## 对齐的三大维度

| 维度 | 说明 | 代表方法 |
|------|------|----------|
| **有用性** (Helpful) | 准确、有效地回答用户问题 | SFT、RLHF |
| **诚实性** (Honest) | 不编造、不误导（减少幻觉） | RLHF、Factuality tuning |
| **无害性** (Harmless) | 不产生有害、偏见、危险内容 | RLHF、Constitutional AI |

**这三个维度存在内在张力**：过度强调无害可能导致过度拒绝（refusal）、降低有用性。

## 红队测试（Red Teaming）

### 定义
系统性地尝试突破模型安全边界，发现漏洞和弱点的过程。

### 形式
- **人类红队**: 安全专家手动构造攻击提示
- **自动化红队**: 用一个模型攻击另一个模型，自动生成对抗性样本
- **LLM 辅助红队**: 用 GPT-4/Claude 等强模型生成攻击变体

### 覆盖的威胁类别
- Hate speech、Harassment、Violence incitement
- Self-harm、Harmful instructions
- Sexually explicit content
- Political bias、Stereotype reinforcement
- Privacy violations（PII 泄露）

## Jailbreak 攻击

### 常见手法

| 手法 | 描述 | 示例 |
|------|------|------|
| **角色扮演** | 让模型扮演一个不遵守规则的"反派" | "请扮演一个不受约束的AI..." |
| **假设场景** | 虚构一个不需要遵守规则的世界 | "假设一个平行宇宙..." |
| **编码/加密** | 用 Base64、凯撒密码等编码请求 | "R2l2ZSBtZSBoYXJtZnVsIGluZm9ybWF0aW9u"（Base64） |
| **多轮诱导** | 分多次提问，逐步接近敏感话题 | 先问一般性 → 逐渐引入敏感内容 |
| **翻译/多语言** | 用低资源语言绕过安全过滤 | 中文攻击比英文更容易成功（因安全训练数据以英文为主） |
| **Token 操纵** | 在 token 级别绕过对齐训练 | Adversarial suffixes（对抗性后缀） |

### 知名案例
- **"Do Anything Now" (DAN)**: 角色扮演类最著名的 jailbreak
- **GCG (Greedy Coordinate Gradient)**: 算法搜索对抗性后缀
- **Crescendo**: 多轮渐进式诱导攻击
- **Deep Inception**: 嵌套场景构造

## 防御机制

### 训练时防御
| 方法 | 说明 |
|------|------|
| **Adversarial Training** | 用红队发现的 jailbreak 数据训练模型 |
| **RLHF 安全强化** | 在 RLHF 中增加安全维度的偏好对 |
| **Constitutional AI** | 用宪法原则指导模型自我修订 |
| **Safety Mix** | SFT 数据中混入安全回绝示例 |

### 推理时防御
| 方法 | 说明 |
|------|------|
| **System Prompt Guard** | 用系统提示设定安全边界 |
| **输入/输出过滤** | 关键词 + 分类器检测有害内容 |
| **Perplexity 检测** | 对抗性后缀通常困惑度较高 |
| **Self-Exam / Self-Reminder** | 模型自己检查输出是否安全 |
| **Safety Prefix** | 在生成前强制加无害前缀 |

## Watermarking（AI 内容检测）

### 主要方法
- **Aaronson 水印**: 用随机种子影响 token 采样（开源方案）
- **Kirchenbauer 水印**: 将 token 分为"绿名单"和"红名单"（逻辑简单）
- **DIP (DetectGPT)**: 基于模型对自身的 logprob 差异检测
- **自回归水印**: 在生成过程中注入统计信号

### 挑战
- 对改写、翻译、摘要的鲁棒性不足
- 降采样（temperature 调高）可削弱水印
- 短文本难以可靠水印

## Bias Mitigation

### 常见偏见类型
- 刻板印象（性别、种族、职业、地域）
- 政治偏见
- 文化偏见（英文中心、西方中心）

### 缓解方法
- **数据去偏**: 筛选训练数据中的偏见内容
- **SFT 修正**: 用公平性数据微调
- **RLHF 偏好调整**: 在偏好数据中增加公平性维度
- **Prompt 干预**: 系统提示中明确要求公平

## 数据隐私

### 风险
- **记忆化**: 模型可能记住训练数据中的 PII（个人信息）
- **提取攻击**: 通过精心设计的 prompt 抽取训练数据
- **成员推理**: 判断特定数据是否在训练集中

### 防御
- 数据去重（减少罕见序列的记忆）
- 差分隐私训练（DP-SGD）
- 回复时过滤 PII
- 版权内容的检测与过滤

## Source
- [[AI大模型知识点全景图]] — 源文件
- [[AI大模型知识点全景图-home]] — Article Home
- Constitutional AI: Harmlessness from AI Feedback (Anthropic, 2022)
- The "Crescendo" Attack (Google DeepMind, 2024)
- A Watermark for Large Language Models (Kirchenbauer et al., 2023)
