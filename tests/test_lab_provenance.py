import pytest

from llm_audit.lab.environment import load_cases
from llm_audit.lab.provenance import select_cases, source_fingerprint


def test_source_hash_is_portable_and_changes_with_code(tmp_path):
    source = tmp_path / "module.py"
    source.write_bytes(b"value = 1\r\n")
    first = source_fingerprint(tmp_path)
    source.write_bytes(b"value = 1\n")
    assert source_fingerprint(tmp_path) == first
    source.write_bytes(b"value = 2\n")
    assert source_fingerprint(tmp_path) != first


def test_balanced_explicit_pairs_keep_order_and_partition():
    cases, _ = load_cases()
    selected = select_cases(cases, "dev", "lab_11,lab_01", 2)
    assert [case.language for case in selected] == ["en", "zh"]
    assert [case.id for case in selected] == ["lab_11", "lab_01"]


@pytest.mark.parametrize(
    "ids,limit",
    [("lab_01,lab_01", 2), ("lab_07", 2), ("lab_99", 2), ("lab_01,", 2), ("lab_01,lab_11", 1)],
)
def test_invalid_subsets_fail_before_inference(ids, limit):
    cases, _ = load_cases()
    with pytest.raises(ValueError):
        select_cases(cases, "dev", ids, limit)


@pytest.mark.parametrize(
    "options",
    ["[]", '{"enable_thinking":"false"}', '{"api_key":"not-allowed"}', '{"torch_dtype":{}}'],
)
def test_invalid_hf_options_are_rejected_without_loading_model(options):
    from click.testing import CliRunner
    from llm_audit.cli import main

    result = CliRunner().invoke(
        main, ["lab-eval", "--model", "hf/fixture", "--hf-options", options]
    )
    assert result.exit_code == 2 and "--hf-options" in result.output


@pytest.mark.parametrize(
    "provider,reason,tokens,expected",
    [
        ("hf", "unknown", 40, True),
        ("hf", "unknown", 512, False),
        ("hf", "unknown", 513, False),
        ("hf", "unknown", 0, False),
        ("openai-api", "unknown", 40, False),
        ("hf", "max_tokens", 40, False),
        ("openai-api", "stop", 40, True),
        ("hf", "unknown", None, False),
    ],
)
def test_unknown_finish_reason_needs_bounded_native_hf_evidence(provider, reason, tokens, expected):
    from types import SimpleNamespace
    from llm_audit.lab.completion import completion_evidence

    output = SimpleNamespace(
        message=SimpleNamespace(text="done", tool_calls=None),
        stop_reason=reason,
        usage=SimpleNamespace(output_tokens=tokens) if tokens is not None else None,
    )
    assert completion_evidence(output, provider, 512)[0] == expected
    output.message.tool_calls = ["pending"]
    assert not completion_evidence(output, provider, 512)[0]
