from pydantic import BaseModel

from app.courtroom.graph.state import CourtroomState
from app.courtroom.models.llm import PERSPECTIVE_MODEL, PERSPECTIVE_LITE_MODEL
from langchain_core.prompts import ChatPromptTemplate
from app.courtroom.prompts.perspective_prompt import (
    PERSPECTIVE_BACKGROUND,
    PUBLIC_PRIVATE_STATEMENT,
    MEMORY_GENERATION,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


class StatementOutput(BaseModel):
    private_thoughts: str
    public_statement: str


from langchain_core.prompts import ChatPromptTemplate

perspective_chain = (
    ChatPromptTemplate.from_messages(
        [("system", PERSPECTIVE_BACKGROUND)]
    )
    | PERSPECTIVE_LITE_MODEL
    | StrOutputParser()
)

statement_chain = (
    ChatPromptTemplate.from_messages(
        [("system", PUBLIC_PRIVATE_STATEMENT)]
    )
    | PERSPECTIVE_MODEL.with_structured_output(StatementOutput)
)

memory_chain = (
    ChatPromptTemplate.from_messages(
        [("system", MEMORY_GENERATION)]
    )
    | PERSPECTIVE_MODEL
    | StrOutputParser()
)


def get_perspective(state: CourtroomState, perspective_id: int):
    for perspective in state.get("perspectives", []):
        if perspective["id"] == perspective_id:
            return perspective
    return None


def upsert_user_perspective(state: CourtroomState, user_perspective: str):
    existing_perspectives = state.get("perspectives", [])

    p0 = {
        "id": 0,
        "role": "User Perspective",
        "active": True,
        "background_motives": "The user has entered the courtroom to personally add their viewpoint,Ensure their concern, correction, or objection is considered by the court but don't strictly move the decision in users favour he is a common person",
        "public_statement": user_perspective,
    }

    found_p0 = False
    updated_perspectives = []

    for perspective in existing_perspectives:
        if perspective["id"] == 0:
            updated_perspectives.append({
                **perspective,
                "public_statement": user_perspective,
                "active": True,
            })
            found_p0 = True
        else:
            updated_perspectives.append(perspective)

    if not found_p0:
        updated_perspectives.insert(0, p0)

    return updated_perspectives

def perspective_node(state: CourtroomState, perspective_id: int):
    turn_count = state.get("turn_count", 0)

    perspective = get_perspective(state, perspective_id)

    if not perspective or perspective.get("active") is not True:
        return {}

    if turn_count == 1:
        background_motives = perspective_chain.invoke({
            "id": perspective["id"],
            "role": perspective["role"],
        })

        statement_result = statement_chain.invoke({
            "role": perspective["role"],
            "background_motives": background_motives,
        })

        return {
            "perspectives": [
                {
                    **perspective,
                    "background_motives": background_motives,
                    "private_thoughts": statement_result.private_thoughts,
                    "public_statement": statement_result.public_statement,
                },
            ]
        }

    if turn_count > 1:
        background_motives = perspective.get("background_motives", "")
        existing_memory_summary = perspective.get("memory_summary") or "No memory yet."
        latest_overall_round_summary = state.get(
            "latest_overall_round_summary",
            "No previous courtroom round summary yet."
        )

        statement_result = statement_chain.invoke({
            "role": perspective["role"],
            "background_motives": background_motives,
            "memory_summary": existing_memory_summary,
            "latest_overall_round_summary": latest_overall_round_summary,
        })

        memory_result = memory_chain.invoke({
            "role": perspective["role"],
            "background_motives": background_motives,
            "existing_memory_summary": existing_memory_summary,
            "latest_overall_round_summary": latest_overall_round_summary,
            "latest_private_thoughts": statement_result.private_thoughts,
        })

        return {
            "perspectives": [
                {
                    **perspective,
                    "private_thoughts": statement_result.private_thoughts,
                    "public_statement": statement_result.public_statement,
                    "memory_summary": memory_result.memory_summary,
                },
            ]
        }

    return {}




def p0_node(state: CourtroomState):
    return perspective_node(state, 0)


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
