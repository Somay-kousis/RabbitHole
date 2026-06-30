from typing import List

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from app.courtroom.graph.state import CourtroomState
from app.courtroom.models.llm import MODERATOR_MODEL
from app.courtroom.prompts.moderator_prompt import (
    NUMBER_OF_PERSPECTIVES_PROMPT,
    ROLE_ASSIGNMENT_PROMPT,
    JUDICIARY_TYPE_PROMPT,
)


class PerspectiveCount(BaseModel):
    count: int = Field(ge=2, le=10)


class RoleCard(BaseModel):
    role: str
    active: bool


class RoleAssignment(BaseModel):
    perspectives: List[RoleCard]


class JudiciaryType(BaseModel):
    judiciary_corrupt: bool


def build_chain(prompt: str, output_schema: type[BaseModel]):
    return (
        ChatPromptTemplate.from_messages([("system", prompt)])
        | MODERATOR_MODEL.with_structured_output(output_schema)
    )


perspective_count_chain = build_chain(
    NUMBER_OF_PERSPECTIVES_PROMPT,
    PerspectiveCount,
)

role_assignment_chain = build_chain(
    ROLE_ASSIGNMENT_PROMPT,
    RoleAssignment,
)

judiciary_type_chain = build_chain(
    JUDICIARY_TYPE_PROMPT,
    JudiciaryType,
)


def build_perspective(perspective_id: int, role_card: RoleCard):
    return {
        "id": perspective_id,
        "role": role_card.role,
        "active": role_card.active,
        "background": "",
        "motives": "",
        "memory_summary": "",
    }


def moderator_node(state: CourtroomState):
    # Moderator should only create roles once.
    if state.get("perspectives"):
        return {}

    query = state["user_input"]
    user_commands = state.get("user_commands", {})

    # 1. Perspective Count
    requested_count = user_commands.get("number_of_perspectives")
    if requested_count is not None:
        perspective_count = requested_count
    else:
        number_result = perspective_count_chain.invoke({
            "query": query,
        })
        perspective_count = number_result.count

    # 2. Role Assignment
    specific_roles = user_commands.get("specific_roles") or []
    role_result = role_assignment_chain.invoke({
        "query": query,
        "number_of_perspectives": perspective_count,
        "specific_roles": ", ".join(specific_roles) if specific_roles else "None specified",
    })

    # 3. Judiciary Type
    requested_judiciary = user_commands.get("judiciary_type")
    if requested_judiciary is not None:
        judiciary_corrupt = (requested_judiciary.lower() == "corrupt")
    else:
        judiciary_result = judiciary_type_chain.invoke({
            "query": query,
        })
        judiciary_corrupt = judiciary_result.judiciary_corrupt

    return {
        "number_of_perspectives": perspective_count,
        "perspectives": [
            build_perspective(index, perspective)
            for index, perspective in enumerate(role_result.perspectives, start=1)
        ],
        "judiciary_corrupt": judiciary_corrupt,
    }
