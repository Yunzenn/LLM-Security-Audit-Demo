# Foundation validation / 基础版本验证

Date / 日期: 2026-10-16. Environment / 环境: Windows, Python 3.12.14.

## Verified locally / 本地已验证

- `pytest -q`: **36 passed**, with 12 upstream Inspect retry deprecation warnings.
  36 项通过，12 条来自 Inspect 重试实现的弃用提示。
- `ruff check src tests` and `git diff --check`: passed / 通过。
- Wheel build succeeded. Importing the wheel package independently of the
  source package found seven payload categories, including ten contract
  fixtures. Core CLI worked with Inspect imports disabled.
  构建成功；独立导入安装包后找到七类用例及十条契约用例；禁用 Inspect 导入时核心命令可运行。
- The Inspect test evaluated ten synthetic fixtures with twelve mock responses,
  including real assistant history between user turns. Deliberately leaking
  mock output was classified as a failed exact-output objective.
  Inspect 测试运行十条合成用例、十二次模拟回复；多轮包含真实助手历史，故意泄露的模拟输出判失败。
- Regression checks cover normal long answers, refusal followed by leakage,
  empty output, leakage before a later empty turn, transport errors, worker
  bounds and stable order, isolated retries, invalid config, null API content,
  report escaping, bilingual reports, and scorable denominators.
  回归覆盖长回复、拒绝后泄露、空输出、泄露后空回复、传输错误、并发与顺序、隔离重试、
  无效配置、空 API 内容、报告转义、双语输出及有效判分分母。

## Versions used / 已验证版本

| Component / 组件 | Version / 版本 |
| --- | --- |
| Inspect AI | 0.3.281 |
| pytest | 9.1.1 |
| pytest-asyncio | 1.4.0 |
| httpx | 0.28.1 |
| pydantic | 2.14.1 |
| Ruff | 0.17.1 |

This is a tested-version snapshot, not a full dependency lock.
这是验证环境快照，不是完整依赖锁定文件。

## Limits / 边界

No real model, GPU benchmark, paid API, adaptive red-team experiment, AgentDojo,
PyRIT or REA integration was used for these results. Passing these tests validates
the implementation paths, not general model security or task utility.
上述结果没有使用真实模型、GPU 基准、付费 API、自适应攻防、AgentDojo、PyRIT 或 REA；
测试通过只验证实现路径，不证明模型整体安全性或正常任务完成能力。

The workflow defines core Python 3.10/3.12 and Inspect Python 3.12 jobs.
Remote CI results must be checked separately after publication.
工作流配置了核心 Python 3.10/3.12 和 Inspect Python 3.12；远端 CI 状态需发布后单独核实。
