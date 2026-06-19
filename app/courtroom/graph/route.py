from graph.state import CourtroomState


def route_after_hitl(state: CourtroomState):
    action = state.get("next_action", "generate conclusion")

    if action == "continue debate":
        return "moderator_node"

    if action == "continue debate with input":
        return "query_refine_node"

    if action == "generate conclusion":
        return "conclusion_node"

    raise ValueError(f"Invalid next_action: {action}")
