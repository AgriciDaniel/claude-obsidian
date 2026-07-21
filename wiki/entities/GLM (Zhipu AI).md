---
type: entity
title: "GLM (Zhipu AI)"
created: 2026-07-17
updated: 2026-07-17
tags:
  - entity
  - glm
  - zhipu
  - chatglm
  - chinese-ai
status: seed
address: c-000021
related:
  - "[[AI大模型知识点全景图-home]]"
  - "[[Chinese AI Model Ecosystem]]"
  - "[[AI Large Model Architecture]]"
  - "[[LLM Training Methods]]"
---

# GLM (Zhipu AI)

GLM（General Language Model）是智谱 AI 开发的大模型系列。智谱 AI 源自清华大学计算机系的知识工程实验室（KEG），拥有深厚的学术背景。

## 模型时间线

| 模型 | 发布时间 | 参数 | 关键特性 |
|------|----------|------|----------|
| GLM-130B | 2022-08 | 130B | 首个千亿级开源中英双语模型 |
| ChatGLM | 2023-03 | 6B | 对话优化，开源 |
| ChatGLM 2 | 2023-06 | 6B | 更强推理、32K 上下文 |
| ChatGLM 3 | 2023-10 | 6B | 多轮对话、Tool Use |
| GLM-4 | 2024-01 | 130B | 综合能力大幅提升 |
| GLM-4V | 2024-03 | 130B | 视觉理解 |
| GLM-4-Plus | 2024-09 | 未公开 | 更强中英文能力 |
| CodeGeeX | 2023-2024 | 6B-13B | 代码生成专用模型 |

## 架构特色

### GLM-130B
- 双向注意力（自回归空白填充）
- 结合了 GPT 和 BERT 的优点
- 支持中英双语
- INT8 量化无损失
- 在 96 块 A100 上训练完成

### ChatGLM 系列
- 针对对话场景优化
- 支持 Tool Use（ChatGLM 3+）
- 多轮对话能力强
- 相对较小的参数（6B）适合本地部署

### GLM-4
- 130B 参数，综合能力大幅提升
- 支持 128K 上下文
- 多模态输入（GLM-4V）
- Agent / Tool Use 增强

## 产品线

| 产品 | 类型 | 说明 |
|------|------|------|
| 智谱清言 | C 端产品 | 对话助手 |
| 智谱 API | API 服务 | 企业级模型调用 |
| 智谱私有化 | 私有化部署 | 政企数据安全方案 |
| CodeGeeX | 代码助手 | IDE 插件 |

## 生态与特色
- **学术渊源深**: 智谱核心团队来自清华大学 KEG 实验室
- **企业市场强**: 在企业级和政务市场有较强布局
- **教育领域**: 高校合作深入
- **GLM 系列的开源影响**: ChatGLM 系列是中文开源模型的早期标杆

## Source
- [[AI大模型知识点全景图]] — 源文件
- [[AI大模型知识点全景图-home]] — Article Home
- GLM-130B: An Open Bilingual Pre-trained Model (Zhipu AI, 2022)
- ChatGLM: A Family of Large Language Models from GLM-130B to GLM-4 (Zhipu AI, 2024)
