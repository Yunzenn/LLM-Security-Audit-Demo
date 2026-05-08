"""OpenAI 兼容客户端 (支持 Ollama, vLLM, LM Studio 等)"""

import time
from typing import Optional

import httpx

from ..config import ModelConfig
from .base import BaseLLMClient, LLMResponse


class OpenAIClient(BaseLLMClient):
    """OpenAI Chat Completions API 兼容客户端"""

    def __init__(self, config: ModelConfig):
        self.config = config
        self._client = httpx.AsyncClient(
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config.api_key}",
            },
            timeout=config.timeout,
        )

    async def query(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """发送查询请求"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.config.model_name,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "stream": False,
        }

        start_time = time.monotonic()
        try:
            response = await self._client.post(self.config.endpoint, json=payload)
            response.raise_for_status()
            data = response.json()
            latency = (time.monotonic() - start_time) * 1000

            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                return LLMResponse(success=True, content=content.strip(), latency_ms=latency)
            else:
                return LLMResponse(success=False, error=f"响应格式异常: {data}")

        except httpx.TimeoutException:
            return LLMResponse(success=False, error="请求超时")
        except httpx.ConnectError:
            return LLMResponse(success=False, error="连接失败 (请检查服务是否启动)")
        except httpx.HTTPStatusError as e:
            return LLMResponse(success=False, error=f"HTTP 错误: {e.response.status_code}")
        except Exception as e:
            return LLMResponse(success=False, error=str(e))

    async def health_check(self) -> bool:
        """检查服务是否可用"""
        response = await self.query("Hi")
        return response.success

    async def close(self):
        """关闭客户端"""
        await self._client.aclose()
