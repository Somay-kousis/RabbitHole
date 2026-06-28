from app.courtroom.rag.structure.graph.states import RagState

def not_supported_node(state: RagState):
    """
    Pass-through node triggered when a generated summary contains hallucinations.
    Simply prints a status message to the console before routing back to recompose.
    """
    turn = state.get("turn", 0)
    critique = state.get("why_loop", "No critique provided.")
    
    print(f"\n--- [SRAG REWRITE LOOP] Attempt {turn}: Summary contains unsupported claims. Re-routing to Recompose... ---")
    print(f"Auditor Critique:\n{critique}\n")
    
    return {}
