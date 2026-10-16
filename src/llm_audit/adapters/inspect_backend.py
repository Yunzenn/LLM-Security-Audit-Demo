"""Inspect AI pilot with the same deterministic output contract as the CLI."""

from inspect_ai import Task
from inspect_ai.dataset import Sample
from inspect_ai.model import ChatMessageSystem, ChatMessageUser, GenerateConfig
from inspect_ai.scorer import Score, mean, scorer
from inspect_ai.solver import solver

from ..attacks.base import AttackPayload
from ..evaluator.contracts import score_output


@solver
def conversation():
    async def solve(state, generate):
        await generate(state)
        for turn in state.metadata["remaining_turns"]:
            state.messages.append(ChatMessageUser(content=turn))
            await generate(state)
        return state

    return solve


@scorer(metrics={"objective_pass": [mean()], "objective_fail": [mean()], "unknown": [mean()]})
def output_contract():
    async def score(state, target):
        replies = [message.text for message in state.messages if message.role == "assistant"]
        result = score_output(replies, state.metadata["forbidden_output"])
        return Score(
            value={
                "objective_pass": int(result.status == "pass"),
                "objective_fail": int(result.status == "fail"),
                "unknown": int(result.status == "unknown"),
            },
            explanation=result.reason,
            metadata=result.to_dict(),
        )

    return score


def build_task(payloads: list[AttackPayload]) -> Task:
    samples = []
    for payload in payloads:
        turns = payload.turns or [payload.prompt]
        messages = [ChatMessageUser(content=turns[0])]
        if payload.system_prompt:
            messages.insert(0, ChatMessageSystem(content=payload.system_prompt))
        samples.append(
            Sample(
                id=payload.id,
                input=messages,
                metadata={
                    "remaining_turns": turns[1:],
                    "forbidden_output": payload.forbidden_output,
                    "category": payload.category,
                },
            )
        )
    return Task(
        name="llm_audit_contract_pilot",
        dataset=samples,
        solver=conversation(),
        scorer=output_contract(),
        config=GenerateConfig(max_tokens=256, temperature=0, max_connections=2),
        message_limit=32,
        time_limit=60,
        metadata={"scope": "exact output only"},
    )
