# LLM Security Audit Tool 🛡️

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

[English](#english) | [中文](#中文)

---

## English

### Overview

**LLM Security Audit Tool** - Automatically test the security boundaries of Large Language Models, detecting vulnerabilities including prompt injection, jailbreak attacks, and information leakage.

> **Security Notice**: This project is for educational and academic research only. Unauthorized use for production environment auditing or any illegal purposes is strictly prohibited.

### Features

- **One-Click Scanning** - Simple commands to execute complete security audits
- **78+ Built-in Test Cases** - Covering prompt injection, jailbreak, info leakage, encoding bypass, and multilingual attacks
- **Multi-Format Reports** - Support Markdown and HTML reports with visualizations
- **Concurrent Testing** - Parallel execution for improved efficiency
- **Easy to Extend** - YAML-based test case library for custom payloads
- **Wide Compatibility** - Support Ollama, vLLM, LM Studio and other OpenAI API compatible endpoints

### Quick Start

#### Installation

```bash
# Method 1: pip install (recommended)
pip install -e .

# Method 2: Install dependencies directly
pip install httpx pydantic pyyaml rich click jinja2
```

#### Basic Usage

```bash
# 1. Generate config file
llm-audit init

# 2. Edit config.yaml with your model info
# vim config.yaml

# 3. Run scan
llm-audit scan

# 4. View reports in ./reports/ directory
```

#### Common Commands

```bash
# Quick scan (high-severity only)
llm-audit scan --quick

# Specify model
llm-audit scan --model "qwen2:7b" --endpoint "http://localhost:11434/v1/chat/completions"

# Specify test categories
llm-audit scan --categories "prompt_injection,jailbreak"

# Use regex evaluator
llm-audit scan --evaluator regex

# Generate HTML report only
llm-audit scan --format html

# List all available attack payloads
llm-audit list-attacks

# Migrate v1.0 config
llm-audit migrate old_config.yaml
```

### Configuration

```yaml
model:
  provider: openai
  endpoint: "http://localhost:11434/v1/chat/completions"
  model_name: "deepseek-r1:1.5b"
  api_key: "ollama"
  timeout: 60

test:
  categories:
    - prompt_injection
    - jailbreak
    - info_leakage
    - encoding_bypass
    - multilingual
  concurrency: 3

evaluator:
  method: heuristic  # heuristic | regex

report:
  output_dir: "./reports"
  formats:
    - markdown
    - html
```

### Test Categories

| Category | Count | Description |
|----------|-------|-------------|
| prompt_injection | 15 | Prompt injection attacks |
| jailbreak | 15 | Jailbreak attacks |
| info_leakage | 15 | Information leakage tests |
| encoding_bypass | 10 | Encoding bypass attacks |
| multi_turn | 8 | Multi-turn dialog attacks |
| multilingual | 15 | Multilingual attacks |

### Custom Test Cases

Create YAML files in `attack_payloads/` directory:

```yaml
category: my_custom_attack
name: "Custom Attack"
payloads:
  - id: custom_001
    name: "Test Case 1"
    prompt: "Your test prompt"
    severity: high
    expected_behavior: refuse
    tags: [custom, test]
```

### Project Structure

```
LLM-Security-Audit-Demo/
├── pyproject.toml           # Project configuration
├── config/
│   └── default.yaml         # Default config template
├── src/
│   └── llm_audit/
│       ├── cli.py           # CLI entry point
│       ├── config.py        # Configuration management
│       ├── engine.py        # Audit engine
│       ├── client/          # LLM clients
│       ├── attacks/         # Attack modules
│       ├── evaluator/       # Evaluation engines
│       └── reporter/        # Report generators
├── attack_payloads/         # Attack test cases (YAML)
│   ├── prompt_injection.yaml
│   ├── jailbreak.yaml
│   ├── info_leakage.yaml
│   ├── encoding_bypass.yaml
│   ├── multi_turn.yaml
│   └── multilingual.yaml
└── reports/                 # Generated reports
```

### License

MIT License

---

## 中文

### 概述

**LLM 安全审计工具** - 自动化测试大语言模型的安全边界，检测提示注入、越狱攻击、信息泄露等安全漏洞。

> **安全声明**: 本项目仅供教育与学术研究使用。严禁将其用于未经授权的生产环境审计或任何非法用途。

### 特性

- **一键扫描** - 简单命令即可执行完整安全审计
- **78+ 内置用例** - 覆盖提示注入、越狱、信息泄露、编码绕过、多语言攻击
- **多格式报告** - 支持 Markdown 和 HTML 报告，HTML 含可视化图表
- **并发测试** - 支持并行执行，提升测试效率
- **易于扩展** - YAML 格式用例库，轻松添加自定义测试用例
- **兼容性强** - 支持 Ollama、vLLM、LM Studio 等 OpenAI API 兼容端点

### 快速开始

#### 安装

```bash
# 方式 1: pip 安装 (推荐)
pip install -e .

# 方式 2: 直接安装依赖
pip install httpx pydantic pyyaml rich click jinja2
```

#### 基本使用

```bash
# 1. 生成配置文件
llm-audit init

# 2. 编辑 config.yaml，配置模型信息
# vim config.yaml

# 3. 执行扫描
llm-audit scan

# 4. 查看 reports/ 目录下的报告
```

#### 常用命令

```bash
# 快速扫描 (仅高危用例)
llm-audit scan --quick

# 指定模型
llm-audit scan --model "qwen2:7b" --endpoint "http://localhost:11434/v1/chat/completions"

# 指定测试类别
llm-audit scan --categories "prompt_injection,jailbreak"

# 使用正则评估器
llm-audit scan --evaluator regex

# 只生成 HTML 报告
llm-audit scan --format html

# 列出所有可用攻击用例
llm-audit list-attacks

# 迁移 v1.0 配置
llm-audit migrate old_config.yaml
```

### 配置说明

```yaml
model:
  provider: openai          # 提供商
  endpoint: "http://localhost:11434/v1/chat/completions"
  model_name: "deepseek-r1:1.5b"
  api_key: "ollama"
  timeout: 60

test:
  categories:               # 启用的测试类别
    - prompt_injection      # 提示注入
    - jailbreak             # 越狱攻击
    - info_leakage          # 信息泄露
    - encoding_bypass       # 编码绕过
    - multilingual          # 多语言攻击
  concurrency: 3            # 并发数

evaluator:
  method: heuristic         # 评估方法: heuristic | regex

report:
  output_dir: "./reports"   # 输出目录
  formats:                  # 报告格式
    - markdown
    - html
```

### 测试类别

| 类别 | 用例数 | 说明 |
|------|--------|------|
| prompt_injection | 15 | 提示注入攻击 |
| jailbreak | 15 | 越狱攻击 |
| info_leakage | 15 | 信息泄露测试 |
| encoding_bypass | 10 | 编码绕过攻击 |
| multi_turn | 8 | 多轮对话攻击 |
| multilingual | 15 | 多语言攻击 |

### 自定义用例

在 `attack_payloads/` 目录下创建 YAML 文件：

```yaml
category: my_custom_attack
name: "自定义攻击"
payloads:
  - id: custom_001
    name: "测试用例 1"
    prompt: "你的测试提示词"
    severity: high
    expected_behavior: refuse
    tags: [custom, test]
```

### 项目结构

```
LLM-Security-Audit-Demo/
├── pyproject.toml           # 项目配置
├── config/
│   └── default.yaml         # 默认配置模板
├── src/
│   └── llm_audit/
│       ├── cli.py           # 命令行入口
│       ├── config.py        # 配置管理
│       ├── engine.py        # 审计引擎
│       ├── client/          # LLM 客户端
│       ├── attacks/         # 攻击模块
│       ├── evaluator/       # 评估引擎
│       └── reporter/        # 报告生成
├── attack_payloads/         # 攻击用例库 (YAML)
│   ├── prompt_injection.yaml
│   ├── jailbreak.yaml
│   ├── info_leakage.yaml
│   ├── encoding_bypass.yaml
│   ├── multi_turn.yaml
│   └── multilingual.yaml
└── reports/                 # 生成的报告
```

### 许可证

MIT License

---

## 免责声明 / Disclaimer

本工具仅供安全研究和教育目的。使用本工具进行测试时，请确保：
- 仅在授权的环境中使用
- 不用于非法目的
- 测试结果需人工复核
- 妥善处理可能的敏感内容

This tool is for security research and educational purposes only. When using this tool, please ensure:
- Use only in authorized environments
- Do not use for illegal purposes
- Test results require manual review
- Handle potentially sensitive content properly
