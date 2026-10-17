"""Conservative completion evidence for the fixed, single-sample tool loop."""


def completion_evidence(output, provider: str | None, max_tokens: int) -> tuple[bool, str]:
    if not output.message.text.strip() or output.message.tool_calls:
        return False, "empty_or_pending_tools"
    if output.stop_reason == "stop":
        return True, "provider_stop"
    # Inspect 0.3.281's native HF provider omits finish_reason. With the
    # single-item batch used here, a normal return strictly below the generated
    # token cap establishes early termination. A capped/missing usage value
    # cannot establish completion. This inference is explicit in every trace.
    if (
        provider == "hf"
        and output.stop_reason == "unknown"
        and output.usage is not None
        and 0 < output.usage.output_tokens < max_tokens
    ):
        return True, "native_hf_early_stop_inferred"
    return False, "incomplete_or_unverified"
