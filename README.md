# LLM Security Audit

**A Python toolkit for reproducible security regression testing of LLM applications.**

[中文说明](README.zh-CN.md) · [Upgrade plan](docs/UPGRADE_PLAN.en.md) · [Changelog](CHANGELOG.md)

LLM Security Audit runs configurable prompt attack cases against a model endpoint and records explicit evaluation outcomes. Its optional [Inspect AI](https://inspect.aisi.org.uk/) integration also runs paired, tool-using lab-assistant tasks with isolated in-memory state. The project focuses on repeatable experiments, observable tool effects and honest reporting of failures and unknowns.

> **Evaluation prototype:** This project is not a security certification, a production guardrail, or a calibrated benchmark. Results depend on the selected model, prompts, task set and scoring contracts. Review the [evaluation limitations](#evaluation-status) before interpreting a score.

## Capabilities

| Area | Available now |
| --- | --- |
| Regression cases | Bundled YAML cases for prompt injection, jailbreaks, information leakage, encoding bypass, multilingual inputs, multi-turn attacks and exact-output contracts; custom YAML cases are supported. |
| Endpoint scans | Run selected cases against a configured OpenAI-compatible chat-completions endpoint, with bounded concurrency, retries and Markdown/HTML reports. |
| Outcome semantics | Distinguish pass, fail, unknown and execution error. Exact contracts are deterministic; heuristic findings are advisory. Missing contracts do not count as safe. |
| Inspect integration | Optional native Inspect tasks and logs for attack-case scans and paired lab-assistant evaluations. |
| Lab evaluation | Compare baseline, prompt-only and enforced tool policies in isolated synthetic environments. Score task utility and security outcomes separately. |
| Reproducibility | Record selected pairs, dataset and source fingerprints, provider settings, model revision, per-case state and resource usage. |

## Quick start

Python 3.10 or later is supported for the core CLI. Install the optional Inspect integration only if you need its native tasks and logs.

```bash
python -m venv .venv
# Activate the environment, then install:
pip install -e '.[dev,inspect]'

llm-audit --version
llm-audit list-attacks
llm-audit init --output config.yaml
```

Edit `config.yaml` for your locally available or otherwise authorized OpenAI-compatible endpoint, model name and credentials. Keep credentials out of source control. Then run a small scan:

```bash
llm-audit scan --config config.yaml --quick --lang en
```

Reports are written to the configured output directory. The bundled default endpoint is a local Ollama-style address; it is only a configuration example. The scan sends selected prompts to the endpoint you configure, so choose data and endpoints accordingly.

### Offline synthetic lab run

The default lab model is a scripted mock. It makes no model API calls and is useful for checking task execution, in-memory tool effects and policy enforcement. It does not measure a real model's safety.

```bash
llm-audit lab-eval --split dev --output reports/lab-dev
# Full synthetic regression matrix: 20 task pairs × 2 variants × 3 defenses.
llm-audit lab-eval --split all --output reports/lab-all
```

See the [lab experiment guide](docs/LAB_EXPERIMENT.en.md) for task design, scoring and output details.

## Real-model pilot

The first fixed Qwen3-0.6B native-Hugging-Face run completed 120 cases on one RTX 3090. It had zero execution errors and 262 completed model responses. Exact task utility ranged from **5% to 20%** across defense/variant groups. No unauthorized action was attempted or executed, so the zero attack-goal count does **not** show that any defense worked. The low utility also limits interpretation of the attack comparison.

The run is a single greedy-decoding pilot on a small, public, template-related task set. It is not a robustness estimate or an AgentDojo result. Failure analysis found both exact-format mismatches and real task failures, including a claimed message send with no corresponding simulated outbox entry. The frozen scorer was not changed after the run.

- [Results and failure analysis](docs/experiments/qwen3-pilot-2026-10-17/RESULTS.en.md)
- [Reproduction guide](docs/REAL_MODEL_GUIDE.en.md)
- [Frozen protocol and provenance](docs/experiments/qwen3-pilot-2026-10-17/PROTOCOL.md)

Native Hugging Face inference succeeded in a project-isolated runtime. The existing shared vLLM runtime failed its startup checks and was left untouched; HTTP serving is not validated by this pilot. The report publishes reviewed synthetic records and hashes while keeping raw native logs private.

A follow-up v2 clean-task run on the same dev tasks completed without execution errors, but the CLI also included injected variants, contrary to its preregistered 36-sample clean-only matrix. The clean subset achieved **0/12** in each defense. This run is published as a deviation and exploratory diagnostic, not as the preregistered primary result; the accidentally included attack rows do not establish defense efficacy. CLI 2.5 adds explicit `--variant clean|attack|all` selection. The utility gate failed, so adaptive red teaming remains deferred.

- [v2 execution deviation and results](docs/experiments/lab-v2-dev-2026-10-17/RESULTS.en.md)
- [v2 frozen protocol](docs/experiments/lab-v2-dev-2026-10-17/PROTOCOL.en.md)

## Evaluation status

Implemented: YAML prompt-attack scans, deterministic output contracts, optional Inspect execution, synthetic paired lab tasks, a first real-weight execution pilot, versioned task-contract data, and explicit clean/injected variant selection.

The v3 diagnostic run matched its 36-sample clean-only protocol but scored 0/12 in every defense. This confirms that additional wording changes on the same tasks are not justified with Qwen3-0.6B; see the [v3 results](docs/experiments/lab-v3-dev-2026-10-17/RESULTS.en.md). Next, assess a separately selected stronger model on dev tasks only. Do not use holdout to tune. Adaptive red-team attacks remain gated on adequate clean-task utility; AgentDojo, PyRIT strategy reuse and focused REA/MCP analysis remain later milestones.

Start with the [bilingual upgrade plan](docs/UPGRADE_PLAN.en.md). The [migration and scoring guide](docs/MIGRATION.en.md) describes how unknown results and exact contracts are handled.

## Development

```bash
pip install -e '.[dev,inspect]'
ruff check src tests
pytest -q
```

The GitHub Actions workflow checks the core package on Python 3.10 and 3.12, builds a wheel and runs the Inspect integration job. See [contributing and validation notes](docs/VALIDATION.md).

## License

[MIT](LICENSE). Third-party projects retain their own licenses.
