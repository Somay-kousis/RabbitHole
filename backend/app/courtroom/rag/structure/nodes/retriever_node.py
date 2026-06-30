from app.courtroom.rag.structure.graph.states import RagState
from app.courtroom.graph.state import CourtroomState
from app.courtroom.rag.retriver import search_documents

def retriver_node(state: RagState):
    query = state['request']

    docs = search_documents(query)

    return {"documents": docs}