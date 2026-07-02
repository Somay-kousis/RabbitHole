from typing import List

from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate

from app.courtroom.graph.state import CourtroomState
from app.courtroom.models.llm import MODERATOR_MODEL
from app.courtroom.prompts.moderator_prompt import ROLE_ASSIGNMENT_PROMPT


class RoleCard(BaseModel):
    role: str
    active: bool


class RoleAssignment(BaseModel):
    perspectives: List[RoleCard]


# We only need the role assignment chain now, since count and profile are set by the user
role_assignment_chain = (
    ChatPromptTemplate.from_messages([("system", ROLE_ASSIGNMENT_PROMPT)])
    | MODERATOR_MODEL.with_structured_output(RoleAssignment)
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
    # Moderator should only create roles once
    if state.get("perspectives"):
        return {}

    query = state["user_input"]
    user_commands = state.get("user_commands", {})

    # 1. Perspective Count (directly read from state/commands, default to 4)
    perspective_count = (
        state.get("number_of_perspectives") 
        or user_commands.get("number_of_perspectives") 
        or 4
    )

    # 2. Role Assignment (ask LLM to dynamically define roles matching the count)
    specific_roles = user_commands.get("specific_roles") or []
    role_result = role_assignment_chain.invoke({
        "query": query,
        "number_of_perspectives": perspective_count,
        "specific_roles": ", ".join(specific_roles) if specific_roles else "None specified",
    })

    # 3. Judiciary Profile (directly read from state/commands, default to false/fair)
    judiciary_corrupt = state.get("judiciary_corrupt")
    if judiciary_corrupt is None:
        requested_judiciary = user_commands.get("judiciary_type")
        if requested_judiciary is not None:
            judiciary_corrupt = (requested_judiciary.lower() == "corrupt")
        else:
            judiciary_corrupt = False

    return {
        "number_of_perspectives": perspective_count,
        "perspectives": [
            build_perspective(index, perspective)
            for index, perspective in enumerate(role_result.perspectives, start=1)
        ],
        "judiciary_corrupt": judiciary_corrupt,
    }
