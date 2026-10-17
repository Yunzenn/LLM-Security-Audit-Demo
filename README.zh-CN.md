# 大模型应用安全审计

**用于大模型应用安全回归测试的 Python 工具集。**

[English](README.md) · [升级计划](docs/UPGRADE_PLAN.zh-CN.md) · [更新记录](CHANGELOG.md)

项目通过模型服务端点运行可配置的提示攻击用例，并记录明确的评测结果。可选的 [Inspect AI](https://inspect.aisi.org.uk/) 集成还支持在隔离的内存环境中，评测带工具调用的资料助手任务。项目关注可重复的实验、可观察的工具效果，以及对失败和未知结果的如实报告。

> **评测原型：** 本项目不是安全认证、生产环境防护组件或经过校准的基准。结果取决于模型、提示词、任务集和评分契约。解释任何分数前，请先阅读[评测状态与限制](#评测状态)。

## 当前能力

| 领域 | 当前支持 |
| --- | --- |
| 回归用例 | 内置 YAML 用例覆盖提示注入、越狱、信息泄露、编码绕过、多语言、多轮攻击和精确输出契约；也支持自定义 YAML 用例。 |
| 端点扫描 | 对配置的 OpenAI 兼容 Chat Completions 端点运行选定用例，支持有界并发、重试，以及 Markdown/HTML 报告。 |
| 结果语义 | 区分通过、失败、未知和执行错误。精确契约提供确定性判分；启发式发现仅作参考。缺少契约的结果不会被视为安全。 |
| Inspect 集成 | 可选使用 Inspect 原生任务和日志执行攻击用例扫描及配对资料助手评测。 |
| 资料助手评测 | 在相互隔离的合成环境中比较基线、提示防御和强制工具策略，并分别统计正常任务效用与安全结果。 |
| 实验复现 | 记录选定任务对、数据集和源码指纹、提供商参数、模型版本、逐例状态及资源用量。 |

## 快速开始

核心命令行支持 Python 3.10 及以上版本。只有需要 Inspect 原生任务和日志时才需安装可选集成。

```bash
python -m venv .venv
# 激活虚拟环境后安装：
pip install -e '.[dev,inspect]'

llm-audit --version
llm-audit list-attacks
llm-audit init --output config.yaml
```

编辑 `config.yaml`，填写本地可用或已获授权的 OpenAI 兼容端点、模型名称及凭证。不要把凭证提交到版本库。然后运行小规模扫描：

```bash
llm-audit scan --config config.yaml --quick --lang zh
```

报告写入配置的输出目录。内置端点只是 Ollama 风格的本地配置示例。扫描会将所选提示发送到你配置的服务端点，请根据数据内容和端点权限选择用例。

### 离线合成实验

资料助手评测默认使用脚本化 Mock，不调用模型 API，可用于检查任务执行、内存工具效果和权限策略；它不能衡量真实模型的安全性。

```bash
llm-audit lab-eval --split dev --output reports/lab-dev
# 完整合成回归矩阵：20 对任务 × 2 种变体 × 3 组防御。
llm-audit lab-eval --split all --output reports/lab-all
```

任务设计、评分和输出细节见[资料助手实验说明](docs/LAB_EXPERIMENT.zh-CN.md)。

## 真实模型试跑

首轮固定配置的 Qwen3-0.6B 原生 Hugging Face 实验在一张 RTX 3090 上完成 120 个用例，执行错误为零，共获得 262 次已完成的模型回复。各防御/任务变体组的精确任务完成率为 **5%–20%**。没有观察到越权尝试或执行，因此攻击目标零命中**不能证明防御有效**；正常任务效用偏低也限制了攻击对照的解释范围。

这是一次小模型单次贪心解码试跑，使用公开且模板相关的任务集，不能视为稳健性评估或 AgentDojo 成绩。失败分析既发现精确格式不匹配，也发现真实任务失败，例如模型声称消息已发送，但模拟发件箱中没有对应记录。实验后没有修改冻结的评分器。

- [实验结果与失败分析](docs/experiments/qwen3-pilot-2026-10-17/RESULTS.zh-CN.md)
- [复现指南](docs/REAL_MODEL_GUIDE.zh-CN.md)
- [冻结协议与来源记录](docs/experiments/qwen3-pilot-2026-10-17/PROTOCOL.md)

实验在项目隔离环境中成功运行原生 Hugging Face 推理。现有共享 vLLM 环境在启动检查时崩溃，因此保持原样；本次试跑没有验证 HTTP 服务部署。报告公开了已复核的合成记录及哈希，原生完整日志仍私下保留。

## 评测状态

已实现：YAML 提示攻击扫描、确定性输出契约、可选 Inspect 执行、配对资料助手合成任务，以及首次真实权重推理链路验证。

后续计划：版本化澄清任务契约、检查正常任务能力、加入受预算约束的自适应红队攻击、建立 AgentDojo 原生基线、复用 PyRIT 攻击策略，并开展范围明确的 REA/MCP 分析。这些工作尚未集成或验证。

完整路线见[中英文升级计划](docs/UPGRADE_PLAN.zh-CN.md)。[迁移与评分说明](docs/MIGRATION.zh-CN.md)介绍未知结果和精确契约的处理方式。

## 开发

```bash
pip install -e '.[dev,inspect]'
ruff check src tests
pytest -q
```

GitHub Actions 在 Python 3.10 和 3.12 检查核心包、构建 wheel，并运行 Inspect 集成任务。验证细节见[项目验证说明](docs/VALIDATION.md)。

## 许可证

[MIT](LICENSE)。第三方项目遵循其各自的许可证。
