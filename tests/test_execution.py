import asyncio
import copy

import httpx
import pytest

from llm_audit.attacks.base import AttackPayload, TestResult as AuditResult
from llm_audit.attacks.loader import AttackLoader, YamlAttack
from llm_audit.client.base import BaseLLMClient, LLMResponse
from llm_audit.client.openai_client import OpenAIClient
from llm_audit.config import AuditConfig, TestConfig as RunConfig, load_config
from llm_audit.engine import AuditEngine
from llm_audit.evaluator.contracts import score_output
from llm_audit.evaluator.heuristic import HeuristicEvaluator
from llm_audit.reporter.base import ReportData
from llm_audit.reporter.html_reporter import HtmlReporter
from llm_audit.reporter.markdown_reporter import MarkdownReporter


def payload(name="case", **kwargs):
    return AttackPayload(name, "demo", name, "hello", **kwargs)


@pytest.mark.parametrize(
    "reply,status",
    [
        ("Sorry, the secret is DEMO_CANARY.", "fail"),
        ("抱歉，秘密是 DEMO_CANARY。", "fail"),
        ("An ordinary long explanation. " * 20, "pass"),
        ("I cannot reveal it.", "pass"),
        ("", "unknown"),
    ],
)
def test_exact_contract(reply, status):
    assert score_output([reply], ["DEMO_CANARY"]).status == status


def test_no_contract_is_not_safe():
    assert score_output(["Hello"], []).status == "unknown"
    result = HeuristicEvaluator().evaluate("demo", "Sorry. import os")
    assert result.is_vulnerable  # Advisory evidence survives a refusal prefix.
    assert result.status == "unknown"


def test_observed_leak_survives_later_empty_output():
    assert score_output(["DEMO_CANARY", ""], ["DEMO_CANARY"]).status == "fail"
    assert score_output(["OK", ""], ["DEMO_CANARY"]).status == "unknown"
    with pytest.raises(ValueError):
        score_output(["OK"], [""])


def test_cli_initialization_failure_exits_nonzero(monkeypatch):
    from click.testing import CliRunner
    from llm_audit.cli import main

    async def unavailable(self):
        return False

    async def close(self):
        pass

    monkeypatch.setattr(AuditEngine, "initialize", unavailable)
    monkeypatch.setattr(AuditEngine, "close", close)
    result = CliRunner().invoke(main, ["scan"])
    assert result.exit_code != 0
    assert "initialization failed" in result.output


class ChatClient(BaseLLMClient):
    def __init__(self):
        self.calls = []

    async def query(self, prompt, system_prompt=None):
        return LLMResponse(True, "OK")

    async def chat(self, messages):
        self.calls.append(copy.deepcopy(messages))
        return LLMResponse(True, "DEMO_CANARY" if len(messages) > 2 else "OK")

    async def health_check(self):
        return True

    async def close(self):
        pass


async def test_multi_turn_isolated_and_scored_across_turns():
    engine = AuditEngine(AuditConfig(test=RunConfig(retry_count=0)))
    engine.client = ChatClient()
    engine.evaluator = HeuristicEvaluator()
    case = payload(turns=["hello", "continue"], forbidden_output=["DEMO_CANARY"])
    result = await engine._test_single(case)
    assert result.evaluation["status"] == "fail"
    assert [m["role"] for m in engine.client.calls[1]] == ["user", "assistant", "user"]
    assert len(result.messages) == 4
    await engine._test_single(case)
    assert len(engine.client.calls[2]) == 1


async def test_real_concurrency_bound_and_stable_order(monkeypatch):
    cases = [payload(str(index)) for index in range(5)]
    monkeypatch.setattr(AttackLoader, "load_all", lambda *args: [YamlAttack("demo", "demo", cases)])
    engine = AuditEngine(AuditConfig(test=RunConfig(concurrency=2, sleep_interval=0)))
    entered = 0
    active = 0
    peak = 0
    rendezvous = asyncio.Event()

    async def run(case):
        nonlocal entered, active, peak
        entered += 1
        active += 1
        peak = max(peak, active)
        if entered >= 2:
            rendezvous.set()
        await asyncio.wait_for(rendezvous.wait(), timeout=1)
        active -= 1
        return AuditResult(payload=case)

    monkeypatch.setattr(engine, "_test_single", run)
    results = await engine.run()
    assert peak == 2
    assert [result.payload.id for result in results] == [case.id for case in cases]


async def test_transport_error_is_not_low_risk():
    engine = AuditEngine(AuditConfig(test=RunConfig(retry_count=0)))
    client = OpenAIClient(engine.config.model)
    await client._client.aclose()
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(lambda request: httpx.Response(503))
    )
    engine.client = client
    engine.evaluator = HeuristicEvaluator()
    try:
        result = await engine._test_single(payload())
    finally:
        await client.close()
    data = ReportData("mock", "local", [result])
    assert data.error_count == 1 and data.safe_count == 0
    assert data.risk_level == "unknown" and data.coverage == 0


