"""报告生成器基类"""

import datetime
from abc import ABC, abstractmethod
from pathlib import Path

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

    @staticmethod
    def outcome(result: TestResult) -> str:
        if not result.success or result.error:
            return "error"
        status = result.evaluation.get("status", "unknown")
        return status if status in {"pass", "fail", "unknown", "error"} else "unknown"

    @property
    def vuln_count(self) -> int:
        return sum(self.outcome(result) == "fail" for result in self.results)

    @property
    def error_count(self) -> int:
        return sum(self.outcome(result) == "error" for result in self.results)

    @property
    def unknown_count(self) -> int:
        return sum(self.outcome(result) == "unknown" for result in self.results)

    @property
    def safe_count(self) -> int:
        return sum(self.outcome(result) == "pass" for result in self.results)

    @property
    def scorable_count(self) -> int:
        return self.safe_count + self.vuln_count

    @property
    def coverage(self) -> float:
        return 100 * self.scorable_count / self.total_tests if self.total_tests else 0.0

    @property
    def vuln_rate(self) -> float:
        return 100 * self.vuln_count / self.scorable_count if self.scorable_count else 0.0

    @property
    def risk_level(self) -> str:
        # Never turn missing/error evidence into a low-risk conclusion.
        if self.scorable_count < self.total_tests or not self.scorable_count:
            return "unknown"
        return "observed_failures" if self.vuln_count else "no_observed_failures"

    def get_category_stats(self) -> dict:
        stats = {}
        keys = {"pass": "safe", "fail": "vuln", "unknown": "unknown", "error": "error"}
        for result in self.results:
            category = result.payload.category if result.payload else "unknown"
            counts = stats.setdefault(
                category, {"total": 0, "vuln": 0, "safe": 0, "unknown": 0, "error": 0}
            )
            counts["total"] += 1
            counts[keys[self.outcome(result)]] += 1
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
