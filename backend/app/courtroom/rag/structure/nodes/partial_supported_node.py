from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.courtroom.models.llm import RETRIEVER_MODEL
from app.courtroom.rag.structure.graph.states import RagState
from langchain_core.documents import Document

partial_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a senior legal auditor. We have tried 5 times to correct a generated legal brief, but it still contains claims that cannot be found in our official local documents.
    
    Your job is to read the original source documents and the generated summary. Output a final restructured summary where you mark each legal claim, provision, or case citation:
    - If it is fully supported by the local source documents, mark it clearly with [OFFICIAL].
    - If it is mentioned in the summary but NOT found in our local source documents, mark it clearly with [UNOFFICIAL].
    
    Be extremely objective and precise. Output the entire summary with [OFFICIAL] and [UNOFFICIAL] tags next to each legal point."""),
    ("user", "Original Source Documents:\n{documents}\n\nGenerated Summary:\n{summary}")
])

partial_chain = partial_prompt | RETRIEVER_MODEL | StrOutputParser()

def partial_supported_node(state: RagState):
    """
    Fallback node executed after 5 failed checks. 
    Segregates the summary into Verified and Unverified claims for the courtroom.
    """
    filtered_docs = state.get("filtered_docs", [])
    final_docs = state.get("final_docs", [])
    
    if not final_docs or not filtered_docs:
        return {}
        
    docs_text = "\n\n---\n\n".join([doc.page_content for doc in filtered_docs])
    summary_text = final_docs[0].page_content
    
    final_report = partial_chain.invoke({
        "documents": docs_text,
        "summary": summary_text
    })
    
    # Wrap the audited report in a Document and save it in state
    report_doc = Document(
        page_content=final_report,
        metadata={"type": "audited_partially_supported_brief", "verified": False}
    )
    
    return {
        "final_docs": [report_doc]
    }
