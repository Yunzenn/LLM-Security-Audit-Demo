from pathlib import Path

import pytest

pytest.importorskip("inspect_ai")
from inspect_ai import eval as inspect_eval
from inspect_ai.model import ModelOutput, get_model

from llm_audit.adapters.inspect_backend import build_task
from llm_audit.attacks.loader import AttackLoader


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
