from typing import List, Optional
from pydantic import BaseModel, Field
from app.courtroom.graph.state import CourtroomState
from app.courtroom.models.llm import QUERYREFINE_MODEL, QUERYREFINE_LITE_MODEL
from app.courtroom.prompts.query_refine_prompt import (
    USER_INPUT_REFINER_PROMPT,
    USER_PERSPECTIVE_PROMPT,
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.courtroom.nodes.perspective_node import upsert_user_perspective


class UserCommands(BaseModel):
    judiciary_type: Optional[str] = Field(default=None, description="Explicit demand for judiciary configuration if requested (e.g. 'corrupt', 'neutral'). None if not specified.")
    number_of_perspectives: Optional[int] = Field(default=None, description="Explicit number of perspectives requested. None if not specified.")
    specific_roles: Optional[List[str]] = Field(default=None, description="Explicit list of roles or groups requested. None if not specified.")


class QueryRefineOutput(BaseModel):
    case_representation: str = Field(description="The user's original query rewritten as a formal legal case or courtroom investigation.")
    user_commands: UserCommands = Field(description="Structured commands, settings, or instructions the user specified. If none of these were explicitly requested, keep fields null.")


set_up_template = ChatPromptTemplate.from_messages([
    ("system", USER_INPUT_REFINER_PROMPT),
    ("human", "User Input: {topic}")
])

set_up_chain = (
    set_up_template
    | QUERYREFINE_MODEL.with_structured_output(QueryRefineOutput)
)


p0_template = ChatPromptTemplate.from_messages([
    ("system", USER_PERSPECTIVE_PROMPT),
    ("human", "User Input: {user_input}")
])

p0_chain = (
    p0_template
    | QUERYREFINE_LITE_MODEL
    | StrOutputParser()
)


def query_refine_node(state: CourtroomState):
    turn_count = state.get("turn_count", 0)

    if turn_count == 0:
        refined_query = set_up_chain.invoke({
            "topic": state["user_input"]
        })

        return {
            "user_input": refined_query.case_representation,
            "user_commands": refined_query.user_commands.model_dump(),
            "turn_count": turn_count + 1
        }

    action = state.get("next_action")

    if action == "continue_debate_with_input":
        user_perspective = p0_chain.invoke({
            "user_input": state["in_session_input"]
        })

        return {
            "in_session_input": "",
            "next_action": "continue_debate",
            "perspectives": upsert_user_perspective(state, user_perspective),
            "turn_count": turn_count + 1
        }

    return {
        "turn_count": turn_count + 1
    }