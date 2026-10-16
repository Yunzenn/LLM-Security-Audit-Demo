"""攻击模块基类"""

import datetime
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AttackPayload:
    """攻击载荷"""

    id: str
    category: str
    name: str
    prompt: str
    expected_behavior: str = "refuse"  # refuse | leak | comply
    severity: str = "high"  # high | medium | low
    tags: list[str] = field(default_factory=list)
    description: str = ""
    turns: list[str] = field(default_factory=list)
    system_prompt: str = ""
    forbidden_output: list[str] = field(default_factory=list)


def _generate_test_id() -> str:
    return f"TEST-{uuid.uuid4().hex}"


@dataclass
class TestResult:
    """测试结果"""

    test_id: str = field(default_factory=_generate_test_id)
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    payload: AttackPayload = None
    response: str = ""
    success: bool = True
    error: Optional[str] = None
    latency_ms: float = 0.0
    evaluation: dict = field(default_factory=dict)
    messages: list[dict[str, str]] = field(default_factory=list)
    attempts: int = 1
    attempt_records: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "test_id": self.test_id,
            "timestamp": self.timestamp,
            "payload_id": self.payload.id if self.payload else None,
            "category": self.payload.category if self.payload else None,
            "name": self.payload.name if self.payload else None,
            "prompt": self.payload.prompt if self.payload else None,
            "response": self.response,
            "success": self.success,
            "error": self.error,
            "latency_ms": self.latency_ms,
            "evaluation": self.evaluation,
            "messages": self.messages,
            "attempts": self.attempts,
            "attempt_records": self.attempt_records,
        }


class BaseAttack(ABC):
    """攻击模块基类"""

    @abstractmethod
    def get_payloads(self) -> list[AttackPayload]:
        """返回该类攻击的所有测试用例"""
        ...

    @abstractmethod
    def get_category(self) -> str:
        """返回攻击类别名称"""
        ...

    def get_name(self) -> str:
        """返回攻击类别显示名称"""
        return self.get_category()
