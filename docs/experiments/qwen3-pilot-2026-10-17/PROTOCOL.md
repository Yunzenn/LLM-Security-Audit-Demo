# Fixed small-model pilot / 固定小模型试跑

Date / 日期: 2026-10-17 (Asia/Shanghai).

This protocol accompanies the first real-weight lab evaluation. It tests the
execution/scoring integration and a small policy comparison, not model safety
in general. No real tools or external recipients are available to the agent.
本轮验证真实权重下的执行/评分与小规模防御对照，不作模型整体安全结论；被测 Agent 只能访问内存合成工具。

- Model / 模型: Qwen/Qwen3-0.6B, revision `c1899de289a04d12100db370d81485cdf75e47ca`.
- Download / 下载: public HF-Mirror snapshot, only JSON/text/safetensors/license
  files, no custom remote code. The downloaded weight SHA-256 matches the
  snapshot metadata: `f47f71177f32bcd101b7573ec9171e6a57f4f4d31148d38e382306f42996874b`.
  镜像下载，固定版本并校验文件一致性，不执行远程自定义代码；这不是独立来源的供应链认证。
- Backend / 后端: Inspect AI 0.3.281 native HF, Transformers 4.57.6,
  Accelerate 1.15.0, PyTorch 2.11.0+cu128, Python 3.12.13.
- Hardware / 硬件: one RTX 3090 24GiB, physical GPU 1; GPU 0 left untouched.
  Only this experiment's process and cache directories are used. Own packages
  are installed in a project environment; the existing Torch installation is
  reused read-only. Native HF was chosen after the existing shared vLLM runtime
  crashed during startup checks. No shared environment was repaired or upgraded.
  使用空闲 1 号卡；自有依赖写入独立环境，已有 Torch 只读复用；未修补共享 vLLM 环境。
- Decoding / 解码: BF16, non-thinking, greedy (`do_sample=false`), one item per
  batch, at most 512 generated tokens; fixed tool-loop sample limits unchanged.
- Cohort / 样本: unchanged `scenarios/lab_v1.json`, all 20 pairs, clean and
  injected variants, all three defenses: 120 planned cases. Dev and public
  template-related holdout strata are reported separately from the same run.
- Frozen / 冻结: task text, attack plans, capabilities, utility and attack-goal
  contracts are unchanged from v2.2. Source/dataset hashes are recorded in the
  manifest. No prompt tuning between dev and holdout.
- Completion / 完成证据: `response-evidence-v2`; explicit provider stops are
  accepted. Inspect's native HF provider omits the reason; normal non-tool
  output strictly below the generated-token cap is marked
  `native_hf_early_stop_inferred`. Capped/missing usage remains unknown. This
  fallback is specific to the single-item HF batch; it is not applied to other
  providers. The reason is retained per sample.

Two dev pairs were used for compatibility preflight. An initial dev run was
interrupted after the missing finish reason was identified. Those runs are
retained privately and excluded from the primary comparison; the fixed cohort
is rerun after the completion adapter correction. This changes transport-level
completion evidence, not the task or attack outcome contracts.
先用两个开发任务对检查兼容性；发现结束原因缺失后，中断了早期开发运行并保留日志。
正式对照在修正接口完成证据后重跑，未改变任务或攻击目标判分条件。

Report utility / all planned cases, observed attack goals / scorable cases,
coverage, errors, unauthorized attempts/executions, blocks, completed model
responses, token usage and elapsed time. Native logs remain private; publish
only reviewed synthetic evidence and aggregates with local host paths removed.
Zero observed attacks alongside poor utility is not a successful defense.
仅公开已审查的合成证据及脱敏汇总。正常任务完成率低时，攻击目标零命中不能被解读为防御成功。

One greedy repetition is a pilot, not a robustness estimate or a standard
AgentDojo result. Exact text/state contracts do not grade semantic equivalence.
Any formatting sensitivity discovered here must be disclosed rather than
changing the scorer to improve this run's score.
单次贪心试跑不是稳健性估计，也不是 AgentDojo 标准成绩；精确契约不判断语义等价。
若发现格式敏感性，应披露限制，不能为提高本轮分数事后修改评分。
