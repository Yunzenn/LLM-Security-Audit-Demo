"""报告生成器基类"""

import datetime
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from ..attacks.base import TestResult


class ReportData:
    """报告数据"""

    def __init__(
        self,
        model_name: str,
        model_endpoint: str,
        results: list[TestResult],
        config: dict = None,
    ):
        self.model_name = model_name
        self.model_endpoint = model_endpoint
        self.results = results
        self.config = config or {}
        self.timestamp = datetime.datetime.now()
        self.timestamp_str = self.timestamp.strftime("%Y%m%d_%H%M%S")

    @property
    def total_tests(self) -> int:
        return len(self.results)

    @property
    def vuln_count(self) -> int:
        return sum(1 for r in self.results if r.evaluation.get("is_vulnerable"))

    @property
    def error_count(self) -> int:
        return sum(1 for r in self.results if r.error)

    @property
    def safe_count(self) -> int:
        return self.total_tests - self.vuln_count - self.error_count

    @property
    def vuln_rate(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return self.vuln_count / self.total_tests * 100

    @property
    def risk_level(self) -> str:
        if self.vuln_count == 0:
            return "low"
        if self.vuln_rate < 20:
            return "low"
        if self.vuln_rate < 50:
            return "medium"
        return "high"

    def get_category_stats(self) -> dict:
        """按类别统计"""
        stats = {}
        for r in self.results:
            cat = r.payload.category if r.payload else "unknown"
            if cat not in stats:
                stats[cat] = {"total": 0, "vuln": 0, "safe": 0, "error": 0}
            stats[cat]["total"] += 1
            if r.error:
                stats[cat]["error"] += 1
            elif r.evaluation.get("is_vulnerable"):
                stats[cat]["vuln"] += 1
            else:
                stats[cat]["safe"] += 1
        return stats

    def get_severity_stats(self) -> dict:
        """按严重性统计"""
        stats = {"safe": 0, "low": 0, "medium": 0, "high": 0, "critical": 0, "unknown": 0}
        for r in self.results:
            sev = r.evaluation.get("severity", "unknown")
            stats[sev] = stats.get(sev, 0) + 1
        return stats


class BaseReporter(ABC):
    """报告生成器基类"""

    @abstractmethod
    def generate(self, data: ReportData, output_path: Path) -> Path:
        """生成报告"""
        ...

    def get_file_extension(self) -> str:
        """获取文件扩展名"""
        return ".txt"
