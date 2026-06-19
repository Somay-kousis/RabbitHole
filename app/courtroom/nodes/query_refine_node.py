from app.courtroom.graph.state import CourtroomState
from app.courtroom.models.llm import QUERYREFINE_MODEL
from app.courtroom.prompts.query_refine_prompt import (
    USER_INPUT_REFINER_PROMPT,
    USER_PERSPECTIVE_PROMPT,
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.courtroom.nodes.perspective_node import upsert_user_perspective


set_up_template = ChatPromptTemplate.from_messages([
    ("system", USER_INPUT_REFINER_PROMPT),
    ("human", "User Input: {topic}")
])

set_up_chain = (
    set_up_template
    | QUERYREFINE_MODEL
    | StrOutputParser()
)


p0_template = ChatPromptTemplate.from_messages([
    ("system", USER_PERSPECTIVE_PROMPT)
])

p0_chain = (
    p0_template
    | QUERYREFINE_MODEL
    | StrOutputParser()
)


def query_refine_node(state: CourtroomState):
    turn_count = state.get("turn_count", 0)

    if turn_count == 0:
        refined_query = set_up_chain.invoke({
            "topic": state["user_input"]
        })

        return {
            "user_input": refined_query,
            "turn_count": turn_count + 1
        }

    action = state.get("next_action")

    if action == "continue debate with input":
        user_perspective = p0_chain.invoke({
            "user_input": state["in_session_input"]
        })

        return {
            "in_session_input": "",
            "next_action": "continue debate",
            "perspectives": upsert_user_perspective(state, user_perspective),
            "turn_count": turn_count + 1
        }

    return {
        "turn_count": turn_count + 1
    }