from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate

from app.courtroom.graph.state import CourtroomState
from app.courtroom.models.llm import JUDICIARY_MODEL
from app.courtroom.prompts.judiciary_prompt import (
    JUDICIARY_TYPE_PROMPT,
    MEMORY_SUMMARY_PROMPT,
    REASON_VERDICT_PROMPT,
    CONFIDENCE_PROMPT,
    LATEST_OVERALL_ROUND_SUMMARY_PROMPT,
)


class JudiciaryTypeOutput(BaseModel):
    type: str


class MemorySummaryOutput(BaseModel):
    memory_summary: str


class ReasonVerdictOutput(BaseModel):
    reasoning: str
    verdict: str


class ConfidenceOutput(BaseModel):
    confidence: float


class LatestOverallRoundSummaryOutput(BaseModel):
    latest_overall_round_summary: str


def build_chain(prompt: str, output_schema: type[BaseModel]):
    return (
        ChatPromptTemplate.from_messages([("system", prompt)])
        | JUDICIARY_MODEL.with_structured_output(output_schema)
    )


type_chain = build_chain(JUDICIARY_TYPE_PROMPT, JudiciaryTypeOutput)
memory_summary_chain = build_chain(MEMORY_SUMMARY_PROMPT, MemorySummaryOutput)
reason_verdict_chain = build_chain(REASON_VERDICT_PROMPT, ReasonVerdictOutput)
confidence_chain = build_chain(CONFIDENCE_PROMPT, ConfidenceOutput)
latest_round_summary_chain = build_chain(
    LATEST_OVERALL_ROUND_SUMMARY_PROMPT,
    LatestOverallRoundSummaryOutput,
)


def get_public_statements(state: CourtroomState):
    return [
        {
            "perspective_id": perspective["id"],
            "role": perspective["role"],
            "public_statement": perspective.get("public_statement", ""),
        }
        for perspective in state.get("perspectives", [])
        if perspective.get("active") is True
    ]


def judiciary_node(state: CourtroomState):
    turn_count = state.get("turn_count", 1)
    public_statements = get_public_statements(state)

    if turn_count == 1:
        type_result = type_chain.invoke({
            "user_input": state["user_input"],
            "judiciary_corrupt": state["judiciary_corrupt"],
        })

        judiciary_type = type_result.type
        memory_summary_text = "No judiciary memory yet."

    if turn_count > 1:
        judiciary = state.get("judiciary", {})
        judiciary_type = judiciary.get("type", "")

        memory_summary_result = memory_summary_chain.invoke({
            "type": judiciary_type,
            "existing_memory_summary": judiciary.get("memory_summary", ""),
            "previous_reasoning": judiciary.get("reasoning", ""),
            "previous_verdict": judiciary.get("verdict", ""),
            "previous_confidence": judiciary.get("confidence", 0.0),
            "latest_overall_round_summary": state.get(
                "latest_overall_round_summary",
                "",
            ),
        })

        memory_summary_text = memory_summary_result.memory_summary

    if turn_count < 1:
        return {}

    reason_verdict_result = reason_verdict_chain.invoke({
        "judiciary_type": judiciary_type,
        "memory_summary": memory_summary_text,
        "latest_overall_round_summary": state.get(
            "latest_overall_round_summary",
            "No previous courtroom round summary yet.",
        ),
        "public_statements": public_statements,
        "user_input": state["user_input"],
        "judiciary_corrupt": state["judiciary_corrupt"],
    })

    confidence_result = confidence_chain.invoke({
        "judiciary_type": judiciary_type,
        "memory_summary": memory_summary_text,
        "latest_overall_round_summary": state.get(
            "latest_overall_round_summary",
            "No previous courtroom round summary yet.",
        ),
        "reasoning": reason_verdict_result.reasoning,
        "verdict": reason_verdict_result.verdict,
    })

    latest_round_summary_result = latest_round_summary_chain.invoke({
        "public_statements": public_statements,
        "judiciary_reasoning": reason_verdict_result.reasoning,
        "judiciary_verdict": reason_verdict_result.verdict,
        "judiciary_confidence": confidence_result.confidence,
    })

    judiciary_state = {
        "type": judiciary_type,
        "memory_summary": memory_summary_text,
        "reasoning": reason_verdict_result.reasoning,
        "verdict": reason_verdict_result.verdict,
        "confidence": confidence_result.confidence,
    }

    return {
        "judiciary": judiciary_state,
        "latest_overall_round_summary": latest_round_summary_result.latest_overall_round_summary,
    }
