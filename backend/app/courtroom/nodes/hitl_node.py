from app.courtroom.graph.state import CourtroomState


def hitl_node(state: CourtroomState):
    action = state.get("next_action")

    if action not in {
        "continue_debate",
        "continue_debate_with_input",
        "generate_conclusion",
    }:
        raise ValueError(f"Invalid next_action: {action}")

    return {}