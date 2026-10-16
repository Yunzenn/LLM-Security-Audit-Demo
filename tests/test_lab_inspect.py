from pathlib import Path

import pytest

pytest.importorskip("inspect_ai")
from inspect_ai import eval as inspect_eval
from llm_audit.adapters.lab_backend import build_lab_task, scripted_lab_model
from llm_audit.lab.environment import load_cases
from llm_audit.lab.report import summarize


def test_paired_matrix_executes_tools_and_enforces_policy(tmp_path, monkeypatch):
    monkeypatch.setenv("WIN_PD_OVERRIDE_LOCAL_APPDATA", str(tmp_path))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    monkeypatch.setenv("TIKTOKEN_CACHE_DIR", str(Path(__file__).parents[1] / ".cache/tiktoken"))
    cases, _ = load_cases()
    logs = inspect_eval(
        build_lab_task(cases),
        model=scripted_lab_model(),
        log_dir=str(tmp_path),
        display="none",
        max_samples=1,
    )
    assert len(logs) == 1 and logs[0].status == "success", logs[0].error
    samples = logs[0].samples
    assert len(samples) == 120
    assert all(sample.error is None for sample in samples)
    rows = [next(iter(sample.scores.values())).metadata for sample in samples]
    groups = summarize(rows)
    assert len(groups) == 6
    for group in groups:
        assert group["utility_successes"] == 20
        assert group["errors"] == 0 and group["scorable"] == 20
        if group["variant"] == "attack":
            assert group["unauthorized_attempted"] == 20
            assert group["unauthorized_executed"] == (0 if group["defense"] == "enforced" else 20)
            assert group["objective_failures"] == (0 if group["defense"] == "enforced" else 20)
        else:
            assert group["objective_failures"] == 0 and group["blocked_cases"] == 0
    assert all(row["events"] for row in rows)


def test_cli_missing_samples_preserve_planned_denominators(tmp_path, monkeypatch):
    import json
    from types import SimpleNamespace
    import inspect_ai
    from click.testing import CliRunner
    from llm_audit.cli import main

    monkeypatch.setattr(
        inspect_ai,
        "eval",
        lambda *args, **kwargs: [SimpleNamespace(status="success", error=None, samples=[])],
    )
    destination = tmp_path / "missing"
    result = CliRunner().invoke(
        main, ["lab-eval", "--defense", "baseline", "--limit", "1", "--output", str(destination)]
    )
    assert result.exit_code != 0
    report = json.loads((destination / "lab_results.json").read_text(encoding="utf-8"))
    assert report["manifest"]["expected_cases"] == 2
    assert len(report["cases"]) == 2
    assert all(group["errors"] == group["total"] == 1 for group in report["groups"])
    again = CliRunner().invoke(main, ["lab-eval", "--output", str(destination)])
    assert again.exit_code != 0 and "must be empty" in again.output


def test_other_mock_provider_is_not_labeled_real(tmp_path, monkeypatch):
    import json
    from types import SimpleNamespace
    import inspect_ai
    from click.testing import CliRunner
    from llm_audit.cli import main

    monkeypatch.setattr(
        inspect_ai,
        "eval",
        lambda *args, **kwargs: [SimpleNamespace(status="success", error=None, samples=[])],
    )
    CliRunner().invoke(
        main, ["lab-eval", "--model", "mockllm/model", "--limit", "1", "--output", str(tmp_path)]
    )
    report = json.loads((tmp_path / "lab_results.json").read_text(encoding="utf-8"))
    assert report["manifest"]["execution"] == "provider_mock"


def test_native_error_retains_known_goal_and_usage(tmp_path, monkeypatch):
    import json
    from types import SimpleNamespace
    import inspect_ai
    from click.testing import CliRunner
    from llm_audit.cli import main
    from llm_audit.lab.environment import LabWorld

    cases, _ = load_cases()
    task = cases[0]  # private-read goal
    world = LabWorld(task, "attack", "baseline")
    world.call("read_note", note_id="private")
    evidence = world.score([], False)
    evidence["model_calls"] = 2
    sample = SimpleNamespace(
        error="transport",
        scores=None,
        total_time=2.5,
        metadata={
            "case": {"id": task.id},
            "variant": "attack",
            "defense": "baseline",
            "lab_evidence": evidence,
        },
        model_usage={"fixture": SimpleNamespace(input_tokens=10, output_tokens=5)},
    )
    monkeypatch.setattr(
        inspect_ai,
        "eval",
        lambda *args, **kwargs: [
            SimpleNamespace(status="error", error="transport", samples=[sample])
        ],
    )
    result = CliRunner().invoke(
        main, ["lab-eval", "--limit", "1", "--defense", "baseline", "--output", str(tmp_path)]
    )
    assert result.exit_code != 0
    report = json.loads((tmp_path / "lab_results.json").read_text(encoding="utf-8"))
    group = next(group for group in report["groups"] if group["variant"] == "attack")
    assert group["model_calls"] == 2 and group["input_tokens"] == 10
    assert group["elapsed_seconds"] == 2.5
    assert group["errors"] == 1 and group["objective_failures"] == group["scorable"] == 1
    assert group["unauthorized_executed"] == 1


def test_inspect_preserves_partial_evidence_after_provider_failure(tmp_path, monkeypatch):
    from inspect_ai.dataset import MemoryDataset
    from inspect_ai.model import ModelOutput, get_model

    monkeypatch.setenv("WIN_PD_OVERRIDE_LOCAL_APPDATA", str(tmp_path))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    monkeypatch.setenv("TIKTOKEN_CACHE_DIR", str(Path(__file__).parents[1] / ".cache/tiktoken"))
    cases, _ = load_cases()
    task = build_lab_task([cases[0]], ("baseline",))
    task.dataset = MemoryDataset(
        [sample for sample in task.dataset if sample.metadata["variant"] == "attack"]
    )
    calls = []

    def output(messages, tools, tool_choice, config):
        calls.append(1)
        if len(calls) == 1:
            return ModelOutput.for_tool_call("fixture", "read_note", {"note_id": "private"})
        raise RuntimeError("synthetic provider failure")

    logs = inspect_eval(
        task,
        model=get_model("mockllm/failure", custom_outputs=output, memoize=False),
        log_dir=str(tmp_path),
        display="none",
    )
    sample = logs[0].samples[0]
    assert sample.error is not None
    evidence = sample.metadata["lab_evidence"]
    assert evidence["objective_status"] == "fail" and evidence["unauthorized_executed"]
    assert evidence["model_calls"] == 1
