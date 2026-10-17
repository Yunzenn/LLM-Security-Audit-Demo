# 真实权重资料助手评测

[English](REAL_MODEL_GUIDE.en.md)

可选 Inspect 后端支持已有的 OpenAI 兼容工具调用服务，也可直接使用原生 Hugging Face 后端。
本轮不新增通用 Agent 框架或自制推理服务器。

## 原生 HF

使用项目独立环境，安装 .[inspect]、兼容的 PyTorch、Transformers、Accelerate。
本轮记录版本为 Python 3.12.13、Torch 2.11.0+cu128、Transformers 4.57.6、Accelerate 1.15.0、
Inspect 0.3.281。依赖写入与缓存留在实验目录；可只读复用已有 Torch，但需记录这种依赖关系，
不能原地升级其他项目环境。

先准备固定版本的模型文件。主站不可达时，可仅为下载进程设置 HF_ENDPOINT 指向公开镜像，
不修改系统 DNS；下载后核对版本和哈希。本轮公开模型不需要向镜像发送账号令牌，
只下载 JSON、文本、safetensors、许可证，不执行远程自定义代码。

```bash
# LAB_RUNTIME 指向项目实验目录，LAB_MODEL_PATH 指向固定版本的模型目录。
export CUDA_VISIBLE_DEVICES=1
: "${LAB_RUNTIME:?请先设置项目内运行目录的绝对路径}"
: "${LAB_MODEL_PATH:?请先设置固定版本模型目录的绝对路径}"
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

LAB_MODEL_PATH 为绝对路径。绑定后 cuda:0 表示第一个可见 GPU，不是物理 0 号卡。
原生 HF 参数白名单只有 enable_thinking、do_sample、device、torch_dtype，其他参数在加载前拒绝。
贪心解码不使用温度、top-p、top-k；清单分别记录请求采样配置与 HF 设置，不能把这些参数当作同时生效。

去掉 --pairs 并设置 --split all 可运行全部 120 个用例。指定编号必须唯一、保持输入顺序、
属于所选分区且不超过 --limit，用于先做中英文平衡的兼容性检查。

## 已有 HTTP 服务

使用 --model openai-api/<served-name>、--base-url .../v1。
--chat-template-kwargs '{"enable_thinking":false}' 仅用于支持该请求字段的服务，原生 HF 使用
--hf-options。命令不启动或修理推理服务器；本轮共享 vLLM 环境启动崩溃，不宣称成功部署了 vLLM HTTP 服务。

## 完成证据与复现

Inspect 0.3.281 原生 HF 不填充结束原因。本项目的单样本 HF 循环仅在正常返回、文本非空、
没有待处理工具调用、生成长度严格小于 token 上限时推断提前结束，记录为 native_hf_early_stop_inferred。
缺失用量、触顶或待执行工具不能据此认定完成；其他提供商仍保留 unknown。
这只修正接口完成证据，不是语义判分，也没有改变冻结的任务/攻击目标契约。

清单保存编号、请求参数、数据集 SHA-256，以及“相对 Python 文件名＋LF 规范化字节”的源码指纹。
指纹可比较源码与安装包，但不是签名构建认证；另存源码提交、依赖、硬件、权重及原生日志哈希。
原始轨迹保留私有，只公开审查过的合成证据。

固定试跑协议见[此处](experiments/qwen3-pilot-2026-10-17/PROTOCOL.md)。
