from typing import TypedDict, List, NotRequired, Literal


class PerspectiveState(TypedDict):
    id: int
    role: str
    active: bool

    background: str
    motives: str
    memory_summary: str

    public_statement: NotRequired[str]
    private_thoughts: NotRequired[str]


CourtAction = Literal[
    "continue debate",
    "continue debate with input",
    "generate conclusion",
    "satisfied",
    "have questions",
    "continue from where we left"
]


class CourtroomState(TypedDict):
    user_input: str
    number_of_perspectives: NotRequired[int]
    perspectives: NotRequired[List[PerspectiveState]]

    judiciary_corrupt: NotRequired[bool]

    latest_overall_round_summary: NotRequired[str]
    current_round: NotRequired[int]

    in_session_input: NotRequired[str]
    conclusion: NotRequired[str]
    next_action: NotRequired[CourtAction]

    turn_count: int