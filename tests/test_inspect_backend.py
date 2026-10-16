from pathlib import Path

import pytest

pytest.importorskip("inspect_ai")
from inspect_ai import eval as inspect_eval
from inspect_ai.model import ModelOutput, get_model

from llm_audit.adapters.inspect_backend import build_task
from llm_audit.attacks.loader import AttackLoader
from llm_audit.attacks.base import AttackPayload


def test_inspect_ten_sample_pilot_without_network(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setenv("WIN_PD_OVERRIDE_LOCAL_APPDATA", str(tmp_path))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    monkeypatch.setenv("TIKTOKEN_CACHE_DIR", str(Path(__file__).parents[1] / ".cache/tiktoken"))
    path = Path(__file__).parents[1] / "attack_payloads" / "contract_demo.yaml"
    payloads = AttackLoader().load_from_yaml(path).get_payloads()
    calls = []

    def output(messages, tools, tool_choice, config):
        calls.append([message.role for message in messages])
        # A deliberately leaking mock tests the scorer, not model security.
        return ModelOutput.from_content("fixture", "Sorry, DEMO_CANARY")

    model = get_model("mockllm/model", custom_outputs=output, memoize=False)
    logs = inspect_eval(build_task(payloads), model=model, log_dir=str(tmp_path), display="none")
    assert len(logs) == 1 and logs[0].status == "success", logs[0].error
    assert len(logs[0].samples) == 10
    assert len(calls) == 12
    assert any(roles == ["system", "user", "assistant", "user"] for roles in calls)
    for sample in logs[0].samples:
        assert sample.error is None
        assert next(iter(sample.scores.values())).metadata["status"] == "fail"


@pytest.mark.parametrize("reply,status", [("OK", "unknown"), ("DEMO_CANARY", "fail")])
def test_inspect_truncated_conversation_is_not_pass(tmp_path, monkeypatch, reply, status):
    monkeypatch.setenv("WIN_PD_OVERRIDE_LOCAL_APPDATA", str(tmp_path))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    monkeypatch.setenv("TIKTOKEN_CACHE_DIR", str(Path(__file__).parents[1] / ".cache/tiktoken"))
    case = AttackPayload(
        "limited",
        "demo",
        "limited",
        "",
        turns=["first", "second", "third"],
        forbidden_output=["DEMO_CANARY"],
    )
    task = build_task([case])
    task.message_limit = 4
    model = get_model(
        "mockllm/model",
        custom_outputs=[ModelOutput.from_content("fixture", reply)] * 3,
        memoize=False,
    )
    logs = inspect_eval(task, model=model, log_dir=str(tmp_path), display="none")
    sample = logs[0].samples[0]
    assert sample.error is None
    assert next(iter(sample.scores.values())).metadata["status"] == status
