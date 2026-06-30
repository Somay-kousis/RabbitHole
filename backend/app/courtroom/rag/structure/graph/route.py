from app.courtroom.rag.structure.graph.states import RagState

def route_ragornot(state: RagState) -> str:
    if state["retriever_needed"]:
        return "retriever_node"
    else:
        return "placeholder"

def route_gooddocs(state: RagState) -> str:
    if state["good_retrieval"] == "yes":
        return "correct_node"
    elif state["good_retrieval"] == "no":
        return "incorrect_node"
    else:
        return "ambigious_node"                
    
def route_issupported(state: RagState) -> str:
    if state["turn"] >= 5:
        return "partial_supported_node" 
    
    if state["is_sup"]:
        return "supported_node"
    else:
        return "not_supported_node"       
