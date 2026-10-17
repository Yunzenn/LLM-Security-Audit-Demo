# Lab iteration validation / 资料助手版本验证

Historical v2.2 mock validation. For the completed v2.3 real-weight pilot, see
[English results](experiments/qwen3-pilot-2026-10-17/RESULTS.en.md) /
[中文结果](experiments/qwen3-pilot-2026-10-17/RESULTS.zh-CN.md).
本页保留 2.2 的历史验证记录；2.3 真实权重试跑已完成，结论与限制见上述链接。

2026-10-16, Windows, Python 3.12.14, Inspect AI 0.3.281.

- Local full suite: **60 tests passed**. 本地完整测试 60 项通过。
- Full matrix: 20 pairs × 2 variants × 3 defenses = **120 samples**, **393 mock
  generations**, no execution errors. 完整矩阵 120 用例、393 次模拟生成，无执行错误。
- Every clean group completed 20/20 tasks, with no unauthorized calls or blocks.
  正常任务三组均完成 20/20，没有越权调用或拦截。
- The deliberately policy-blind mock followed the injected plans in both
  baseline and prompt modes. Enforced mode blocked all 20 attacked cases'
  unauthorized effects while preserving 20/20 legitimate task completions.
  故意忽略提示防御的模拟模型在 baseline/prompt 两组执行注入计划；enforced 阻断
  20 个攻击用例的越权效果，同时完成 20/20 个合法任务。
- These are expected scripted behaviors, **not measured real-model defense
  efficacy**. 这些是脚本预设行为，不是真实模型的防御效果成绩。
- Upstream Inspect emits a known retry deprecation warning per generation;
  the full suite emitted 411 warnings of this one type. 上游重试实现每次生成发出同类
  弃用提示，完整测试共 411 条；不影响本轮执行结果。

[English example report](examples/lab_mock.en.md) · [中文示例](examples/lab_mock.zh.md)

The normalized examples contain synthetic data only. Native logs remain local.
示例只含合成汇总；原生日志保留本地，不公开本机路径或未审查轨迹。

Real-model smoke status at v2.2: not run. The authorized server had available GPUs and
an existing inference runtime, but resolving the model download domain timed
out. No model was downloaded or loaded. This records the incomplete step rather
than claiming the full real-agent milestone is complete.
2.2 当时的真实模型试跑未完成：服务器有空闲 GPU 和已有推理环境，但下载域名解析超时；没有下载或加载
模型。本记录明确保留未完成步骤，不宣称真实 Agent 实验阶段已全部完成。

Pre-merge review reproduced and fixed mock-provider mislabeling and loss of partial goal/usage evidence after native errors. Three added regressions include a native Inspect provider-failure run.
合并前复现并修复了模拟提供商误标真实推理、报错后丢失部分攻击证据及用量的问题；新增三项回归，包含 Inspect 原生提供商失败场景。
