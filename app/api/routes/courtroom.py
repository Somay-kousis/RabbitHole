from typing import Any, Literal
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from langgraph.types import Command
from pydantic import BaseModel, Field

from app.courtroom.graph.graph import courtroom_app


router = APIRouter(prefix="/courtroom", tags=["courtroom"])

CourtroomAction = Literal[
    "continue debate",
    "continue debate with input",
    "generate conclusion",
]

HITL_OPTIONS = [
    "continue debate",
    "continue debate with input",
    "generate conclusion",
]


class CourtroomStartRequest(BaseModel):
    user_input: str = Field(min_length=1)
    session_id: str | None = None


class CourtroomActionRequest(BaseModel):
    session_id: str = Field(min_length=1)
    action: CourtroomAction
    in_session_input: str | None = None


class CourtroomConclusionRequest(BaseModel):
    session_id: str = Field(min_length=1)


class CourtroomStateResponse(BaseModel):
    session_id: str
    status: Literal["hitl", "completed"]
    state: dict[str, Any]
    hitl_options: list[str] = []


def graph_config(session_id: str):
    return {
        "configurable": {
            "thread_id": session_id,
        }
    }


def response_for(session_id: str, state: dict[str, Any]) -> CourtroomStateResponse:
    snapshot = courtroom_app.get_state(graph_config(session_id))
    is_waiting_for_hitl = "hitl_node" in snapshot.next

    return CourtroomStateResponse(
        session_id=session_id,
        status="hitl" if is_waiting_for_hitl else "completed",
        state=state,
        hitl_options=HITL_OPTIONS if is_waiting_for_hitl else [],
    )


@router.post("/start", response_model=CourtroomStateResponse)
def start_courtroom(request: CourtroomStartRequest):
    session_id = request.session_id or str(uuid4())

    initial_state = {
        "user_input": request.user_input,
        "turn_count": 0,
    }

    state = courtroom_app.invoke(initial_state, graph_config(session_id))
    return response_for(session_id, state)


@router.post("/action", response_model=CourtroomStateResponse)
def run_courtroom_action(request: CourtroomActionRequest):
    if request.action == "continue debate with input" and not request.in_session_input:
        raise HTTPException(
            status_code=400,
            detail="in_session_input is required when action is 'continue debate with input'.",
        )

    update: dict[str, Any] = {
        "next_action": request.action,
    }

    if request.action == "continue debate with input":
        update["in_session_input"] = request.in_session_input

    state = courtroom_app.invoke(
        Command(update=update),
        graph_config(request.session_id),
    )

    return response_for(request.session_id, state)


@router.post("/continue", response_model=CourtroomStateResponse)
def continue_courtroom(request: CourtroomActionRequest):
    return run_courtroom_action(request)


@router.post("/conclusion", response_model=CourtroomStateResponse)
def generate_conclusion(request: CourtroomConclusionRequest):
    return run_courtroom_action(
        CourtroomActionRequest(
            session_id=request.session_id,
            action="generate conclusion",
        )
    )
