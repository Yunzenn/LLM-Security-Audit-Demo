"""LLM 客户端基类"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResponse:
    """LLM 响应结果"""

    success: bool
    content: str = ""
    error: Optional[str] = None
    latency_ms: float = 0.0


class BaseLLMClient(ABC):
    """LLM 客户端抽象基类"""

    @abstractmethod
    async def query(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """发送查询请求"""
        ...

    async def chat(self, messages: list[dict[str, str]]) -> LLMResponse:
        """A client must explicitly implement conversation support."""
        return LLMResponse(success=False, error="Client does not support multi-turn chat")

    @abstractmethod
    async def health_check(self) -> bool:
        """检查服务是否可用"""
        ...

    @abstractmethod
    async def close(self):
        """关闭客户端连接"""
        ...
