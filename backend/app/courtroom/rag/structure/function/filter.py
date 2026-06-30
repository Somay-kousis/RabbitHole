from typing import Literal
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from app.courtroom.models.llm import RETRIVER_LITE_MODEL
from app.courtroom.rag.structure.graph.states import RagState
from langchain_core.documents import Document

class FilterScore(BaseModel):
    score: Literal["yes", "no"]

filter_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a legal relevance checker. Given a legal document chunk and the case request, decide strictly if the document contains relevant information. Reply only 'yes' or 'no'."),
    ("user", "Request: {request}\n\nDocument: {document}")
])

filter_chain = filter_prompt | RETRIVER_LITE_MODEL.with_structured_output(FilterScore)

def filter_docs(decomposed_docs: list, state: RagState) -> list:
    """
    Scores each document chunk against the request.
    Returns only the chunks that scored 'yes'.
    """
    request = state["request"]
    filtered = []
    
    for doc in decomposed_docs:
        result = filter_chain.invoke({
            "request": request,
            "document": doc.page_content
        })
        if result.score == "yes":
            filtered.append(doc)
    
    return filtered
