from typing import List

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from courtroom.graph.state import CourtroomState
from models.llm import MODERATOR_MODEL
from app.courtroom.prompts.moderator_prompt import (
    NUMBER_OF_PERSPECTIVES_PROMPT,
    ROLE_ASSIGNMENT_PROMPT,
    JUDICIARY_TYPE_PROMPT,
)


class PerspectiveCount(BaseModel):
    count: int = Field(ge=3, le=10)


class RoleCard(BaseModel):
    id: int
    role: str
    active: bool


class RoleAssignment(BaseModel):
    perspectives: List[RoleCard]


class JudiciaryType(BaseModel):
    judiciary_corrupt: bool


perspective_count_prompt = ChatPromptTemplate.from_messages([
    ("system", NUMBER_OF_PERSPECTIVES_PROMPT)
])

perspective_count_chain = (
    perspective_count_prompt
    | MODERATOR_MODEL.with_structured_output(PerspectiveCount)
)


role_assignment_prompt = ChatPromptTemplate.from_messages([
    ("system", ROLE_ASSIGNMENT_PROMPT)
])

role_assignment_chain = (
    role_assignment_prompt
    | MODERATOR_MODEL.with_structured_output(RoleAssignment)
)


judiciary_type_prompt = ChatPromptTemplate.from_messages([
    ("system", JUDICIARY_TYPE_PROMPT)
])

judiciary_type_chain = (
    judiciary_type_prompt
    | MODERATOR_MODEL.with_structured_output(JudiciaryType)
)


def moderator_node(state: CourtroomState):
    """
    First setup pass:
    - decides number of AI perspectives
    - assigns only id, role, active
    - initializes empty background, motives, memory, and round summary

    Later passes:
    - keeps existing courtroom setup
    """

    number_result = perspective_count_chain.invoke({
        "query": state["user_input"]
    })

    role_result = role_assignment_chain.invoke({
        "query": state["user_input"],
        "number_of_perspectives": number_result.count,
    })

    judiciary_result = judiciary_type_chain.invoke({
        "query": state["user_input"]
    })

    return {
        "number_of_perspectives": number_result.count,
        "perspectives": [
            {
                "id": perspective.id,
                "role": perspective.role,
                "active": perspective.active,
                "background": "",
                "motives": "",
                "memory_summary": "",
                "latest_round_summary": "",
            }
            for perspective in role_result.perspectives
        ],
        "judiciary_corrupt": judiciary_result.judiciary_corrupt,
    }