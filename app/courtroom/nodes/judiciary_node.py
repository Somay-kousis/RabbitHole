from app.courtroom.models.llm import JUDICIARY_MODEL
from app.courtroom.graph.state import JudiciaryState, CourtroomState
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from app.courtroom.prompts.judiciary_prompt import (
    JUDICIARY_TYPE_PROMPT,
    MEMORY_SUMMARY_PROMPT,
    REASON_VERDICT_PROMPT,
    CONFIDENCE_PROMPT,
    LATEST_OVERALL_ROUND_SUMMARY_PROMPT,
)


class type(BaseModel):
    type: str


class memory_summary(BaseModel):
    memory_summary: str


class reason_verdict(BaseModel):
    reasoning: str
    verdict: str


class confidence(BaseModel):
    confidence: float


class latest_overall_round_summary(BaseModel):
    latest_overall_round_summary: str


def build_chain(prompt: str, output_schema: type[BaseModel]):
    return (
        ChatPromptTemplate.from_messages([("system", prompt)])
        | JUDICIARY_MODEL.with_structured_output(output_schema)
    )


type_chain = build_chain(JUDICIARY_TYPE_PROMPT, type)
memory_summary_chain = build_chain(MEMORY_SUMMARY_PROMPT, memory_summary)
reason_verdict_chain = build_chain(REASON_VERDICT_PROMPT, reason_verdict)
confidence_chain = build_chain(CONFIDENCE_PROMPT, confidence)
latest_round_summary_chain = build_chain(
    LATEST_OVERALL_ROUND_SUMMARY_PROMPT,
    latest_overall_round_summary,
)


def judiciary_node(state: CourtroomState):
    turn_count = state.get("turn_count", 1)

    public_statements = [
        {
            "perspective_id": perspective["id"],
            "role": perspective["role"],
            "public_statement": perspective.get("public_statement", ""),
        }
        for perspective in state.get("perspectives", [])
        if perspective.get("active") is True
    ]

    judiciary_type = state.get("type", "")
    memory_summary_text = state.get("memory_summary", "")

    if turn_count == 1:
        type_result = type_chain.invoke({
            "user_input": state["user_input"],
            "judiciary_corrupt": state["judiciary_corrupt"],
        })

        judiciary_type = type_result.type

    if turn_count > 1:
        memory_summary_result = memory_summary_chain.invoke({
            "type": judiciary_type,
            "existing_memory_summary": memory_summary_text,
            "previous_reasoning": state.get("reasoning", ""),
            "previous_verdict": state.get("verdict", ""),
            "previous_confidence": state.get("confidence", 0.0),
            "latest_overall_round_summary": state.get(
                "latest_overall_round_summary",
                "",
            ),
        })

        memory_summary_text = memory_summary_result.memory_summary

    reason_verdict_result = reason_verdict_chain.invoke({
        "judiciary_type": judiciary_type,
        "memory_summary": memory_summary_text or "No judiciary memory yet.",
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
        "memory_summary": memory_summary_text or "No judiciary memory yet.",
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

    if turn_count == 1:
        return {
            "type": judiciary_type,
            "latest_overall_round_summary": latest_round_summary_result.latest_overall_round_summary,
            "reasoning": reason_verdict_result.reasoning,
            "verdict": reason_verdict_result.verdict,
            "confidence": confidence_result.confidence,
        }

    if turn_count > 1:
        return {
            "memory_summary": memory_summary_text,
            "latest_overall_round_summary": latest_round_summary_result.latest_overall_round_summary,
            "reasoning": reason_verdict_result.reasoning,
            "verdict": reason_verdict_result.verdict,
            "confidence": confidence_result.confidence,
        }