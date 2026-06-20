from app.courtroom.graph.state import CourtroomState


def hitl_node(state: CourtroomState):
    action = state.get("next_action")

    if action not in {
        "continue debate",
        "continue debate with input",
        "generate conclusion",
    }:
        raise ValueError(f"Invalid next_action: {action}")

    return {}