from app.courtroom.rag.structure.graph.states import RagState
from app.courtroom.rag.structure.function.decompose import decompose
from app.courtroom.rag.structure.function.filter import filter_docs
from app.courtroom.rag.structure.function.recompose import recompose

def correct_node(state: RagState):
    
    # If we are looping back, skip search & filter and just recompose
    if state.get("turn", 0) >= 1:
        decomposed = state.get("decomposed_docs", [])
        filtered = state.get("filtered_docs", [])
    else:
        # Step 1: Decompose - break sub-queries and fetch more targeted docs
        decomposed = decompose(state)
        
        # Step 2: Filter - remove irrelevant chunks from the pool
        filtered = filter_docs(decomposed, state)
    
    # Step 3: Recompose - LLM reads filtered docs and writes a structured legal summary
    # (what each law says, what each case held, relevant provisions etc.)
    final = recompose(filtered, state)
    
    return {
        "decomposed_docs": decomposed,
        "filtered_docs": filtered,
        "final_docs": final
    }