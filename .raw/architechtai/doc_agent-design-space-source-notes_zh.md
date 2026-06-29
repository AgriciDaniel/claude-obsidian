# Agent Systems Design Space 新进展资料记录

更新月份：2026-05

本页记录与 agent system design space 高度相关、且来源质量足够高的新进展。每条资料保留发布年月，方便后续持续追加和比较。

本页汇总关于 agent system 设计空间的高信号资料，重点关注高层原则、运行时机制、权限与治理、上下文/记忆、工具连接、长程执行、多 agent 编排和评测安全。资料来自并行子代理检索后的人工合并与去重。

## 快速结论

这些资料体现的核心趋势不是“更会聊天的 agent”，而是 agent operating layer 正在成形：可恢复的执行环境、显式权限边界、可审计遥测、可版本化 context/skills、可插拔工具连接、长任务状态机、人类中途接管，以及从 traces 反推 eval 和改进循环。

对本仓库的 Design Space 叙事，最值得强化的设计启示是：

1. **Runtime and control plane are first-class design concerns**：持久执行、检查点、沙箱、agent inventory、策略面和可观测性，应该作为一等设计关注点，而不是部署细节。
2. **Context is managed infrastructure**：context 不只是 prompt，而是文件、skills、memory、interpreter state、workspace state、IDE indexes 和可版本化策略。
3. **Execution boundary is the safety boundary**：sandbox、network policy、credential custody、OS-level isolation、tenant boundary 和 approval policy 是核心架构对象。
4. **Tools and skills are a supply chain**：MCP、SDK、CLI、plugins、skills 和 agent-to-agent protocols 放大能力，也引入 registry、allowlist、identity、versioning 和 revocation 问题。
5. **Humans become managers and verifiers**：长任务和异步代理要求人类能在过程中审查、改方向、批准、回滚，而不是只看最终 diff。
6. **Observability must close the improvement loop**：生产 agent 的失败模式需要通过 trace/eval/issue/dataset 回路进入下一轮系统改进。

## P0: 最值得纳入综述的资料

