"""报告生成模块"""

from .base import BaseReporter
from .markdown_reporter import MarkdownReporter
from .html_reporter import HtmlReporter

__all__ = ["BaseReporter", "MarkdownReporter", "HtmlReporter"]


def get_reporter(format: str) -> BaseReporter:
    """获取报告生成器实例"""
    reporters = {
        "markdown": MarkdownReporter,
        "html": HtmlReporter,
    }
    if format not in reporters:
        raise ValueError(f"不支持的报告格式: {format}，可选: {list(reporters.keys())}")
    return reporters[format]()
