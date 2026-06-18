from pydantic import BaseModel

from graph.state import CourtroomState
from models.llm import PERSPECTIVE_MODEL
from langchain_core.prompts import ChatPromptTemplate
from prompts.perspective_prompt import (
    PERSPECTIVE_BACKGROUND,
    PUBLIC_PRIVATE_STATEMENT,
    MEMORY_GENERATION,
)


class PerspectiveOutput(BaseModel):
    background: str
    motives: str


class StatementOutput(BaseModel):
    private_thoughts: str
    public_statement: str


class MemoryOutput(BaseModel):
    memory_summary: str


def build_perspective_chain(prompt: str, output_schema: type[BaseModel]):
    return (
        ChatPromptTemplate.from_messages([("system", prompt)])
        | PERSPECTIVE_MODEL.with_structured_output(output_schema)
    )


perspective_chain = build_perspective_chain(PERSPECTIVE_BACKGROUND, PerspectiveOutput)
statement_chain = build_perspective_chain(PUBLIC_PRIVATE_STATEMENT, StatementOutput)
memory_chain = build_perspective_chain(MEMORY_GENERATION, MemoryOutput)


def get_perspective(state: CourtroomState, perspective_id: int):
    for perspective in state.get("perspectives", []):
        if perspective["id"] == perspective_id:
            return perspective
    return None


def update_perspective(
    state: CourtroomState,
    perspective_id: int,
    updates: dict,
):
    return [
        {**perspective, **updates}
        if perspective["id"] == perspective_id
        else perspective
        for perspective in state.get("perspectives", [])
    ]


def perspective_node(state: CourtroomState, perspective_id: int):
    turn_count = state.get("turn_count", 0)

    perspective = get_perspective(state, perspective_id)

    if not perspective or perspective.get("active") is not True:
        return {}

    background = perspective.get("background", "")
    motives = perspective.get("motives", "")
    existing_memory_summary = perspective.get("memory_summary", "")

    if turn_count == 1:
        setup_result = perspective_chain.invoke({
            "id": perspective["id"],
            "role": perspective["role"],
        })

        background = setup_result.background
        motives = setup_result.motives

    if not existing_memory_summary:
        existing_memory_summary = "No memory yet."

    latest_overall_round_summary = state.get(
        "latest_overall_round_summary",
        "No previous courtroom round summary yet."
    )

    statement_result = statement_chain.invoke({
        "role": perspective["role"],
        "background": background,
        "motives": motives,
        "memory_summary": existing_memory_summary,
        "latest_overall_round_summary": latest_overall_round_summary,
    })

    memory_result = memory_chain.invoke({
        "role": perspective["role"],
        "background": background,
        "motives": motives,
        "existing_memory_summary": existing_memory_summary,
        "latest_overall_round_summary": latest_overall_round_summary,
        "latest_private_thoughts": statement_result.private_thoughts,
    })

    return {
        "perspectives": update_perspective(
            state,
            perspective_id,
            {
                "background": background,
                "motives": motives,
                "private_thoughts": statement_result.private_thoughts,
                "public_statement": statement_result.public_statement,
                "memory_summary": memory_result.memory_summary,
            },
        )
    }


def p1_node(state: CourtroomState):
    return perspective_node(state, 1)


def p2_node(state: CourtroomState):
    return perspective_node(state, 2)


def p3_node(state: CourtroomState):
    return perspective_node(state, 3)


def p4_node(state: CourtroomState):
    return perspective_node(state, 4)


def p5_node(state: CourtroomState):
    return perspective_node(state, 5)


def p6_node(state: CourtroomState):
    return perspective_node(state, 6)


def p7_node(state: CourtroomState):
    return perspective_node(state, 7)


def p8_node(state: CourtroomState):
    return perspective_node(state, 8)


def p9_node(state: CourtroomState):
    return perspective_node(state, 9)


def p10_node(state: CourtroomState):
    return perspective_node(state, 10)