| 年月 | 资料 | 核心内容 | Design Space 价值 |
|:---:|:---|:---|:---|
| 2026-05 | [OpenAI named a Leader in enterprise coding agents by Gartner](https://openai.com/index/gartner-2026-agentic-coding-leader/) | Codex 被定位为企业级 coding agent；OpenAI 强调 large codebase、工具使用、测试、approval gates、RBAC、sandboxing、auditable workspace governance。 | 说明 coding agent 已从 autocomplete 进入 delegated work / operating layer；治理和审计是企业 agent 的一等需求。 |
| 2026-05 | [Cursor: What we've learned building cloud agents](https://cursor.com/blog/cloud-agent-lessons) | 云端 agent 需要完整开发环境、durable execution、VM checkpoint/fork、secret redaction、network policies、credential management。 | 可直接支撑“agent environment as product”和“cloud agent runtime”章节。 |
| 2026-05 | [AWS: Break the context window barrier with Bedrock AgentCore](https://aws.amazon.com/blogs/machine-learning/break-the-context-window-barrier-with-amazon-bedrock-agentcore/) | 用 AgentCore Code Interpreter + Strands Agents SDK 实现 Recursive Language Models，把长文档放入 sandbox/interpreter working memory，模型只按需调用子 LLM。 | 强化“context 不只在 prompt 里”：外部环境、代码状态和 working variables 可以成为 agent memory surface。 |
| 2026-05 | [LangChain: From Token Streams to Agent Streams](https://www.langchain.com/blog/token-streams-to-agent-streams) | streaming 从 token delta 升级为 typed events：messages、tool calls、subagent activity、state changes、approvals、media。 | 对 agent UI、可观测性、重连、子代理 inspector 和长任务 dashboard 很关键。 |
| 2026-05 | [LangChain: Give Your Agents an Interpreter](https://www.langchain.com/blog/give-your-agents-an-interpreter) | Deep Agents 增加受限 interpreter，介于串行 tool calls 和完整 sandbox 之间；工具通过 allowlist bridge 暴露。 | 提供“可编程 agent loop”的中间设计点：更窄 action surface、更少 token、更清楚的失败模式。 |
| 2026-05 | [Google: Building the agentic future at I/O 2026](https://blog.google/innovation-and-ai/technology/developers-tools/google-io-2026-developer-highlights/) | Antigravity 2.0、Managed Agents in Gemini API、persistent isolated environments、dynamic subagents、scheduled tasks、custom skills。 | Google 把 agent-first development platform 明确做成 harness + sandbox + persistent state + subagents。 |
| 2026-05 | [Google: Build managed agents with the Gemini API](https://blog.google/innovation-and-ai/technology/developers-tools/managed-agents-gemini-api/) | 单次 API 调用创建可推理、用工具、执行代码的托管 agent；运行在隔离 Linux 环境，可保留文件和状态。 | 可作为“managed runtime ownership”的对照案例：谁拥有 loop、环境、state 和工具边界。 |
| 2026-05 | [LangChain: How We Built LangSmith Engine](https://www.langchain.com/blog/how-we-built-langsmith-engine-our-agent-for-improving-agents) | LangSmith Engine 坐在 agent traces 之上，发现 recurring issues，并建议下一步修复。 | 适合“agent improvement loop”：trace -> failure cluster -> eval/dataset/issue -> fix agent。 |
| 2026-05 | [Anthropic acquires Stainless](https://www.anthropic.com/news/anthropic-acquires-stainless) | Anthropic 收购 SDK、CLI、MCP server tooling 公司 Stainless，强调 agents 的价值取决于它能连接到哪些系统。 | “Connectivity is capability”：API spec 到 SDK/CLI/MCP server 是 agent 可行动能力的基础设施层。 |
| 2026-05 | [OpenAI and Dell: Codex for hybrid/on-prem enterprise](https://openai.com/index/dell-codex-enterprise-partnership/) | Codex 将靠近企业本地/混合环境中的数据、代码库、文档、业务系统和工作流。 | 引入 deployment topology/context locality 维度：agent 放在哪里，决定能看见什么、能做什么、如何治理。 |
| 2026-05 | [OpenAI: Work with Codex from anywhere](https://openai.com/index/work-with-codex-from-anywhere/) | Codex 进入 ChatGPT mobile preview；用户可远程查看状态、批准命令、改方向、审 diff；Remote SSH、Hooks、programmatic tokens GA。 | 很适合“supervised async agent”：人类不全程陪跑，但能在关键决策点介入。 |
| 2026-05 | [OpenAI: Building a safe, effective sandbox to enable Codex on Windows](https://openai.com/index/building-codex-windows-sandbox/) | 讲 Windows 下 Codex sandbox 如何在频繁审批和 Full Access 之间平衡。 | 具体机制案例：OS-level isolation、workspace boundary、network control、approval friction。 |
| 2026-05 | [LangChain: LangSmith Sandboxes GA](https://www.langchain.com/blog/langsmith-sandboxes-generally-available) | microVM kernel isolation、snapshots/forks、prewarmed environments、Service URLs、Auth Proxy。 | 说明 production agent 不能只靠“容器式 sandbox”；执行环境本身是安全边界。 |
| 2026-05 | [LangChain: Introducing Managed Deep Agents](https://www.langchain.com/blog/introducing-managed-deep-agents) | 托管 runtime 提供 durable threads、checkpointing、streaming、context、observability、human-in-the-loop。 | 对应“open-source harness + managed runtime”的拆分方式。 |
| 2026-05 | [LangChain: Introducing Context Hub](https://www.langchain.com/blog/introducing-context-hub) | 把 `AGENTS.md`、skills、policies、examples、memory files 版本化、可回滚、可协作。 | 直接支撑“context as first-class artifact”：context 需要自己的生命周期，而不是散落在 prompt 里。 |
| 2026-05 | [Claude Code Dynamic Workflows](https://code.claude.com/docs/en/workflows) + [Opus 4.8](https://www.anthropic.com/news/claude-opus-4-8) | Claude 自己写 JavaScript 编排脚本，后台 runtime 扇出到上千个 subagent；中间状态存在脚本变量（对话之外），只有最终答案进入 context；16 并发 / 1000 总量上限，同一 session 内可 resume。随 Opus 4.8（2026-05-28）一同发布，v2.1.154 引入，research preview。 | 直接延伸本文 §8 subagent 编排与 Future「超越 session / sub-agent / memory 的新协调原语」：编排逻辑从对话搬进代码，是 context-as-bottleneck 原则的下一步。 |

## P1: 强相关资料

| 年月 | 资料 | 核心内容 | Design Space 价值 |
|:---:|:---|:---|:---|
| 2026-05 | [Project Glasswing: initial update](https://www.anthropic.com/research/glasswing-initial-update) | Anthropic 用模型发现漏洞，瓶颈从发现迁移到验证、披露、修复。 | agent 能力提升后，系统瓶颈转向人类验证队列、责任流程和安全发布。 |
| 2026-05 | [OpenAI: Virgin Atlantic ships faster with Codex](https://openai.com/index/virgin-atlantic/) | Codex 用于测试、legacy refactor、数据原型和生产工程流程。 | adoption case：agent 改变工程节奏后，瓶颈转向组织协作和 review 流程。 |
| 2026-05 | [Microsoft + EY: From AI pilots to enterprise impact](https://blogs.microsoft.com/blog/2026/05/21/from-ai-pilots-to-enterprise-impact-why-execution-is-the-new-differentiator/) | 强调从 pilot 到 production，需要 intelligence + trust、透明、安全、可问责、可复制执行模型。 | 适合组织层设计原则：agent 系统不是单工具，而是运营模型重构。 |
| 2026-05 | [Google DeepMind: Gemini 3.5](https://deepmind.google/models/gemini/) | Gemini 3.5 Flash 被定位为面向 agents and coding 的高性能模型，强调 long-horizon tasks、tool use、UI control 等 benchmark。 | 可作为“model capability substrate”背景，但应避免让模型分数淹没 harness 讨论。 |
| 2026-05 | [GitHub: Fix code review feedback with Copilot cloud agent](https://github.blog/changelog/2026-05-19-easily-apply-copilot-code-review-feedback-with-copilot-cloud-agent/) | 将 Copilot code review comment 批量交给 Copilot cloud agent 修复，可选择模型和应用方式。 | 表明 review -> implementation handoff 正在产品化；human review 成为 agent workflow gate。 |
| 2026-05 | [GitHub: one-click fixes for failing Actions](https://github.blog/changelog/2026-05-18-one-click-fixes-for-failing-actions-with-copilot-cloud-agent/) | CI 失败后可一键让 Copilot cloud agent 调查、推 fix、等待 review。 | 对应“event-triggered repair agents”和“CI as agent entry point”。 |
| 2026-05 | [GitHub: fast, cost-efficient models for Copilot cloud agent](https://github.blog/changelog/2026-05-18-copilot-cloud-agent-fast-cost-efficient-models-for-simple-tasks/) | Copilot cloud agent 可按任务选择更快、更便宜模型。 | 引入“模型路由 / cost-capability matching”维度。 |
| 2026-05 | [GitHub: Building a general-purpose accessibility agent](https://github.blog/ai-and-ml/github-copilot/building-a-general-purpose-accessibility-agent-and-what-we-learned-in-the-process/) | GitHub accessibility agent 采用 reviewer sub-agent + implementer sub-agent，并用复杂度评分决定是否只给 guidance。 | 很好的多 agent 分工案例：passive reviewer、active implementer、escalation gates、complexity-based behavior。 |
| 2026-05 | [PwC + Anthropic expanded partnership](https://www.anthropic.com/news/pwc-expanded-partnership) | PwC 将部署 Claude Code/Cowork，建立 Center of Excellence，培训认证 30,000 人。 | 组织采用侧证：agent system 需要培训、治理、COE 和行业流程落地。 |
| 2026-05 | [Agent-First Tool API](https://arxiv.org/abs/2605.10555) | 提出 agent-first API：search、resolve、preview、execute、verify、recover 六阶段，以及 Normalized Tool Contract。 | 对工具层设计很有价值：传统 CRUD API 不适合 autonomous agents，需要 agent-native semantic interface。 |
| 2026-05 | [Code as Agent Harness](https://arxiv.org/abs/2605.18747) | 把 code 视为 agent reasoning、acting、environment modeling、execution verification 的统一 harness。 | 和本仓库 thesis 高度一致：agent 的工程复杂度在可执行、可验证、可状态化的 harness。 |
| 2026-05 | [MemGym](https://arxiv.org/abs/2605.20833) | 长程 agent memory benchmark，覆盖 tool-use dialogue、deep research、coding、computer use。 | memory 不是简单长期记忆，而是长任务中形成、压缩、检索和迁移的执行能力。 |
| 2026-05 | [Push Your Agent](https://arxiv.org/abs/2605.23574) | 衡量 long-horizon agents 是否能坚持到 verifier 确认足够多有效工件，而非过早停止。 | 强化 stop condition、verified progress、backlog tracking 是长任务 agent 的核心机制。 |
| 2026-05 | [Boiling the Frog](https://arxiv.org/abs/2605.22643) | 多轮、持久 workspace 中的渐进式 agentic safety benchmark。 | 安全评测对象从“模型输出文本”转向“环境状态是否被改坏”。 |
| 2026-05 | [How to Steer Your Multi-Agent System](https://arxiv.org/abs/2605.23023) | 将 human-LLM co-planning 分成 semantic/structural、global/targeted、low/high-level edits 三轴。 | 支持“过程级监督”：人类控制面应落在 plan/process 上，而不是只审最终产物。 |

## 其他高信号资料

| 年月 | 资料 | 为什么仍值得纳入 |
|:---:|:---|:---|
| 2026-05 | [OpenAI: Running Codex safely at OpenAI](https://openai.com/index/running-codex-safely/) | 给出了清晰的 coding-agent 安全设计原则：bounded environment、low-risk frictionless、high-risk review、agent-native telemetry。 |
| 2026-05 | [Microsoft: Frontier Firms operating model](https://blogs.microsoft.com/blog/2026/05/05/how-frontier-firms-are-rebuilding-the-operating-model-for-the-age-of-ai/) | 组织设计角度很强：人类从逐步执行转向设方向、定标准、评估结果；AI 价值取决于工作如何被重新设计。 |
| 2026-05 | [Anthropic: Agents for financial services](https://www.anthropic.com/news/finance-agents) | 垂直 agent 模板、per-tool permissions、credential vaults、audit logs，适合展示 regulated domains 的 agent design requirements。 |

## 更多可持续追加的高质量资料

| 年月 | 资料 | 可吸收的设计启示 | 适合放在哪里 |
|:---:|:---|:---|:---|
| 2026-05 | [NSA: MCP Security](https://www.nsa.gov/Portals/75/documents/Cybersecurity/CSI_MCP_SECURITY.pdf) | MCP server 是能力入口，也是供应链和权限入口，需要 registry、identity、allowlist、monitoring 和 revocation。 | 工具供应链、connectivity risk。 |
| 2026-05 | [Kiro: Deep spec analysis](https://kiro.dev/blog/deep-spec-analysis/) | spec/requirements 可以作为 agent 前置控制面，让实现之前先稳定目标、约束和验收条件。 | human control surface、plan/process supervision。 |
| 2026-05 | [OpenAI agent improvement loop](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop) | traces、evals、prompt/tool changes 可以形成闭环，而不是停留在日志分析。 | observability/eval improvement loop。 |
| 2026-05 | [Microsoft Agent 365](https://www.microsoft.com/en-us/security/blog/2026/05/01/microsoft-agent-365-now-generally-available-expands-capabilities-and-integrations/) | agent inventory、访问控制、治理和组织级可见性正在成为 control plane 的组成部分。 | README 的 runtime/control plane 行，或企业采用部分。 |
| 2026-04 | [NSA/CISA: Careful Adoption of Agentic AI Services](https://media.defense.gov/2026/Apr/30/2003922823/-1/-1/0/CAREFUL%20ADOPTION%20OF%20AGENTIC%20AI%20SERVICES_FINAL.PDF) | agentic service 的风险来自 autonomy、tool use、data access、credential handling 和第三方执行环境的组合。 | 安全边界、治理和 enterprise adoption。 |
| 2026-04 | [Cognition: Multi-agents working](https://cognition.ai/blog/multi-agents-working) | 多 agent 并行的关键不是数量，而是任务切分、写权限约束、冲突处理和可验证合并。 | human manager/verifier、多 agent architecture。 |
| 2026-04 | [GitHub Copilot CLI MCP allowlists](https://github.blog/changelog/2026-04-16-copilot-cli-supports-custom-registry-based-mcp-allowlists/) | MCP allowlist 正在从安全建议变成产品机制。 | 工具供应链的代表信号。 |
| 2026-04 | [A2A protocol milestone](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year) | agent-to-agent protocol 正在形成互操作层，但也会扩大身份、权限和责任边界。 | 多 agent 协议与治理。 |

## 可写入 Design Space 的新原则草案

- **Environment parity before model blame**：云端 agent 失败常常不是模型差，而是环境缺依赖、权限、网络或凭证。
- **Bounded programmability beats raw power**：interpreter / programmatic tool calling 给 agent 编程能力，但通过 allowlist bridge 缩小 action surface。
- **Human oversight must be interruptible and mobile**：长程异步 agent 需要远程查看、批准、改方向和审查 diff 的控制面。
- **Memory needs provenance and lifecycle**：memory/context/skills 需要版本、来源、审查、回滚、环境标签和过期机制。
- **Progress must be verified, not inferred**：长任务应维护 verified backlog，而不是靠模型自称“完成了”。
- **Telemetry is not enough without evaluation**：logs 只能解释发生了什么；生产 agent 还需要把 traces 转化为 failure clusters、evals 和改进任务。
- **Connectivity is capability, but also risk**：MCP、SDK、CLI、plugins 放大能力，也扩大 credential、data exfiltration 和 tool misuse 的设计面。
