from langgraph.graph import END
from state import CourtroomState


def action_one_route(state: CourtroomState):
    action = state.get("next_action")

    if action in ("continue debate", "continue debate with input"):
        return "moderator_node"

    if action == "generate conclusion":
        return "conclusion_node"

    raise ValueError(f"Unknown action after debate: {action}")


def action_two_route(state: CourtroomState):
    action = state.get("next_action")

    if action == "satisfied":
        return END

    if action == "have questions":
        return "general_node"

    if action == "continue from where we left":
        return "moderator_node"

    raise ValueError(f"Unknown action after conclusion: {action}")

