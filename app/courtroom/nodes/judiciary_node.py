from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from app.courtroom.graph.state import CourtroomState
from app.courtroom.models.llm import JUDICIARY_MODEL, JUDICIARY_LITE_MODEL
from app.courtroom.prompts.judiciary_prompt import (
    JUDICIARY_TYPE_PROMPT,
    MEMORY_SUMMARY_PROMPT,
    LATEST_OVERALL_ROUND_SUMMARY_PROMPT,
    REASON_PROMPT,
    VERDICT_PROMPT
)
from langchain_core.output_parsers import StrOutputParser


class JudiciaryTypeOutput(BaseModel):
    type: str = Field(description="A concise judiciary profile describing the judge's nature, likely biases, and decision style.")


class MemorySummaryOutput(BaseModel):
    memory_summary: str = Field(description="The updated judiciary memory summary.")


class LatestRoundSummaryOutput(BaseModel):
    latest_overall_round_summary: str = Field(description="The public record/summary of the courtroom round.")


type_chain = (
    ChatPromptTemplate.from_messages([("system", JUDICIARY_TYPE_PROMPT)])
    | JUDICIARY_LITE_MODEL.with_structured_output(JudiciaryTypeOutput)
)

memory_summary_chain = (
    ChatPromptTemplate.from_messages([("system", MEMORY_SUMMARY_PROMPT)])
    | JUDICIARY_MODEL.with_structured_output(MemorySummaryOutput)
)

reason_chain = (
    ChatPromptTemplate.from_messages([("system", REASON_PROMPT)])
    | JUDICIARY_MODEL
    | StrOutputParser()
)

verdict_chain = (
    ChatPromptTemplate.from_messages([("system", VERDICT_PROMPT)])
    | JUDICIARY_LITE_MODEL
    | StrOutputParser()
)

latest_round_summary_chain = (
    ChatPromptTemplate.from_messages([("system", LATEST_OVERALL_ROUND_SUMMARY_PROMPT)])
    | JUDICIARY_MODEL.with_structured_output(LatestRoundSummaryOutput)
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
            "latest_overall_round_summary": state.get(
                "latest_overall_round_summary",
                "",
            ),
        })

        memory_summary_text = memory_summary_result.memory_summary

    if turn_count < 1:
        return {}

    reason_result = reason_chain.invoke({
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

    verdict_result = verdict_chain.invoke({
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


    latest_round_summary_result = latest_round_summary_chain.invoke({
        "public_statements": public_statements,
        "judiciary_reasoning": reason_result,
        "judiciary_verdict": verdict_result,
    })

    judiciary_state = {
        "type": judiciary_type,
        "memory_summary": memory_summary_text,
        "reasoning": reason_result,
        "verdict": verdict_result,
    }

    return {
        "judiciary": judiciary_state,
        "latest_overall_round_summary": latest_round_summary_result.latest_overall_round_summary,
    }
