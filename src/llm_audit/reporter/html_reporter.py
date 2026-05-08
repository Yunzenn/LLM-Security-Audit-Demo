"""HTML 报告生成器"""

import datetime
from pathlib import Path

from .base import BaseReporter, ReportData


class HtmlReporter(BaseReporter):
    """生成 HTML 格式的安全审计报告"""

    TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM 安全审计报告 - {model_name}</title>
    <style>
        :root {{
            --primary: #2563eb;
            --success: #16a34a;
            --warning: #d97706;
            --danger: #dc2626;
            --critical: #7c3aed;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 2rem;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, var(--primary), #7c3aed);
            color: white;
            padding: 2rem;
            border-radius: 1rem;
            margin-bottom: 2rem;
        }}
        .header h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
        .header .meta {{ opacity: 0.9; font-size: 0.9rem; }}
        .card {{
            background: var(--card-bg);
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .card h2 {{
            font-size: 1.25rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--primary);
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}
        .stat-card {{
            background: var(--bg);
            padding: 1.25rem;
            border-radius: 0.5rem;
            text-align: center;
        }}
        .stat-card .value {{
            font-size: 2rem;
            font-weight: bold;
        }}
        .stat-card .label {{
            color: var(--text-muted);
            font-size: 0.875rem;
        }}
        .stat-card.success .value {{ color: var(--success); }}
        .stat-card.warning .value {{ color: var(--warning); }}
        .stat-card.danger .value {{ color: var(--danger); }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}
        th, td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            background: var(--bg);
            font-weight: 600;
            font-size: 0.875rem;
            color: var(--text-muted);
        }}
        .severity {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .severity.safe {{ background: #dcfce7; color: #166534; }}
        .severity.low {{ background: #dbeafe; color: #1e40af; }}
        .severity.medium {{ background: #fef3c7; color: #92400e; }}
        .severity.high {{ background: #fee2e2; color: #991b1b; }}
        .severity.critical {{ background: #ede9fe; color: #5b21b6; }}
        .progress-bar {{
            height: 8px;
            background: var(--border);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 0.5rem;
        }}
        .progress-fill {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s;
        }}
        .progress-fill.success {{ background: var(--success); }}
        .progress-fill.warning {{ background: var(--warning); }}
        .progress-fill.danger {{ background: var(--danger); }}
        .disclaimer {{
            background: #fef3c7;
            border-left: 4px solid var(--warning);
            padding: 1rem;
            border-radius: 0 0.5rem 0.5rem 0;
            margin-bottom: 1.5rem;
            font-size: 0.875rem;
        }}
        .footer {{
            text-align: center;
            color: var(--text-muted);
            font-size: 0.875rem;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
        }}
        .vuln-detail {{
            background: #fef2f2;
            border-left: 4px solid var(--danger);
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 0 0.5rem 0.5rem 0;
        }}
        .vuln-detail h4 {{ color: var(--danger); margin-bottom: 0.5rem; }}
        .vuln-detail .prompt {{
            background: #f1f5f9;
            padding: 0.5rem;
            border-radius: 0.25rem;
            font-family: monospace;
            font-size: 0.8rem;
            margin: 0.5rem 0;
            word-break: break-all;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ LLM 安全审计报告</h1>
            <div class="meta">
                <p><strong>目标模型:</strong> {model_name}</p>
                <p><strong>API 端点:</strong> {model_endpoint}</p>
                <p><strong>生成时间:</strong> {timestamp}</p>
            </div>
        </div>

        <div class="disclaimer">
            <strong>⚠️ 安全声明:</strong> 本报告由自动化工具生成，所有结果必须由安全专家人工复核。
            测试用例仅用于安全研究，请勿用于非法目的。
        </div>

        <div class="card">
            <h2>📊 测试概览</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="value">{total_tests}</div>
                    <div class="label">总测试用例</div>
                </div>
                <div class="stat-card success">
                    <div class="value">{safe_count}</div>
                    <div class="label">安全通过</div>
                </div>
                <div class="stat-card warning">
                    <div class="value">{vuln_count}</div>
                    <div class="label">潜在漏洞</div>
                </div>
                <div class="stat-card danger">
                    <div class="value">{error_count}</div>
                    <div class="label">请求错误</div>
                </div>
            </div>
            <div>
                <strong>漏洞率:</strong> {vuln_rate}%
                <div class="progress-bar">
                    <div class="progress-fill {risk_color}" style="width: {vuln_rate}%"></div>
                </div>
            </div>
            <p style="margin-top: 1rem;"><strong>风险等级:</strong> <span class="severity {risk_class}">{risk_level}</span></p>
        </div>

        <div class="card">
            <h2>📈 分类统计</h2>
            <table>
                <thead>
                    <tr>
                        <th>类别</th>
                        <th>总数</th>
                        <th>漏洞</th>
                        <th>安全</th>
                        <th>错误</th>
                        <th>通过率</th>
                    </tr>
                </thead>
                <tbody>
                    {category_rows}
                </tbody>
            </table>
        </div>

        <div class="card">
            <h2>📋 详细测试结果</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>类别</th>
                        <th>测试名称</th>
                        <th>风险等级</th>
                        <th>置信度</th>
                        <th>标记</th>
                    </tr>
                </thead>
                <tbody>
                    {result_rows}
                </tbody>
            </table>
        </div>

        {vuln_details}

        <div class="footer">
            <p>Generated by LLM Security Audit Tool v2.0</p>
            <p>{generation_time}</p>
        </div>
    </div>
</body>
</html>"""

    def generate(self, data: ReportData, output_path: Path) -> Path:
        """生成 HTML 报告"""
        report_path = output_path / f"Security_Report_{data.timestamp_str}.html"
        content = self._render(data)
        report_path.write_text(content, encoding="utf-8")
        return report_path

    def _render(self, data: ReportData) -> str:
        """渲染 HTML 报告"""
        category_stats = data.get_category_stats()

        # 分类统计行
        category_rows = []
        for cat, stats in category_stats.items():
            pass_rate = (stats["safe"] / stats["total"] * 100) if stats["total"] > 0 else 0
            category_rows.append(
                f"<tr><td>{cat}</td><td>{stats['total']}</td><td>{stats['vuln']}</td>"
                f"<td>{stats['safe']}</td><td>{stats['error']}</td><td>{pass_rate:.1f}%</td></tr>"
            )

        # 详细结果行
        result_rows = []
        for r in data.results:
            if r.payload:
                sev = r.evaluation.get("severity", "unknown")
                confidence = r.evaluation.get("confidence", 0)
                flags = ", ".join(r.evaluation.get("flags", [])[:2])
                result_rows.append(
                    f"<tr>"
                    f"<td>{r.test_id}</td>"
                    f"<td>{r.payload.category}</td>"
                    f"<td>{r.payload.name}</td>"
                    f"<td><span class='severity {sev}'>{sev}</span></td>"
                    f"<td>{confidence:.0%}</td>"
                    f"<td>{flags}</td>"
                    f"</tr>"
                )

        # 漏洞详情
        vuln_details = ""
        vuln_results = [r for r in data.results if r.evaluation.get("is_vulnerable")]
        if vuln_results:
            detail_cards = []
            for r in vuln_results:
                if r.payload:
                    detail_cards.append(
                        f"<div class='vuln-detail'>"
                        f"<h4>{r.payload.name}</h4>"
                        f"<p><strong>类别:</strong> {r.payload.category} | "
                        f"<strong>严重性:</strong> <span class='severity {r.evaluation.get('severity', 'unknown')}'>"
                        f"{r.evaluation.get('severity', 'unknown')}</span></p>"
                        f"<div class='prompt'>{r.payload.prompt[:200]}</div>"
                        f"<p><strong>评估:</strong> {r.evaluation.get('reason', 'N/A')}</p>"
                        f"</div>"
                    )
            vuln_details = f"<div class='card'><h2>🔍 漏洞详情</h2>{''.join(detail_cards)}</div>"

        risk_class = data.risk_level if data.risk_level in ("safe", "low", "medium", "high") else "medium"
        risk_color = {"low": "success", "medium": "warning", "high": "danger"}.get(data.risk_level, "warning")

        return self.TEMPLATE.format(
            model_name=data.model_name,
            model_endpoint=data.model_endpoint,
            timestamp=data.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            total_tests=data.total_tests,
            safe_count=data.safe_count,
            vuln_count=data.vuln_count,
            error_count=data.error_count,
            vuln_rate=f"{data.vuln_rate:.1f}",
            risk_level=data.risk_level.upper(),
            risk_class=risk_class,
            risk_color=risk_color,
            category_rows="\n".join(category_rows),
            result_rows="\n".join(result_rows),
            vuln_details=vuln_details,
            generation_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

    def get_file_extension(self) -> str:
        return ".html"
