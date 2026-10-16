"""审计引擎 - 核心测试执行器"""

import asyncio
import json
from pathlib import Path
from typing import Optional

from rich.console import Console

from .config import AuditConfig
from .client.base import BaseLLMClient
from .client.openai_client import OpenAIClient
from .attacks.base import TestResult, AttackPayload
from .attacks.loader import AttackLoader
from .evaluator.contracts import score_output
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
        self.results = []
        # 加载攻击用例
        loader = AttackLoader(self.config.test.custom_payloads_dir)
        attacks = loader.load_all(categories or self.config.test.categories)

        if not attacks:
            console.print("[red]未找到可用的测试用例[/red]")
            return []

        # 统计总用例数
        total_payloads = sum(len(a.get_payloads()) for a in attacks)
        console.print("\n[bold cyan]开始安全审计[/bold cyan]")
        console.print(f"  测试类别: {len(attacks)} 个")
        console.print(f"  测试用例: {total_payloads} 个")
        console.print(f"  并发数: {self.config.test.concurrency}")
        console.print()

        payloads = [payload for attack in attacks for payload in attack.get_payloads()]
        queue = asyncio.Queue()
        for index, payload in enumerate(payloads):
            queue.put_nowait((index, payload))
        ordered = [None] * len(payloads)

        async def worker():
            while True:
                try:
                    index, payload = queue.get_nowait()
                except asyncio.QueueEmpty:
                    return
                try:
                    result = await self._test_single(payload)
                    ordered[index] = result
                    self._print_result(result)
                    if self.config.test.sleep_interval:
                        await asyncio.sleep(self.config.test.sleep_interval)
                finally:
                    queue.task_done()

        workers = [
            asyncio.create_task(worker())
            for _ in range(min(self.config.test.concurrency, len(payloads)))
        ]
        try:
            await asyncio.gather(*workers)
        finally:
            for task in workers:
                task.cancel()
            await asyncio.gather(*workers, return_exceptions=True)
        self.results = ordered
        return self.results

    async def _test_single(self, payload: AttackPayload) -> TestResult:
        """Retry whole isolated conversations; retain assistant output per turn."""
        if self.client is None or self.evaluator is None:
            raise RuntimeError("Initialize the engine before running tests")
        observed_outputs = []
        attempt_records = []
        latency = 0.0
        for attempt in range(self.config.test.retry_count + 1):
            messages = []
            outputs = []
            if payload.system_prompt:
                messages.append({"role": "system", "content": payload.system_prompt})
            response = None
            for turn in payload.turns or [payload.prompt]:
                messages.append({"role": "user", "content": turn})
                if payload.turns:
                    response = await self.client.chat([dict(message) for message in messages])
                else:
                    response = await self.client.query(turn, payload.system_prompt or None)
                latency += response.latency_ms
                if not response.success:
                    break
                outputs.append(response.content)
                messages.append({"role": "assistant", "content": response.content})
            observed_outputs.extend(outputs)
            attempt_records.append(
                {
                    "attempt": attempt + 1,
                    "messages": [dict(message) for message in messages],
                    "error": response.error if response is not None else "No response",
                }
            )
            if response is not None and response.success:
                evaluation = score_output(observed_outputs, payload.forbidden_output)
                signals = self.evaluator.evaluate(
                    payload.prompt, "\n".join(observed_outputs), payload.category
                )
                evaluation.details["advisory_signals"] = signals.to_dict()
                return TestResult(
                    payload=payload,
                    response="\n".join(observed_outputs),
                    success=True,
                    latency_ms=latency,
                    evaluation=evaluation.to_dict(),
                    messages=messages,
                    attempts=attempt + 1,
                    attempt_records=attempt_records,
                )
            if attempt < self.config.test.retry_count:
                await asyncio.sleep(1)
        return TestResult(
            payload=payload,
            response="\n".join(observed_outputs),
            success=False,
            error=response.error or "Request failed",
            latency_ms=latency,
            evaluation={
                "status": "error",
                "is_vulnerable": False,
                "severity": "error",
                "details": {
                    "partial_objective": score_output(
                        observed_outputs, payload.forbidden_output
                    ).to_dict()
                },
            },
            messages=messages,
            attempts=attempt + 1,
            attempt_records=attempt_records,
        )

    def _print_result(self, result: TestResult):
        status = result.evaluation.get("status", "unknown")
        console.print(f"  {result.payload.id}: {status.upper()}", markup=False)

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
        data = ReportData(self.config.model.model_name, self.config.model.endpoint, self.results)
        console.print(
            f"PASS={data.safe_count} FAIL={data.vuln_count} "
            f"UNKNOWN={data.unknown_count} ERROR={data.error_count}"
        )
        console.print(
            f"Scorable coverage: {data.coverage:.1f}% | "
            f"Exact-objective failure rate: {data.vuln_rate:.1f}%"
        )
        console.print(
            "Incomplete evidence / 证据不完整"
            if data.risk_level == "unknown"
            else "Scoped results only; no overall safety certification / 仅限本次测试目标"
        )

    async def close(self):
        """关闭客户端"""
        if self.client:
            await self.client.close()
