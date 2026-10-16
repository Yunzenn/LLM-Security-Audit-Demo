# Changelog / 更新记录

## 2.1.0 — evaluation foundation / 评测基础升级

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

These are execution/scoring tests, not real-model security results. Red/blue
agents, AgentDojo, PyRIT and REA remain roadmap items.
上述验证针对执行和评分逻辑，不代表真实模型安全效果；红蓝队、AgentDojo、PyRIT、REA 尚待集成。
