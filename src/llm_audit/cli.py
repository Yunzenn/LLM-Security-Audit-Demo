"""命令行入口"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel

from . import __version__
from .config import load_config, save_config, DEFAULT_CONFIG
from .engine import AuditEngine
from .attacks.loader import AttackLoader

console = Console()

BANNER = """
╔═══════════════════════════════════════════╗
║     🛡️  LLM Security Audit Tool  🛡️      ║
║          大语言模型安全审计工具            ║
╚═══════════════════════════════════════════╝
"""


@click.group()
@click.version_option(__version__, prog_name="llm-audit")
def main():
    """LLM 安全审计工具 - 自动化测试大语言模型的安全边界"""
    pass


@main.command()
@click.option("-c", "--config", "config_path", default=None, help="配置文件路径")
@click.option("--categories", default=None, help="测试类别 (逗号分隔)")
@click.option("--model", default=None, help="模型名称")
@click.option("--endpoint", default=None, help="API 端点")
@click.option(
    "--evaluator", default=None, type=click.Choice(["heuristic", "regex"]), help="评估方法"
)
@click.option("--output", "-o", default=None, help="输出目录")
@click.option("--format", "formats", default=None, help="报告格式 (逗号分隔: markdown,html)")
@click.option("--concurrency", default=None, type=int, help="并发数")
@click.option("--quick", is_flag=True, help="快速扫描 (提示注入和越狱类别)")
@click.option(
    "--lang", default=None, type=click.Choice(["zh", "en"]), help="报告语言 / report language"
)
def scan(
    config_path: Optional[str],
    categories: Optional[str],
    model: Optional[str],
    endpoint: Optional[str],
    evaluator: Optional[str],
    output: Optional[str],
    formats: Optional[str],
    concurrency: Optional[int],
    quick: bool,
    lang: Optional[str],
):
    """执行安全审计扫描"""
    console.print(BANNER)

    # 加载配置
    config = load_config(config_path)
    if lang:
        config.report.language = lang

    # 命令行参数覆盖配置
    if model:
        config.model.model_name = model
    if endpoint:
        config.model.endpoint = endpoint
    if evaluator:
        config.evaluator.method = evaluator
    if output:
        config.report.output_dir = output
    if concurrency is not None:
        if not 1 <= concurrency <= 64:
            raise click.BadParameter("concurrency must be between 1 and 64")
        config.test.concurrency = concurrency
    if formats:
        config.report.formats = [f.strip() for f in formats.split(",")]

    # 确定测试类别
    test_categories = None
    if categories:
        test_categories = [c.strip() for c in categories.split(",")]
    elif quick:
        test_categories = ["prompt_injection", "jailbreak"]

    # 显示配置
    console.print(
        Panel(
            f"[bold]模型:[/bold] {config.model.model_name}\n"
            f"[bold]端点:[/bold] {config.model.endpoint}\n"
            f"[bold]评估:[/bold] {config.evaluator.method}\n"
            f"[bold]类别:[/bold] {', '.join(test_categories or config.test.categories)}\n"
            f"[bold]输出:[/bold] {config.report.output_dir}",
            title="扫描配置",
            border_style="cyan",
        )
    )

    # 执行扫描
    async def run_scan():
        engine = AuditEngine(config)
        try:
            if not await engine.initialize():
                raise click.ClickException("Model initialization failed / 模型初始化失败")
            await engine.run(test_categories)
            engine.print_summary()
            engine.generate_reports()
        finally:
            await engine.close()

    try:
        asyncio.run(run_scan())
    except KeyboardInterrupt:
        console.print("\n[yellow]用户中断扫描[/yellow]")
        sys.exit(1)


@main.command()
@click.option("-c", "--config", "config_path", default=None, help="配置文件路径")
def list_attacks(config_path: Optional[str]):
    """列出所有可用的攻击用例"""
    config = load_config(config_path)
    loader = AttackLoader(config.test.custom_payloads_dir)

    categories = loader.list_categories()

    if not categories:
        console.print("[yellow]未找到攻击用例[/yellow]")
        return

    from rich.table import Table
    from rich import box

    table = Table(title="可用攻击用例", box=box.ROUNDED)
    table.add_column("类别", style="cyan")
    table.add_column("名称", style="green")
    table.add_column("用例数", justify="right")

    total = 0
    for cat in categories:
        table.add_row(cat["category"], cat["name"], str(cat["payload_count"]))
        total += cat["payload_count"]

    console.print(table)
    console.print(f"\n总计: {len(categories)} 个类别, {total} 个用例")


@main.command()
@click.option("-o", "--output", default="config.yaml", help="输出路径")
def init(output: str):
    """生成默认配置文件"""
    if Path(output).exists():
        if not click.confirm(f"配置文件 {output} 已存在，是否覆盖？"):
            return

    save_config(DEFAULT_CONFIG, output)
    console.print(f"[green]✓ 配置文件已生成: {output}[/green]")
    console.print("\n使用方法:")
    console.print(f"  1. 编辑 {output} 配置模型信息")
    console.print("  2. 运行 llm-audit scan 开始扫描")


@main.command()
@click.argument("old_config_path")
def migrate(old_config_path: str):
    """迁移 v1.0 配置文件到 v2.0"""
    import yaml
    from .config import migrate_old_config

    try:
        with open(old_config_path, "r", encoding="utf-8") as f:
            old_config = yaml.safe_load(f)
        new_config = migrate_old_config(old_config)
        save_config(new_config, "config.yaml")
        console.print("[green]✓ 配置迁移完成: config.yaml[/green]")
    except Exception as e:
        console.print(f"[red]迁移失败: {e}[/red]")


@main.command("inspect-scan")
@click.option("--dataset", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--model", required=True, help="Inspect model identifier, e.g. mockllm/model")
@click.option("--base-url", default=None, help="Optional provider API root / API 根地址")
@click.option("--output", default="reports/inspect", type=click.Path())
def inspect_scan(dataset: str, model: str, base_url: Optional[str], output: str):
    """Run the optional Inspect pilot / 运行可选 Inspect 试点。"""
    try:
        from inspect_ai import eval as inspect_eval
        from .adapters.inspect_backend import build_task
    except ImportError as error:
        raise click.ClickException(
            "Install the optional extra: pip install -e '.[inspect]'"
        ) from error
    payloads = AttackLoader().load_from_yaml(Path(dataset)).get_payloads()
    if not payloads:
        raise click.ClickException("Dataset is empty / 数据集为空")
    logs = inspect_eval(
        build_task(payloads), model=model, model_base_url=base_url, log_dir=output, display="none"
    )
    if not logs or any(
        log.status != "success" or log.error or any(sample.error for sample in log.samples or [])
        for log in logs
    ):
        raise click.ClickException("Inspect evaluation contains errors; inspect the native logs")
    console.print(f"Inspect logs / 轨迹: {output}")


@main.command("lab-eval")
@click.option("--model", default="mockllm/lab", show_default=True)
@click.option(
    "--dataset", default=None, type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option("--base-url", default=None)
@click.option("--model-revision", default="unverified")
@click.option(
    "--defense", type=click.Choice(["all", "baseline", "prompt", "enforced"]), default="all"
)
@click.option(
    "--variant", type=click.Choice(["all", "clean", "attack"]), default="all", show_default=True
)
@click.option("--split", type=click.Choice(["all", "dev", "holdout"]), default="dev")
@click.option("--pairs", default=None, help="Explicit comma-separated pair IDs / 指定任务对编号")
@click.option("--hf-options", default=None, help="Native HF settings JSON / 原生 HF 设置")
@click.option(
    "--chat-template-kwargs", default=None, help="Provider template JSON / 提供商模板参数"
)
@click.option(
    "--limit", type=click.IntRange(1, 20), default=20, help="Maximum task pairs / 任务对上限"
)
@click.option("--output", default="reports/lab", type=click.Path())
def lab_eval(
    model,
    dataset,
    base_url,
    model_revision,
    defense,
    variant,
    split,
    pairs,
    chat_template_kwargs,
    hf_options,
    limit,
    output,
):
    """Compare lab-agent defenses / 对比资料助手防御。"""
    import platform
    import json
    from importlib.metadata import version
    from .lab.environment import DEFENSES, POLICY_VERSION, SCORER_VERSION, load_cases
    from .lab.report import write_reports
    from .lab.provenance import select_cases, source_fingerprint

    initialization = {}
    if hf_options is not None:
        try:
            initialization = json.loads(hf_options)
            allowed = {"enable_thinking", "do_sample", "device", "torch_dtype"}
            if (
                not model.startswith("hf/")
                or not isinstance(initialization, dict)
                or not set(initialization) <= allowed
            ):
                raise ValueError("Invalid HF options")
            for key in ("enable_thinking", "do_sample"):
                if key in initialization and not isinstance(initialization[key], bool):
                    raise ValueError("Expected boolean")
            if "device" in initialization and not isinstance(initialization["device"], str):
                raise ValueError("Expected device string")
            if "torch_dtype" in initialization and initialization["torch_dtype"] not in {
                "bfloat16",
                "float16",
                "float32",
                "auto",
            }:
                raise ValueError("Invalid dtype")
        except (ValueError, TypeError):
            raise click.BadParameter(
                "Expected native hf/ options: enable_thinking, do_sample, device, torch_dtype",
                param_hint="--hf-options",
            ) from None

    template_options = None
    if chat_template_kwargs is not None:
        try:
            template_options = json.loads(chat_template_kwargs)
            if not isinstance(template_options, dict):
                raise ValueError("Expected JSON object")
        except ValueError:
            raise click.BadParameter(
                "Expected a JSON object", param_hint="--chat-template-kwargs"
            ) from None

    try:
        from inspect_ai import eval as inspect_eval
        from inspect_ai.model import get_model
        from .adapters.lab_backend import build_lab_task, scripted_lab_model
    except ImportError as error:
        raise click.ClickException(
            "Install optional dependencies: pip install -e '.[inspect]'"
        ) from error
    destination = Path(output).resolve()
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise click.ClickException(
            "Output directory must be empty / 输出目录必须为空，避免覆盖实验"
        )
    cases, digest = load_cases(dataset)
    try:
        selected = select_cases(cases, split, pairs, limit)
    except ValueError as error:
        raise click.BadParameter(str(error), param_hint="--pairs/--split/--limit") from None
    defenses = DEFENSES if defense == "all" else (defense,)
    variants = ("clean", "attack") if variant == "all" else (variant,)
    is_mock = model == "mockllm/lab"
    selected_model = (
        scripted_lab_model()
        if is_mock
        else (get_model(model, base_url=base_url, **initialization) if initialization else model)
    )
    logs = inspect_eval(
        build_lab_task(
            selected,
            defenses,
            variants=variants,
            chat_template_kwargs=template_options,
            provider=model.split("/", 1)[0],
        ),
        model=selected_model,
        model_base_url=base_url,
        log_dir=str(destination / "native"),
        display="none",
        max_samples=1,
    )
    rows = []
    for log in logs:
        for sample in log.samples or []:
            if sample.error or not sample.scores:
                row = dict(sample.metadata.get("lab_evidence", {}))
                row.update(
                    {
                        "pair_id": sample.metadata["case"]["id"],
                        "variant": sample.metadata["variant"],
                        "defense": sample.metadata["defense"],
                        "error": "Native sample error; inspect logs",
                    }
                )
            else:
                row = dict(next(iter(sample.scores.values())).metadata)
            row["elapsed_seconds"] = sample.total_time
            row["input_tokens"] = sum(usage.input_tokens for usage in sample.model_usage.values())
            row["output_tokens"] = sum(usage.output_tokens for usage in sample.model_usage.values())
            rows.append(row)
    expected = len(selected) * len(variants) * len(defenses)
    present = {(row["pair_id"], row["variant"], row["defense"]) for row in rows}
    for case in selected:
        for variant in variants:
            for mode in defenses:
                if (case.id, variant, mode) not in present:
                    rows.append(
                        {
                            "pair_id": case.id,
                            "variant": variant,
                            "defense": mode,
                            "error": "Missing native sample; run incomplete",
                        }
                    )
    manifest = {
        "experiment": "lab-v2-dev" if dataset and dataset.name == "lab_v2_dev.json" else "lab-v1",
        "execution": "scripted_mock"
        if is_mock
        else ("provider_mock" if model.startswith("mockllm/") else "real_model"),
        "aggregation_version": "lab-aggregate-v2",
        "completion_version": "response-evidence-v2",
        "model": model,
        "model_revision": "scripted-v1" if is_mock else model_revision,
        "dataset_sha256": digest,
        "dataset_id": dataset.name if dataset else "lab_v1.json",
        "source_sha256": source_fingerprint(),
        "source_hash_scheme": "relative-path-and-lf-python-v1",
        "pair_ids": [case.id for case in selected],
        "chat_template_kwargs": template_options,
        "hf_options": initialization,
        "split": split,
        "pair_count": len(selected),
        "expected_cases": expected,
        "defenses": list(defenses),
        "variants": list(variants),
        "policy_version": POLICY_VERSION,
        "scorer_version": SCORER_VERSION,
        "inspect_ai": version("inspect_ai"),
        "package_version": __version__,
        "python": platform.python_version(),
        "sampling": {"temperature": 0, "max_tokens": 512},
        "limits": {"messages": 32, "tokens": 8192, "seconds_per_sample": 90, "concurrency": 1},
    }
    paths = write_reports(rows, manifest, destination)
    for path in paths:
        console.print(str(path), markup=False)
    if (
        len(rows) != expected
        or any(log.status != "success" or log.error for log in logs)
        or any(row.get("error") for row in rows)
    ):
        raise click.ClickException(
            "Incomplete/error run; do not report it as a successful evaluation"
        )


if __name__ == "__main__":
    main()
