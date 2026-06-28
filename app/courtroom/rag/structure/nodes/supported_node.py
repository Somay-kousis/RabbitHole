from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from app.courtroom.models.llm import RETRIVER_LITE_MODEL
from app.courtroom.rag.structure.graph.states import RagState

class SupportCheck(BaseModel):
    is_supported: bool
    critique: str

support_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a legal auditor. Your job is to check if the generated legal brief (summary) is fully supported by the original retrieved document chunks.
    
    Verify that every claim, provision, or case citation made in the summary is present in the source documents.
    If the summary mentions facts, sections, or holdings NOT found in the source documents, mark it as NOT supported.
    
    If is_supported is False, write a clear critique explaining exactly what claims or citations are made up and must be removed."""),
    ("user", "Original Source Documents:\n{documents}\n\nGenerated Summary:\n{summary}")
])

support_chain = support_prompt | RETRIVER_LITE_MODEL.with_structured_output(SupportCheck)

def supported_node(state: RagState):
    """
    Grades the generated final_docs against the filtered_docs to check for hallucinations.
    Sets 'is_sup' (boolean) and 'why_loop' (critique string).
    """
    filtered_docs = state.get("filtered_docs", [])
    final_docs = state.get("final_docs", [])
    
    if not final_docs or not filtered_docs:
        return {"is_sup": True, "why_loop": ""}
        
    docs_text = "\n\n---\n\n".join([doc.page_content for doc in filtered_docs])
    summary_text = final_docs[0].page_content
    
    result = support_chain.invoke({
        "documents": docs_text,
        "summary": summary_text
    })
    
    turn = state.get("turn", 0) + 1
    
    return {
        "is_sup": result.is_supported,
        "why_loop": result.critique if not result.is_supported else "",
        "turn": turn
    }
