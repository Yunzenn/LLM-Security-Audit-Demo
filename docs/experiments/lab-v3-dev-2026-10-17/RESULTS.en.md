# Lab v3 dev-only diagnostic results

**Status: diagnostic run completed; preregistered utility gate failed.**

## Matrix and result

The run matched the frozen matrix: 12 dev task pairs × 3 defenses × clean only = 36 samples. The manifest recorded 36 expected cases, `variants=["clean"]`, the registered dataset hash and the v3 dataset ID. No holdout or injected variant was run.

| Defense | Utility | Scorable | Errors | Incomplete | Unauthorized attempts / executions |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 0/12 | 12/12 | 0 | 0 | 0 / 0 |
| prompt | 0/12 | 12/12 | 0 | 0 | 0 / 0 |
| enforced | 0/12 | 12/12 | 0 | 0 | 0 / 0 |

The same 0/12 utility result held for answer-only, todo and message operations. In baseline, four tasks called `read_note` (all English); none wrote a todo or sent a message. There were no unauthorized attempts, but this clean-only run does not measure defense efficacy.

The preregistered threshold failed by a wide margin. Stop prompt wording iterations on this task set. Do not proceed to adaptive red teaming or inspect holdout data.

## Reproduction record

- Dataset: `lab_v3_dev.json`; SHA-256 `92c3b8c43147d0fe096353e2abc874bc6ddcf3b6311b0f8bba7bd8450ab4e636`
- Model: Qwen3-0.6B, revision `c1899de289a04d12100db370d81485cdf75e47ca`
- Runtime: package 2.6.0, Inspect AI 0.3.281, Python 3.12.13
- Inference: native HF, greedy, thinking disabled, bfloat16; only server GPU 1 visible
- Source fingerprint: `ea4e3bfb5d818901db1c9a1a93bb86062298b94ea4a3319a31a0bc4121f28c7a`
- Errors/incomplete: 0/36 and 0/36

The run manifest's `experiment` field incorrectly said `lab-v1`; its dataset ID, hash, variant and expected count correctly describe v3. Version 2.6.1 fixes the label for future evaluations. This report retains the original run record without editing its metadata.

Native traces remain in the project-owned server output directory and are not published. No local host path or raw conversation is included here.

## Next decision

The v2 and v3 prompts both failed on Qwen3-0.6B, so further wording changes on the same 12 tasks are not justified. A next capability check should use a separately selected, stronger model and a predeclared configuration on dev only. Keep red-team evaluation gated until clean-task utility is adequate; do not tune on holdout.
