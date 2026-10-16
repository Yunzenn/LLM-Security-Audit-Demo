# LLM Security Audit — 2.3

[English](#english) · [中文](#中文)

## English

A security regression evaluation prototype for LLM applications. This iteration
provides explicit outcomes, an optional Inspect AI integration, paired lab tasks,
and a first real-weight Qwen3-0.6B pilot.
It is not a security certification or a calibrated benchmark.

### What works now

- Exact, case-sensitive forbidden-output contracts across every assistant turn.
- Separate `pass`, `fail`, `unknown`, and execution `error` outcomes. Keyword
  heuristics remain advisory; legacy YAML without contracts scores unknown.
- Isolated multi-turn histories, bounded concurrency (1–64 case workers), and
  retries that restart the entire conversation.
- English/Chinese Markdown and escaped offline HTML reports with coverage and
  explicit denominators; raw JSON includes messages and attempts.
- Optional Inspect AI backend with native logs and ten bilingual synthetic
  fixtures. Mock results validate execution/scoring, not model safety.

### Quick start

Python >=3.10 for core; the Inspect pilot is validated on Python 3.12.

```bash
pip install -e '.[dev,inspect]'
llm-audit init
# Edit config.yaml to point to your running OpenAI-compatible model service.
llm-audit scan --categories contract_demo --lang en
llm-audit scan --categories contract_demo --lang zh
# Synthetic execution, no real model or paid API:
llm-audit inspect-scan --dataset attack_payloads/contract_demo.yaml --model mockllm/model
pytest -q
```

Inspect's first run may fetch public tokenizer files. See the migration guide
for cache preparation and real endpoint settings. Inspect is optional: install
`.[dev]` for core only. Use `llm-audit list-attacks` to inspect bundled cases.

### Roadmap

Inspect execution, paired lab tasks and a three-defense comparison are
implemented. The real-weight pilot completed 120 cases with no execution
errors, but exact utility was only 5–20% and no unauthorized attempts occurred;
zero attack goals do not establish defense efficacy. Next: clarify task contracts
in a new dataset version, establish clean-task competence, then add budgeted
adaptive attacks. PyRIT, native AgentDojo baselines and REA remain planned.

- [Upgrade plan](docs/UPGRADE_PLAN.en.md)
- [Migration and scoring semantics](docs/MIGRATION.en.md)
- [Real-model guide](docs/REAL_MODEL_GUIDE.en.md)
- [Real pilot results and limitations](docs/experiments/qwen3-pilot-2026-10-17/RESULTS.en.md)
- [Changes / 更新记录](CHANGELOG.md)

## 中文

面向大模型应用的安全回归评测原型。已实现明确判分、可选 Inspect AI 后端、配对资料助手任务，
并完成首次 Qwen3-0.6B 真实权重试跑。当前版本不能提供安全认证，也不是经过校准的安全基准。

### 已实现

- 逐轮检查助手输出中的精确、区分大小写的禁止字符串。
- 明确区分通过、失败、未知、执行错误。关键词规则只作辅助信号；没有判分契约的旧用例记为未知。
- 用例间对话隔离，支持真实多轮、有界并发和整段对话重试。
- 中英文 Markdown 与转义后的离线 HTML 报告，展示可评分覆盖率及明确分母；原始 JSON 保存对话和尝试次数。
- 可选 Inspect AI 执行后端、原生轨迹及十条双语合成用例。Mock 仅验证执行与评分逻辑，不代表模型安全效果。

### 使用

核心要求 Python >=3.10，Inspect 试点在 Python 3.12 验证。安装命令见上方。
`scan` 需要先配置并启动模型服务；`inspect-scan --model mockllm/model` 使用合成输出，
不调用真实模型或付费 API。首次 Inspect 运行可能下载公开分词器数据，离线准备步骤见迁移说明。

### 后续路线

已实现 Inspect 执行、资料助手配对样本和三组防御对照。真实权重完成 120 个用例且执行错误为零，
但精确任务完成率仅 5%–20%，没有观察到越权尝试，攻击零命中不能证明防御有效。
下一步先版本化澄清任务契约、验证正常任务能力，再加入有预算的自适应攻击。
PyRIT 红队策略、AgentDojo 原生基准、REA 分析/MCP 场景仍待集成。

- [中文升级方案](docs/UPGRADE_PLAN.zh-CN.md)
- [中文迁移与判分说明](docs/MIGRATION.zh-CN.md)
- [真实模型操作指南](docs/REAL_MODEL_GUIDE.zh-CN.md)
- [真实试跑结果与限制](docs/experiments/qwen3-pilot-2026-10-17/RESULTS.zh-CN.md)
- [Changes / 更新记录](CHANGELOG.md)

## Lab-assistant iteration / 资料助手实验

```bash
# 20 pairs × 2 variants × 3 defenses = 120 simulated cases
llm-audit lab-eval --split all --output reports/lab-v1
```

The default is a deliberately policy-blind scripted mock, with no paid API.
It verifies in-memory tool effects and enforcement, not model defense efficacy.
默认使用故意忽略防御提示的模拟模型，不调用付费 API；验证的是内存工具状态与权限拦截。

[English guide](docs/LAB_EXPERIMENT.en.md) · [中文说明](docs/LAB_EXPERIMENT.zh-CN.md)

## License / 许可

[MIT](LICENSE). Third-party frameworks retain their own licenses.
第三方框架遵循各自许可证。
