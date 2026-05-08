"""配置管理模块"""

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """模型连接配置"""
    provider: str = Field(default="openai", description="提供商: openai | ollama")
    endpoint: str = Field(default="http://localhost:11434/v1/chat/completions", description="API 端点")
    model_name: str = Field(default="deepseek-r1:1.5b", description="模型名称")
    api_key: str = Field(default="ollama", description="API Key")
    timeout: int = Field(default=60, description="请求超时(秒)")
    max_tokens: int = Field(default=512, description="最大生成 token 数")
    temperature: float = Field(default=0.7, description="生成温度")


class TestConfig(BaseModel):
    """测试配置"""
    categories: list[str] = Field(
        default=["prompt_injection", "jailbreak", "info_leakage"],
        description="启用的测试类别"
    )
    concurrency: int = Field(default=3, description="并发测试数")
    retry_count: int = Field(default=2, description="失败重试次数")
    sleep_interval: float = Field(default=0.5, description="请求间隔(秒)")
    custom_payloads_dir: Optional[str] = Field(default=None, description="自定义用例目录")


class EvaluatorConfig(BaseModel):
    """评估器配置"""
    method: str = Field(default="heuristic", description="评估方法: heuristic | regex | llm_judge")
    judge_model: Optional[str] = Field(default=None, description="LLM Judge 模型 (仅 llm_judge 方法)")


class ReportConfig(BaseModel):
    """报告配置"""
    output_dir: str = Field(default="./reports", description="输出目录")
    formats: list[str] = Field(default=["markdown", "html"], description="报告格式")


class AuditConfig(BaseModel):
    """主配置"""
    model: ModelConfig = Field(default_factory=ModelConfig)
    test: TestConfig = Field(default_factory=TestConfig)
    evaluator: EvaluatorConfig = Field(default_factory=EvaluatorConfig)
    report: ReportConfig = Field(default_factory=ReportConfig)


DEFAULT_CONFIG = AuditConfig()


def load_config(config_path: Optional[str] = None) -> AuditConfig:
    """加载配置文件，如果不存在则返回默认配置"""
    if config_path is None:
        # 尝试常见位置
        candidates = [
            "config.yaml",
            "config.yml",
            os.path.expanduser("~/.llm-audit/config.yaml"),
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                config_path = candidate
                break

    if config_path is None or not os.path.exists(config_path):
        return DEFAULT_CONFIG

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if data is None:
            return DEFAULT_CONFIG
        return AuditConfig(**data)
    except Exception as e:
        print(f"[!] 配置文件解析失败，使用默认配置: {e}")
        return DEFAULT_CONFIG


def save_config(config: AuditConfig, config_path: str = "config.yaml"):
    """保存配置到文件"""
    data = config.model_dump()
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)


# 兼容旧配置格式
def migrate_old_config(old_config: dict) -> AuditConfig:
    """将 v1.0 配置格式迁移到 v2.0"""
    model_data = old_config.get("model", {})
    test_data = old_config.get("security_tests", {})
    report_data = old_config.get("report", {})

    categories = []
    if test_data.get("enable_prompt_injection", True):
        categories.append("prompt_injection")
    if test_data.get("enable_jailbreak", True):
        categories.append("jailbreak")
    if test_data.get("enable_information_leakage", True):
        categories.append("info_leakage")

    return AuditConfig(
        model=ModelConfig(
            endpoint=model_data.get("api_url", DEFAULT_CONFIG.model.endpoint),
            model_name=model_data.get("model_name", DEFAULT_CONFIG.model.model_name),
            api_key=model_data.get("api_key", DEFAULT_CONFIG.model.api_key),
            timeout=model_data.get("request_timeout", DEFAULT_CONFIG.model.timeout),
        ),
        test=TestConfig(categories=categories),
        report=ReportConfig(output_dir=report_data.get("output_dir", "./reports")),
    )
