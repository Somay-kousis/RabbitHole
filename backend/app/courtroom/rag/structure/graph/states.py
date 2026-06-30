from typing import TypedDict, Literal

class RagState(TypedDict):
    query: str
    retriever_needed: bool
    request: str

    documents: list

    decomposed_docs: list
    filtered_docs: list
    final_docs: list
    
    good_retrieval: Literal["yes","no","ambigious"]
    
    is_sup: bool
    turn: int
    why_loop: str