from typing import TypedDict, List, NotRequired, Literal


class Perspective(TypedDict):
    id: int
    role: str
    background: str
    motives: str
    beliefs: List[str]
    memory: List[str]
    public_statement: NotRequired[str]
    private_thoughts: NotRequired[str]
    active: bool


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
    perspectives: NotRequired[List[Perspective]]

    judiciary_corrupt: NotRequired[bool]

    session_summary: NotRequired[str]
    debate_history: NotRequired[List[str]]
    current_round: NotRequired[int]

    in_session_input: NotRequired[str]
    conclusion: NotRequired[str]
    next_action: NotRequired[CourtAction]