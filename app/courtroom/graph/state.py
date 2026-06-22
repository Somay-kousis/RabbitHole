from typing import Annotated, TypedDict, List, NotRequired, Literal

from app.courtroom.graph.reducers import merge_perspectives


class PerspectiveState(TypedDict):
    id: int
    role: str
    active: bool

    background_motives: str
    memory_summary: NotRequired[str]

    public_statement: NotRequired[str]
    private_thoughts: NotRequired[str]


class JudiciaryState(TypedDict):
    type: str
    memory_summary: NotRequired[str]
    reasoning: NotRequired[str]
    verdict: NotRequired[str]


CourtAction = Literal[
    "continue_debate",
    "continue_debate_with_input",
    "generate_conclusion",
]


class CourtroomState(TypedDict):
    user_input: str
    number_of_perspectives: NotRequired[int]
    perspectives: NotRequired[Annotated[List[PerspectiveState], merge_perspectives]]

    judiciary_corrupt: NotRequired[bool]
    judiciary: NotRequired[JudiciaryState]

    latest_overall_round_summary: NotRequired[str]
    current_round: NotRequired[int]

    in_session_input: NotRequired[str]
    conclusion: NotRequired[str]
    next_action: NotRequired[CourtAction]

    turn_count: int
