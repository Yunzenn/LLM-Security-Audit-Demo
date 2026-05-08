"""评估器基类"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EvalResult:
    """评估结果"""
    is_vulnerable: bool = False
    severity: str = "safe"  # safe | low | medium | high | critical
    confidence: float = 0.0  # 0.0 - 1.0
    flags: list[str] = field(default_factory=list)
    reason: str = ""
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "is_vulnerable": self.is_vulnerable,
            "severity": self.severity,
            "confidence": self.confidence,
            "flags": self.flags,
            "reason": self.reason,
            "details": self.details,
        }


class BaseEvaluator(ABC):
    """评估器抽象基类"""

    @abstractmethod
    def evaluate(self, prompt: str, response: str, category: str = "") -> EvalResult:
        """评估模型回复的安全性"""
        ...

    def batch_evaluate(self, items: list[tuple[str, str, str]]) -> list[EvalResult]:
        """批量评估"""
        return [self.evaluate(prompt, response, category) for prompt, response, category in items]
