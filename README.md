# LLM Security Audit Demo 🛡️

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

一个面向教育研究与实验室环境的 **LLM 安全性自动化测试工具**。本项目旨在帮助研究人员和学生通过模拟典型的攻击向量（提示注入、越狱、信息泄露），评估本地部署的轻量级大语言模型（如 DeepSeek、Llama 等）的安全边界。

> [!WARNING]
> **重要安全声明**：本项目仅供教育与学术研究使用。严禁将其用于未经授权的生产环境审计或任何非法用途。

---

## 1. 核心功能

- **自动化攻击模拟**：内置三大类、15+ 种典型安全测试用例。
- **启发式风险评估**：基于响应模式自动识别潜在漏洞并划分风险等级（High/Medium/Low）。
- **结构化审计报告**：自动生成 Markdown 格式的专业安全报告，包含测试详情与加固建议。
- **本地 LLM 适配**：完美兼容 Ollama, vLLM, LM Studio 等 OpenAI API 格式端点。

---

## 2. 项目架构


- `llm_security_audit_demo.py`: 核心逻辑模块，包含测试调度引擎与评估算法。
- `config.yaml`: 集中管理 API 端点、模型参数及测试开关。
- `reports/`: 存储生成的 JSON 原始数据与 Markdown 审计报告。

---

## 3. 快速开始

### 环境依赖
```bash
pip install -r requirements.txt