async def test_openai_wire_history_and_null_content():
    client = OpenAIClient(AuditConfig().model)
    await client._client.aclose()
    captured = []

    def handle(request):
        import json

        captured.append(json.loads(request.content))
        return httpx.Response(200, json={"choices": [{"message": {"content": None}}]})

    client._client = httpx.AsyncClient(transport=httpx.MockTransport(handle))
    messages = [
        {"role": "user", "content": "one"},
        {"role": "assistant", "content": "reply"},
        {"role": "user", "content": "two"},
    ]
    try:
        response = await client.chat(messages)
    finally:
        await client.close()
    assert captured[0]["messages"] == messages
    assert not response.success


@pytest.mark.parametrize(
    "language,title", [("en", "LLM security evaluation"), ("zh", "LLM 安全评测")]
)
def test_reports_unknown_and_escape(tmp_path, language, title):
    result = AuditResult(
        payload=payload("<script>alert(1)</script>"), evaluation={"status": "unknown"}
    )
    data = ReportData("mock", "local", [result], {"report": {"language": language}})
    md = MarkdownReporter().generate(data, tmp_path).read_text(encoding="utf-8")
    html = HtmlReporter().generate(data, tmp_path).read_text(encoding="utf-8")
    assert title in md and title in html
    assert "<script>" not in html
    assert data.safe_count == 0 and data.unknown_count == 1
    assert data.get_category_stats()["demo"]["unknown"] == 1


def test_scorable_denominator_and_legacy_unknown():
    results = [
        AuditResult(evaluation={"status": value}) for value in ["pass", "fail", "unknown", "error"]
    ]
    results.append(AuditResult(evaluation={"is_vulnerable": False}))
    data = ReportData("mock", "local", results)
    assert data.vuln_rate == 50 and data.coverage == 40
    assert data.safe_count == 1 and data.unknown_count == 2


def test_config_validation_and_fresh_defaults():
    with pytest.raises(ValueError):
        RunConfig(concurrency=0)
    with pytest.raises(ValueError):
        RunConfig(retry_count=-1)
    first = load_config("does-not-exist.yaml")
    first.model.model_name = "changed"
    assert load_config("does-not-exist.yaml").model.model_name != "changed"


def test_invalid_config_does_not_silently_change_target(tmp_path):
    path = tmp_path / "invalid.yaml"
    path.write_text("test:\n  concurrency: 0\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid configuration"):
        load_config(str(path))


async def test_retry_restarts_entire_conversation(monkeypatch):
    class RetryClient(ChatClient):
        async def chat(self, messages):
            self.calls.append(copy.deepcopy(messages))
            if len(self.calls) == 2:
                return LLMResponse(False, error="temporary transport error")
            return LLMResponse(True, "OK")

    async def no_delay(seconds):
        pass

    monkeypatch.setattr(asyncio, "sleep", no_delay)
    engine = AuditEngine(AuditConfig(test=RunConfig(retry_count=1)))
    engine.client = RetryClient()
    engine.evaluator = HeuristicEvaluator()
    result = await engine._test_single(
        payload(turns=["first", "second"], forbidden_output=["DEMO_CANARY"])
    )
    assert result.attempts == 2 and result.evaluation["status"] == "pass"
    assert [len(messages) for messages in engine.client.calls] == [1, 3, 1, 3]


async def test_leak_from_failed_attempt_cannot_become_pass(monkeypatch):
    class RetryLeakClient(ChatClient):
        async def chat(self, messages):
            self.calls.append(copy.deepcopy(messages))
            if len(self.calls) == 1:
                return LLMResponse(True, "DEMO_CANARY")
            if len(self.calls) == 2:
                return LLMResponse(False, error="temporary transport error")
            return LLMResponse(True, "OK")

    async def no_delay(seconds):
        pass

    monkeypatch.setattr(asyncio, "sleep", no_delay)
    engine = AuditEngine(AuditConfig(test=RunConfig(retry_count=1)))
    engine.client = RetryLeakClient()
    engine.evaluator = HeuristicEvaluator()
    result = await engine._test_single(
        payload(turns=["first", "second"], forbidden_output=["DEMO_CANARY"])
    )
    assert result.evaluation["status"] == "fail"
    assert result.attempt_records[0]["messages"][1]["content"] == "DEMO_CANARY"
    assert result.attempt_records[0]["error"] == "temporary transport error"
    assert len(result.to_dict()["attempt_records"]) == 2


def test_loader_turns_and_invalid_canary(tmp_path):
    path = tmp_path / "case.yaml"
    path.write_text(
        "payloads:\n  - id: m\n    turns: [hello, continue]\n    forbidden_output: [CANARY]\n",
        encoding="utf-8",
    )
    assert AttackLoader().load_from_yaml(path).get_payloads()[0].turns == ["hello", "continue"]
    path.write_text('payloads:\n  - prompt: hello\n    forbidden_output: [""]\n', encoding="utf-8")
    with pytest.raises(ValueError):
        AttackLoader().load_from_yaml(path)
