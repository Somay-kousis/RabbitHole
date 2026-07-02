from typing import List
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from app.courtroom.models.llm import RETRIVER_LITE_MODEL
from app.courtroom.rag.structure.graph.states import RagState

class FilterReport(BaseModel):
    relevant_indices: List[int]

filter_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a legal relevance checker. 
Given a case request and a list of numbered document chunks, decide strictly which documents contain relevant information to help answer the request.

Reply with a JSON object containing `relevant_indices`, which is a list of the 0-based indices of all document chunks that are relevant. If none are relevant, return an empty list. Do not explain your decisions."""),
    ("user", "Request: {request}\n\nDocuments:\n{documents_list}")
])

filter_chain = filter_prompt | RETRIVER_LITE_MODEL.with_structured_output(FilterReport)

def filter_docs(decomposed_docs: list, state: RagState) -> list:
    """
    Scores each document chunk against the request in a single LLM call.
    Returns only the chunks that scored relevant.
    """
    if not decomposed_docs:
        return []

    request = state["request"]

    # Format the documents list for a single prompt
    documents_list = ""
    for i, doc in enumerate(decomposed_docs):
        documents_list += f"[{i}] {doc.page_content}\n\n"

    try:
        result = filter_chain.invoke({
            "request": request,
            "documents_list": documents_list
        })
        relevant_indices = result.relevant_indices
    except Exception as e:
        print(f"Error in filter_docs single-call filtering: {e}. Defaulting to keep all.")
        return decomposed_docs

    filtered = []
    for idx in relevant_indices:
        if 0 <= idx < len(decomposed_docs):
            filtered.append(decomposed_docs[idx])
            
    return filtered
