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


perspective_prompt = ChatPromptTemplate.from_messages([
    ("system", PERSPECTIVE_BACKGROUND)
])

statement_prompt = ChatPromptTemplate.from_messages([
    ("system", PUBLIC_PRIVATE_STATEMENT)
])

memory_generation_prompt = ChatPromptTemplate.from_messages([
    ("system", MEMORY_GENERATION)
])


perspective_chain = (
    perspective_prompt
    | PERSPECTIVE_MODEL.with_structured_output(PerspectiveOutput)
)

statement_chain = (
    statement_prompt
    | PERSPECTIVE_MODEL.with_structured_output(StatementOutput)
)

memory_chain = (
    memory_generation_prompt
    | PERSPECTIVE_MODEL.with_structured_output(MemoryOutput)
)


def get_perspective(state: CourtroomState, perspective_id: int):
    for perspective in state.get("perspectives", []):
        if perspective["id"] == perspective_id:
            return perspective

    return None


def perspective_node(state: CourtroomState, perspective_id: int):
    turn_count = state.get("turn_count", 0)

    perspective = get_perspective(state, perspective_id)

    if perspective is None:
        return {}

    if perspective.get("active") is not True:
        return {}

    background = perspective.get("background", "")
    motives = perspective.get("motives", "")

    # Turn 1: setup background + motives first.
    # Turn 2 onward: reuse existing background + motives.
    if turn_count == 1:
        setup_result = perspective_chain.invoke({
            "id": perspective["id"],
            "role": perspective["role"],
        })

        background = setup_result.background
        motives = setup_result.motives

    memory_summary = "\n".join(perspective.get("memory", []))

    if not memory_summary:
        memory_summary = "No memory yet."

    statement_result = statement_chain.invoke({
        "role": perspective["role"],
        "background": background,
        "motives": motives,
        "memory_summary": memory_summary,
    })

    memory_result = memory_chain.invoke({
        "existing_memory_summary": memory_summary,
        "previous_public_statement": statement_result.public_statement,
        "previous_private_thoughts": statement_result.private_thoughts,
        "role": perspective["role"],
        "background": background,
        "motives": motives,
    })

    updated_perspectives = []

    for p in state["perspectives"]:
        if p["id"] == perspective_id:
            updated_perspectives.append({
                **p,
                "background": background,
                "motives": motives,
                "private_thoughts": statement_result.private_thoughts,
                "public_statement": statement_result.public_statement,
                "memory": [memory_result.memory_summary],
            })
        else:
            updated_perspectives.append(p)

    return {
        "perspectives": updated_perspectives,
        "debate_history": state.get("debate_history", []) + [
            {
                "perspective_id": perspective["id"],
                "role": perspective["role"],
                "public_statement": statement_result.public_statement,
            }
        ],
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