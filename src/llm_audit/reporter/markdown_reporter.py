"""Bilingual, evidence-scoped Markdown reports."""

import html
from pathlib import Path
from .base import BaseReporter, ReportData

LABELS = {
    "en": [
        "LLM security evaluation",
        "Metric",
        "Value",
        "Total",
        "Passed objective",
        "Failed objective",
        "Unknown",
        "Execution errors",
        "Scorable coverage",
        "Failure rate (scorable only)",
        "Results",
        "ID",
        "Category",
        "Outcome",
        "Reason",
        "No general safety conclusion. Rule matches are advisory, not verified vulnerabilities.",
        "N/A: no scorable cases",
    ],
    "zh": [
        "LLM 安全评测",
        "指标",
        "数值",
        "总数",
        "目标通过",
        "目标失败",
        "无法判定",
        "执行错误",
        "有效判分覆盖率",
        "失败率（仅有效判分）",
        "结果",
        "编号",
        "类别",
        "判定",
        "依据",
        "不作整体安全性结论。关键词命中是辅助信号，不是已确认漏洞。",
        "不适用：没有可判分用例",
    ],
}


def cell(value: object) -> str:
    return html.escape(str(value)).replace("|", "&#124;").replace("\n", "<br>")


class MarkdownReporter(BaseReporter):
    def generate(self, data: ReportData, output_path: Path) -> Path:
        language = data.config.get("report", {}).get("language", "zh")
        path = output_path / f"Security_Report_{data.timestamp_str}.{language}.md"
        path.write_text(self._render(data), encoding="utf-8")
        return path

    def _render(self, data: ReportData) -> str:
        labels = LABELS[data.config.get("report", {}).get("language", "zh")]
        rate = f"{data.vuln_rate:.1f}%" if data.scorable_count else labels[16]
        values = [
            data.total_tests,
            data.safe_count,
            data.vuln_count,
            data.unknown_count,
            data.error_count,
            f"{data.coverage:.1f}%",
            rate,
        ]
        lines = [
            f"# {labels[0]}",
            "",
            f"Model: {cell(data.model_name)}",
            "",
            labels[15],
            "",
            f"| {labels[1]} | {labels[2]} |",
            "| --- | --- |",
        ]
        lines.extend(f"| {label} | {value} |" for label, value in zip(labels[3:10], values))
        lines.extend(
            [
                "",
                f"## {labels[10]}",
                "",
                "| " + " | ".join(labels[11:15]) + " |",
                "| --- | --- | --- | --- |",
            ]
        )
        for result in data.results:
            lines.append(
                "| "
                + " | ".join(
                    cell(value)
                    for value in [
                        result.payload.id if result.payload else result.test_id,
                        result.payload.category if result.payload else "unknown",
                        data.outcome(result),
                        result.error or result.evaluation.get("reason", ""),
                    ]
                )
                + " |"
            )
        return "\n".join(lines) + "\n"

    def get_file_extension(self) -> str:
        return ".md"
