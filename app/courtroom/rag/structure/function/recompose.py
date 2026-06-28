from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.courtroom.models.llm import RETRIEVER_MODEL
from app.courtroom.rag.structure.graph.states import RagState
from langchain_core.documents import Document

recompose_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a senior legal researcher preparing a structured legal brief for a courtroom agent.

    You are given a set of filtered legal document chunks relevant to the case. Your job is to synthesize them into a concise, structured legal summary.
    
    For each relevant law or case, clearly state:
    - The name of the law or case
    - The specific provision, section, or holding that applies
    - How it is directly relevant to this case
    
    Be precise and legal in your language. Do not add any information not present in the provided documents."""),
    ("user", "Case Request: {request}\n\nRelevant Legal Documents:\n{documents}\n\n{critique}")
])

recompose_chain = recompose_prompt | RETRIEVER_MODEL | StrOutputParser()

def recompose(filtered_docs: list, state: RagState) -> list:
    """
    Reads all filtered document chunks, synthesizes them into a structured
    legal summary string, and wraps it in a Document object for state consistency.
    """
    if not filtered_docs:
        return []
    
    # Concatenate all filtered doc texts
    docs_text = "\n\n---\n\n".join([doc.page_content for doc in filtered_docs])
    
    # Check if this is a rewrite loop
    turn = state.get("turn", 0)
    why_loop = state.get("why_loop", "")
    
    if turn >= 1 and why_loop:
        critique_str = f"CRITIQUE FROM PREVIOUS ATTEMPT:\n{why_loop}\nPlease rewrite the summary to correct these errors, ensuring all claims are fully supported by the document chunks."
    else:
        critique_str = ""
    
    # LLM synthesizes a structured legal summary
    summary = recompose_chain.invoke({
        "request": state["request"],
        "documents": docs_text,
        "critique": critique_str
    })
    
    # Wrap the output in a Document for state consistency
    from langchain_core.documents import Document
    final_doc = Document(
        page_content=summary,
        metadata={"type": "recomposed_legal_brief", "source_count": len(filtered_docs)}
    )
    
    return [final_doc]
