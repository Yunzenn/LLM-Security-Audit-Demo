# Real-weight lab evaluation

[中文](REAL_MODEL_GUIDE.zh-CN.md)

The optional Inspect dependency supports two distinct paths: an existing
OpenAI-compatible tool-calling endpoint, and Inspect's native Hugging Face
backend. No general agent framework or custom inference server is added here.

## Native HF

Use a project environment with `.[inspect]`, a compatible PyTorch build,
Transformers and Accelerate. The recorded pilot uses Python 3.12.13, Torch
2.11.0+cu128, Transformers 4.57.6, Accelerate 1.15.0 and Inspect 0.3.281.
Keep dependencies and caches inside the selected experiment workspace. Reusing
an existing Torch installation read-only is possible but that dependency must
be recorded; do not upgrade another project's environment in place.

Prepare the model before running. If the main Hub is unreachable, a public
mirror may be selected for the download process with `HF_ENDPOINT`; this is
not a system DNS change. Pin the snapshot revision and verify the downloaded
file hashes. Do not pass account tokens to third-party mirrors for this public
model. The pilot used only JSON/text/safetensors/license files and no custom
remote model code.

```bash
# Set these to project-owned directories and your free GPU.
: "${LAB_RUNTIME:?Set an absolute project-owned runtime directory first}"
: "${LAB_MODEL_PATH:?Set an absolute pinned snapshot directory first}"
export CUDA_VISIBLE_DEVICES=1
export HF_HOME="$LAB_RUNTIME/cache/huggingface"
export HF_HUB_OFFLINE=1
export HF_HUB_DISABLE_TELEMETRY=1
export XDG_DATA_HOME="$LAB_RUNTIME/data"
export XDG_CACHE_HOME="$LAB_RUNTIME/cache"
export CUDA_CACHE_PATH="$LAB_RUNTIME/cache/cuda"
export TRITON_CACHE_DIR="$LAB_RUNTIME/cache/triton"
export TORCHINDUCTOR_CACHE_DIR="$LAB_RUNTIME/cache/torchinductor"
export TMPDIR="$LAB_RUNTIME/tmp"
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=4
mkdir -p "$XDG_DATA_HOME" "$XDG_CACHE_HOME" "$TMPDIR"

llm-audit lab-eval --model "hf/$LAB_MODEL_PATH" \
  --model-revision c1899de289a04d12100db370d81485cdf75e47ca \
  --hf-options '{"enable_thinking":false,"do_sample":false,"device":"cuda:0","torch_dtype":"bfloat16"}' \
  --pairs lab_01,lab_11 --limit 2 --defense baseline \
  --output "$LAB_RUNTIME/outputs/native-smoke"
```

`LAB_MODEL_PATH` is an absolute directory containing the pinned snapshot.
`cuda:0` refers to the first *visible* GPU after binding, not physical GPU 0.
The supported non-secret HF initialization options are `enable_thinking`,
`do_sample`, `device` and `torch_dtype`. Unsupported options are rejected before
model initialization. Greedy decoding does not use temperature/top-p/top-k;
the manifest distinguishes the requested sampling config and HF options.

Use `--split all` without `--pairs` for all 120 cases. Explicit pairs are
comma-separated, ordered, unique, constrained to `--split`, and bounded by
`--limit`. This supports a balanced Chinese/English compatibility preflight.

## Existing HTTP endpoint

For an OpenAI-compatible server, use `--model openai-api/<served-name>` and
`--base-url .../v1`. `--chat-template-kwargs '{"enable_thinking":false}'` forwards
provider-specific request parameters through Inspect. It is intended for
endpoints that support them; native HF instead uses `--hf-options`. The command
does not launch or repair a server. The pilot's shared vLLM runtime crashed on
startup, so no successful vLLM HTTP deployment is claimed.

## Completion and provenance

Inspect 0.3.281's native HF API leaves the finish reason unknown. This suite's
single-item HF loop accepts a normal, nonempty, non-tool return strictly below
the generated-token cap as `native_hf_early_stop_inferred`. Missing usage,
capped output or pending tools cannot establish completion. Other providers'
unknown finish reasons remain unknown. This is explicit transport evidence,
not semantic grading or a change to the frozen task/attack contracts.

The manifest includes the selected pair IDs, requested provider settings,
dataset SHA-256, and a source fingerprint over relative Python file names and
LF-normalized bytes. The fingerprint is portable between a checkout and its
wheel; it is not a signed build attestation. Record the source commit, dependency
versions, hardware, downloaded weight hash, and run/native-log hashes alongside
it. Retain raw logs privately and publish reviewed synthetic evidence only.

The fixed pilot protocol is [here](experiments/qwen3-pilot-2026-10-17/PROTOCOL.md).
The observed results and failure analysis are
[here](experiments/qwen3-pilot-2026-10-17/RESULTS.en.md).
