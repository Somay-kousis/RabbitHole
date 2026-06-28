from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.courtroom.models.llm import RETRIVER_LITE_MODEL
from app.courtroom.rag.retriver import search_documents
from app.courtroom.rag.structure.graph.states import RagState

class SubQueries(BaseModel):
    sub_queries: list[str]

decompose_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a legal research assistant. Your job is to break down a complex legal query into simpler, targeted sub-queries for a document search engine.
    
    Each sub-query should target a single specific legal concept, provision, or case aspect.
    Return a list of 3 to 5 specific sub-queries."""),
    ("user", "Request: {request}")
])

decompose_chain = decompose_prompt | RETRIVER_LITE_MODEL.with_structured_output(SubQueries)

def decompose(state: RagState) -> list:
    """
    Breaks the request into sub-queries, runs each through the retriever,
    and returns a merged pool of documents (duplicates are naturally handled by IDs).
    """
    result = decompose_chain.invoke({"request": state["request"]})
    sub_queries = result.sub_queries
    
    all_docs = list(state["documents"])  # start with existing docs
    seen_contents = {doc.page_content for doc in all_docs}
    
    for query in sub_queries:
        new_docs = search_documents(query)
        for doc in new_docs:
            if doc.page_content not in seen_contents:
                all_docs.append(doc)
                seen_contents.add(doc.page_content)
    
    return all_docs
