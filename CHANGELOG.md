# Changelog / 更新记录

## 2.3.0 — real-weight pilot / 真实权重试跑

- Explicit pair selection, validated native-HF initialization options and forwarded HTTP chat-template settings. 显式选择任务对、校验原生 HF 参数、转发 HTTP 模板设置。
- Portable source fingerprints and explicit completion evidence for Inspect's missing native-HF finish reason; capped/absent evidence stays unknown. 可跨源码与 wheel 核对的源码指纹；明确标注原生 HF 的推断完成证据，截断或缺失证据仍记未知。
- 120 real-weight Qwen3-0.6B cases, 262 completed responses, zero execution errors, bilingual reviewed artifacts and separate dev/holdout summaries. 120 个真实权重用例、262 次已完成回复、零执行错误，公开双语复核结果与分区汇总。
- Exact utility is only 5–20%, with no unauthorized attempts; zero achieved attack goals is not evidence of defense efficacy. 精确任务完成率仅 5%–20%，无越权尝试，不能宣称防御有效。
- 80 local tests passed; Ruff and wheel build passed. Native HF validated; shared vLLM startup crashed and HTTP serving remains unvalidated. 本地 80 项测试、Ruff、wheel 构建通过；原生 HF 验证完成，共享 vLLM 启动崩溃，HTTP 服务仍待验证。

## 2.2.0 — lab-agent regression matrix / 资料助手回归实验

- Review fixes: label all mock providers accurately and retain observed attack goals and usage after errors. 审查修复：准确标注模拟提供商，报错后保留已观察到的攻击目标和用量。

- Twenty synthetic bilingual task pairs and three defense variants, using Inspect tools and native execution. 20 对双语合成任务、三组防御，复用 Inspect 工具执行。
- Isolated in-memory tools, deterministic authorization, state-based utility and independent attack goals. 隔离内存工具、程序授权、状态任务判分与独立攻击目标。
- Bilingual summaries, dataset/version manifests, native evidence and planned error denominators. 双语汇总、数据与版本清单、原生证据及完整计划分母。
- Complete 120-case mock integration matrix. Real-model validation remains pending; no autonomous red/blue agent is claimed. 完整 120 用例模拟测试；真实模型仍待验证，尚不宣称自主红蓝队。

## 2.1.0 — evaluation foundation / 评测基础升级

- Review fixes: preserve evidence across retries, retain attempt transcripts,
  and avoid passing incomplete Inspect conversations. 审查修复：跨重试保留证据和对话，未完成的 Inspect 对话不判通过。

- Separate deterministic pass/fail, unknown, and execution errors. Keyword rules
  are advisory; legacy results without contracts no longer count as safe.
  区分确定性通过/失败、未知和执行错误；关键词仅作辅助信号，无契约的旧用例不再计为安全。
- Execute isolated multi-turn conversations with bounded concurrency and whole
  conversation retries. 保存真实对话链，实现有界并发和整段对话重试。
- Add an optional Inspect AI backend and ten synthetic bilingual fixtures.
  接入可选 Inspect AI 后端，加入十条中英文合成测试用例。
- Provide English/Chinese Markdown and escaped offline HTML reports, package
  payload YAML, and add regression CI. 提供双语报告、随安装包发布 YAML，并新增回归 CI。
- A leak observed before a later blank response remains a failure. Model
  initialization failures exit nonzero. 已观察到的泄漏不会被后续空回复覆盖；初始化失败返回错误码。

The 2.1/2.2 validations above are execution/scoring tests; the 2.3 pilot is
reported separately with its limitations. Autonomous red/blue agents,
AgentDojo, PyRIT and REA remain roadmap items.
上述 2.1/2.2 验证针对执行和评分逻辑；2.3 真实试跑单独披露结果与限制。
自主红蓝队、AgentDojo、PyRIT、REA 尚待集成。
