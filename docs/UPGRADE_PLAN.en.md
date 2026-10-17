# Upgrade plan and implementation status

[中文](UPGRADE_PLAN.zh-CN.md) · [Migration guide](MIGRATION.en.md)

Research snapshot: 2026-10-16. Project owner: Yunzenn. This roadmap describes
both delivered work and future milestones; planned integrations are not claims
of tested capability.

## Direction and reuse decisions

Build a Chinese/English RAG and tool-using agent security regression suite.
The project's original contribution should be tasks, benign controls, outcome
contracts, Banxuan integration, and reproducible defense comparisons.

| Component | Decision | Boundary |
| --- | --- | --- |
| [Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai) | Primary new evaluation backend; optional extra | Reuse execution and native logs rather than creating a general agent framework |
| [AgentDojo](https://github.com/ethz-spylab/agentdojo) | Later external benchmark subset | Preserve native environment/scoring; adapted tasks are not standard benchmark results |
| [PyRIT](https://github.com/microsoft/PyRIT) | Later optional red-team strategy adapter | Separate environment; pin a tested release instead of combining incompatible examples |
| [Promptfoo](https://github.com/promptfoo/promptfoo) | Alternative backend | Do not maintain two primary execution frameworks in the first version |
| [garak](https://github.com/NVIDIA/garak) | Optional external scan baseline | Import results instead of duplicating a broad probe library |
| [Guardrails](https://github.com/NVIDIA-NeMo/Guardrails) | Optional defensive baseline | Not a substitute for enforced tool permissions |
| [REA](https://github.com/morluto/rea) | Later analysis tool and MCP test target | Evidence collection is not proof of a vulnerability |

## Foundation iteration: delivered locally

- Bounded concurrent case workers with deterministic result ordering.
- Conversation history for actual multi-turn cases, isolated per case/retry.
- Four outcomes: pass, fail, unknown and error. Legacy rule matches are advisory.
- Exact forbidden-output contracts inspect every assistant turn. Refusal text
  cannot override an observed canary leak. Encoded or transformed leaks are not
  covered by an exact-string contract.
- Unknown/error samples are excluded from the scorable-rate denominator and
  reported separately. Zero scorable cases cannot produce a low-risk claim.
- Chinese and English Markdown/HTML reports. HTML contains escaped text and no
  remote scripts. JSON retains raw conversation evidence and needs appropriate
  handling before sharing.
- Optional Inspect adapter: 10 synthetic fixtures, including two conversations,
  exercise the same scorer with 12 mock generations. This validates plumbing,
  not a real model's attack resistance.
- Wheel-packaged YAML, regression tests and a CI workflow.

## Lab iteration: delivered offline

Twenty synthetic task pairs, three defenses, four in-memory tools, independent
utility/security/attack-goal contracts, bilingual summaries and the full
120-case mock matrix are implemented. Real-model endpoint validation remains
pending due to server download-domain DNS timeout. See
[experiment guide](LAB_EXPERIMENT.en.md). This is not an adaptive red/blue agent
implementation or a real-model security result.

## Red and blue agents

The red agent may modify only specified retrieval/tool-result content, within
fixed turn, token and time budgets. It cannot modify the system prompt, scorer,
secret store or defense. Fixed regression cases and adaptive searches must be
reported separately.

The online defender remains responsible for the legitimate task. Versioned
policies can provide source labeling and tool restrictions. A deterministic
execution boundary enforces permitted tools, argument ranges, file paths and
confirmation requirements; a second model does not grant authority.

An offline blue analysis agent may inspect failed traces and propose a small
defense change. Train/development data and a frozen evaluation set remain
separate. Changes must be tested independently, without changing the scorer to
make a defense appear successful.

The independent scorer checks synthetic canaries, attempted versus executed
unauthorized actions, memory/file state, and legitimate task completion.
Model grading is reserved for semantic judgments with human spot checks.
Agent roles use isolated histories; sharing a base model is disclosed as a
limitation.

## REA integration

REA here means Reverse Engineer Anything, not ReAct. The official project
offers MCP/CLI analysis for several application/artifact types, with different
engine requirements. Its own code and third-party engines have distinct
licensing terms. Local analysis does not imply that an attached remote model
never receives the resulting evidence.

Start with a small owned JavaScript application with known behavior. Collect
file positions, artifact hashes, tool versions, observations and unknowns.
Later, test whether an analysis agent follows injected instructions embedded in
artifact strings or tool results. Native ELF/Ghidra and Android samples are
later experiments, not current support claims. Existing Banxuan source does not
need to be reverse-engineered.

Static and runtime REA operations have different effects. Isolate actual tool
processes and mounts: configuring an Inspect Docker sandbox does not
automatically isolate every external MCP server or the Python host process.
See [Inspect sandboxing](https://inspect.aisi.org.uk/sandboxing.html).

## First real-agent experiment

Create a lab-document assistant with search, note-reading, to-do-writing and
simulated messaging tools. Pair each legitimate task with an injection variant.
Compare no additional defense, prompt-only defense, and enforced tool-policy
defense. Record final state rather than relying on the agent's self-report.
Use a text adapter first if Banxuan's voice service is not ready.

## Metrics and evidence

Report clean task completion, task completion under attack, attack success,
attempted/executed unauthorized actions, benign false blocks, scorable coverage,
errors, latency and model calls/tokens. Always state the denominators.
An attack-success reduction caused by refusing every task is not a useful
defense. Do not collapse utility and security into a universal safety score.

Record model/weights revision, sampling settings, task/defense/scorer revisions,
full traces and environment state. Repeat stochastic experiments, grouping
statistics by task rather than pretending successive attack turns are
independent samples. Preserve external framework logs alongside normalized
summaries. Never publish API keys or unreviewed private traces.

## Remaining milestones

1. Native-HF small-model validation is complete: [120-case pilot](experiments/qwen3-pilot-2026-10-17/RESULTS.en.md). The v2 task clarification run deviated from its clean-only matrix and its clean subset scored 0/12 in every defense; the [deviation report](experiments/lab-v2-dev-2026-10-17/RESULTS.en.md) records this. CLI 2.5 added explicit variant selection. The v3 dev-only diagnostic then matched its clean matrix but also scored 0/12; see [v3 results](experiments/lab-v3-dev-2026-10-17/RESULTS.en.md). Stop wording iterations with this model. Next, predeclare a separate dev-only capability check using a stronger model; do not tune on holdout or rescore v1. HTTP endpoint validation remains pending.
2. Defer adaptive red-team attacks until a versioned clean-task iteration demonstrates adequate utility. Then freeze target/configuration and task version, trial PyRIT in an isolated environment, and reuse existing strategies with explicit turn/token/time budgets. Distinguish proposed, attempted, executed and successful attacks; a zero-attempt run cannot validate a defense.
3. AgentDojo subset and frozen-set evaluation, with original benchmark results
   kept distinct from adaptations.
4. REA owned-JavaScript evidence pilot and one MCP injection scenario.
5. Banxuan memory/tool-confirmation adapter; embodied simulation only after the
   agent evaluation contract works.

At roughly 20 hours/week, the original estimate was four to five weeks for
these milestones, conditional on endpoint and tool availability. The current
foundation iteration does not imply that future milestones are complete.

## Resource and release policy

Keep external adapters optional and versioned; do not install every candidate.
Reuse one model sequentially across roles when GPU memory is constrained.
Limit workers, turns, tokens, cache and logs. Retain reproducibility evidence;
clean only this project's regenerable caches. Do not default to paid APIs.

Before release, verify wheel data, core-only imports, bilingual reports and
error handling. Dependencies were researched, not all integrated: current
PyRIT main has a different Python/dependency contract from its old tutorials;
REA main's package version is not proof of an identical published npm release.

## Primary references

- [Inspect agents](https://inspect.aisi.org.uk/agents.html)
- [Inspect sandbox boundaries](https://inspect.aisi.org.uk/sandboxing.html)
- [AgentDojo paper](https://arxiv.org/abs/2406.13352)
- [PyRIT dependency metadata](https://github.com/microsoft/PyRIT/blob/main/pyproject.toml)
- [REA prerequisites and tool boundaries](https://github.com/morluto/rea)
- [REA third-party notices](https://github.com/morluto/rea/blob/main/THIRD_PARTY_NOTICES.md)
