from graph.state import CourtroomState

def hitl_node(state: CourtroomState):
    if state.get("next_action") == "continue debate":
        return {
            "turn_count": state.get("turn_count", 0) + 1,
        }

    return {}
