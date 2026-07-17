---
type: concept
title: "Chinese AI Model Ecosystem"
created: 2026-07-17
updated: 2026-07-17
tags:
  - concept
  - chinese-ai
  - domestic-models
  - ecosystem
status: seed
address: c-000008
related:
  - "[[AI大模型知识点全景图-home]]"
  - "[[DeepSeek]]"
  - "[[Qwen (Alibaba)]]"
  - "[[GLM (Zhipu AI)]]"
  - "[[Moonshot AI (Kimi)]]"
---

# Chinese AI Model Ecosystem

国内大模型生态全景。2023-2025 年间，中国大模型领域经历了从"百模大战"到"头部收敛"的激烈竞争。

## 竞争格局总览

### 第一梯队（2025）
| 公司 | 代表模型 | 核心特色 | 开源策略 |
|------|----------|----------|----------|
| **DeepSeek（深度求索）** | V2/V3/R1 | 推理能力、MoE 架构、性价比极高 | 全面开源 |
| **阿里 (Alibaba)** | Qwen 1.5/2/2.5 | 综合能力强、多模态、Agent 生态好 | 全面开源 |
| **智谱 AI (Zhipu)** | GLM-130B/GLM-4 | 学术渊源、企业级服务 | 部分开源 |
| **百度 (Baidu)** | ERNIE 3.5/4.0 | 搜索引擎结合、中文理解强 | 闭源 |
| **字节跳动** | 豆包 Doubao | C 端应用场景广、推荐系统融合 | 闭源 |
| **腾讯** | 混元 (Hunyuan) | 微信生态整合、多模态 | 闭源（部分开源） |

### 第二梯队
| 公司 | 代表模型 | 核心特色 |
|------|----------|----------|
| **百川智能 (Baichuan)** | Baichuan 7B/13B/2/3 | 开源起步、王小川领衔、医疗方向 |
| **零一万物 (01.AI)** | Yi 34B/VL/Large | 李开复带队、大参数量开源模型 |
| **Moonshot AI（月之暗面）** | Kimi k1.5 | 超长上下文、推理能力强、C 端口碑佳 |
| **MiniMax** | MiniMax-01/Text-01 | 技术创新驱动、万亿级 MoE |
| **阶跃星辰 (Stepfun)** | Step-1/Step-2 | 姜大昕带队、多模态 |
| **商汤科技** | SenseChat 日日新 | 视觉基础强、算力储备 |

### 学术/研究机构
| 机构 | 代表模型 | 特色 |
|------|----------|------|
| **上海 AI Lab** | InternLM/InternLM2 | 开源教育、书生系列 |
| **清华大学** | GLM 系列（智谱前身） | 学术根基深厚 |
| **中科院** | 紫东太初 | 多模态、全模态 |

## 开源生态对比

| 维度 | 国内 | 国际 |
|------|------|------|
| 开源主导 | DeepSeek、Qwen、Baichuan 早期 | LLaMA、Mistral、Gemma |
| 开放程度 | 权重 + 技术报告 | 权重 + 训练流程 + 数据集 |
| 社区生态 | 中文优化（ModelScope） | Hugging Face 为主 |
| 商用授权 | 各家不同（需申请） | LLaMA 社区许可宽松 |

**国内开源的三驾马车：DeepSeek + Qwen + GLM**，三者都保持了持续更新和高质量技术报告。

## 技术特色对比

| 能力维度 | 国内领先者 | 国际对标 | 差距分析 |
|----------|-----------|----------|----------|
| 数学推理 | DeepSeek-R1 | o1 | 已接近，开源版本稍弱 |
| 代码生成 | Qwen 2.5-Coder | GPT-4o | 接近，特定语言有优势 |
| 中文理解 | Qwen/GLM | GPT-4o | 国内模型明显领先 |
| 多模态 VLM | Qwen-VL | GPT-4V/4o | 有差距，尤其在细粒度理解 |
| 长上下文 | Kimi k1.5 | Gemini 1.5 Pro | Kimi 是强竞争者 |
| Agent | Qwen Agent | GPTs/Claude | 生态不如国际成熟 |
| 安全对齐 | 普遍较强 | - | 国内安全过滤更严格 |
| 推理效率 | DeepSeek V3 | GPT-4 | 成本极低，部分维度领先 |

## 产业特点

1. **激烈的价格战**: 2024 年起国内大模型 API 价格大幅下降（部分模型免费），推动应用普及
2. **应用层开花**: Kimi 聊天助手、豆包（抖音内嵌）、通义千问（阿里内嵌）等 C 端产品用户量可观
3. **政企市场**: 私有化部署需求旺盛（数据安全合规考量）
4. **监管严格**: 生成式 AI 管理办法要求模型备案、内容审核
5. **算力限制**: 高端 GPU 出口管制影响训练规模，但推动国产芯片和训推优化

## Source
- [[AI大模型知识点全景图]] — 源文件
- [[AI大模型知识点全景图-home]] — Article Home
- [[DeepSeek]] — DeepSeek 模型系列
- [[Qwen (Alibaba)]] — Qwen 系列
- [[GLM (Zhipu AI)]] — GLM 系列
- [[Moonshot AI (Kimi)]] — Kimi 系列
