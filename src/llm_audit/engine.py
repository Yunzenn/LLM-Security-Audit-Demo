"""审计引擎 - 核心测试执行器"""

import asyncio
import json
import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from rich import box

from .config import AuditConfig
from .client.base import BaseLLMClient
from .client.openai_client import OpenAIClient
from .attacks.base import TestResult, AttackPayload
from .attacks.loader import AttackLoader
from .evaluator.base import BaseEvaluator
from .evaluator import get_evaluator
from .reporter.base import ReportData
from .reporter import get_reporter

console = Console()


class AuditEngine:
    """安全审计引擎"""

    def __init__(self, config: AuditConfig):
        self.config = config
        self.client: Optional[BaseLLMClient] = None
        self.evaluator: Optional[BaseEvaluator] = None
        self.results: list[TestResult] = []

    async def initialize(self):
        """初始化客户端和评估器"""
        self.client = OpenAIClient(self.config.model)
        self.evaluator = get_evaluator(self.config.evaluator.method)

        # 检查连接
        console.print("[blue]正在检查模型连接...[/blue]")
        if await self.client.health_check():
            console.print(f"[green]✓ 连接成功: {self.config.model.model_name}[/green]")
            return True
        else:
            console.print(f"[red]✗ 连接失败: {self.config.model.endpoint}[/red]")
            console.print("[yellow]请确保本地 LLM 服务 (如 Ollama) 已启动[/yellow]")
            return False

    async def run(self, categories: Optional[list[str]] = None) -> list[TestResult]:
        """执行安全审计"""
        # 加载攻击用例
        loader = AttackLoader(self.config.test.custom_payloads_dir)
        attacks = loader.load_all(categories or self.config.test.categories)

        if not attacks:
            console.print("[red]未找到可用的测试用例[/red]")
            return []

        # 统计总用例数
        total_payloads = sum(len(a.get_payloads()) for a in attacks)
        console.print(f"\n[bold cyan]开始安全审计[/bold cyan]")
        console.print(f"  测试类别: {len(attacks)} 个")
        console.print(f"  测试用例: {total_payloads} 个")
        console.print(f"  并发数: {self.config.test.concurrency}")
        console.print()

        self.results = []
        semaphore = asyncio.Semaphore(self.config.test.concurrency)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("测试进行中...", total=total_payloads)

            for attack in attacks:
                category = attack.get_category()
                payloads = attack.get_payloads()
                console.print(f"\n[cyan]━━━ {attack.get_name()} ({len(payloads)} 用例) ━━━[/cyan]")

                for payload in payloads:
                    async with semaphore:
                        result = await self._test_single(payload)
                        self.results.append(result)
                        self._print_result(result)
                        progress.advance(task)

                        # 请求间隔
                        if self.config.test.sleep_interval > 0:
                            await asyncio.sleep(self.config.test.sleep_interval)

        return self.results

    async def _test_single(self, payload: AttackPayload) -> TestResult:
        """执行单个测试"""
        for attempt in range(self.config.test.retry_count + 1):
            response = await self.client.query(payload.prompt)
            if response.success:
                evaluation = self.evaluator.evaluate(
                    payload.prompt, response.content, payload.category
                )
                return TestResult(
                    payload=payload,
                    response=response.content,
                    success=True,
                    latency_ms=response.latency_ms,
                    evaluation=evaluation.to_dict(),
                )

            if attempt < self.config.test.retry_count:
                await asyncio.sleep(1)

        return TestResult(
            payload=payload,
            response="",
            success=False,
            error=response.error,
            evaluation={"is_vulnerable": False, "severity": "error"},
        )

    def _print_result(self, result: TestResult):
        """打印测试结果"""
        if not result.success:
            console.print(f"  [yellow]⚠ {result.payload.name}: {result.error}[/yellow]")
            return

        sev = result.evaluation.get("severity", "unknown")
        is_vuln = result.evaluation.get("is_vulnerable", False)

        if is_vuln:
            color = {"medium": "yellow", "high": "red", "critical": "red bold"}.get(sev, "red")
            icon = "⚠" if sev == "medium" else "✗"
            console.print(f"  [{color}] {icon} {result.payload.name}: {sev.upper()}[/{color}]")
        else:
            console.print(f"  [green] ✓ {result.payload.name}: SAFE[/green]")

    def generate_reports(self) -> list[Path]:
        """生成报告"""
        if not self.results:
            console.print("[yellow]没有测试结果可生成报告[/yellow]")
            return []

        output_dir = Path(self.config.report.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        report_data = ReportData(
            model_name=self.config.model.model_name,
            model_endpoint=self.config.model.endpoint,
            results=self.results,
            config=self.config.model_dump(),
        )

        # 保存原始 JSON
        json_path = output_dir / f"raw_results_{report_data.timestamp_str}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump([r.to_dict() for r in self.results], f, ensure_ascii=False, indent=2)

        report_paths = [json_path]

        # 生成各格式报告
        for fmt in self.config.report.formats:
            try:
                reporter = get_reporter(fmt)
                path = reporter.generate(report_data, output_dir)
                report_paths.append(path)
                console.print(f"[green]✓ {fmt.upper()} 报告: {path}[/green]")
            except Exception as e:
                console.print(f"[red]✗ {fmt.upper()} 报告生成失败: {e}[/red]")

        return report_paths

    def print_summary(self):
        """打印测试摘要"""
        if not self.results:
            return

        total = len(self.results)
        vuln = sum(1 for r in self.results if r.evaluation.get("is_vulnerable"))
        safe = total - vuln - sum(1 for r in self.results if r.error)

        table = Table(title="审计结果摘要", box=box.ROUNDED)
        table.add_column("指标", style="cyan")
        table.add_column("数值", justify="right")

        table.add_row("总测试数", str(total))
        table.add_row("安全通过", f"[green]{safe}[/green]")
        table.add_row("潜在漏洞", f"[red]{vuln}[/red]" if vuln else "0")
        table.add_row("漏洞率", f"{vuln/total*100:.1f}%")

        console.print()
        console.print(table)

        # 风险等级
        if vuln == 0:
            console.print(Panel("[green bold]低风险 - 未发现明显漏洞[/green bold]", title="风险评估"))
        elif vuln / total < 0.2:
            console.print(Panel("[yellow bold]中风险 - 发现部分潜在漏洞[/yellow bold]", title="风险评估"))
        else:
            console.print(Panel("[red bold]高风险 - 发现多个潜在漏洞[/red bold]", title="风险评估"))

    async def close(self):
        """关闭客户端"""
        if self.client:
            await self.client.close()
