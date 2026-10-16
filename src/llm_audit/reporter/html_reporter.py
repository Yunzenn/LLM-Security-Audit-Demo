"""Offline bilingual HTML reports with escaped model-generated content."""

from html import escape
from pathlib import Path
from .base import BaseReporter, ReportData
from .markdown_reporter import MarkdownReporter


class HtmlReporter(BaseReporter):
    def generate(self, data: ReportData, output_path: Path) -> Path:
        language = data.config.get("report", {}).get("language", "zh")
        path = output_path / f"Security_Report_{data.timestamp_str}.{language}.html"
        body = escape(MarkdownReporter()._render(data))
        document = (
            f'<!doctype html><html lang="{language}"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            "<title>LLM audit</title><style>body{max-width:1000px;margin:2rem auto;"
            "padding:1rem;font:16px system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere}"
            "</style><body><pre>" + body + "</pre></body></html>"
        )
        path.write_text(document, encoding="utf-8")
        return path

    def get_file_extension(self) -> str:
        return ".html"
