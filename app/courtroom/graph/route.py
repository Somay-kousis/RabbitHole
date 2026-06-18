from langgraph.graph import END
from state import CourtroomState


def route_after_hitl(state: CourtroomState):

    action = state["next_action"]

    if action == "continue debate":
        return "perspective_node"

    elif action == "continue debate with input":
        return "query_refine_node"

    elif action == "generate conclusion":
        return "conclusion_node"

    raise ValueError(f"Invalid next_action: {action}")