from typing import List
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from app.courtroom.models.llm import RETRIVER_LITE_MODEL
from app.courtroom.rag.structure.graph.states import RagState

class RelevanceReport(BaseModel):
    relevant_indices: List[int]

grader_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a legal document quality grader. 
Given a case request and a list of numbered document chunks, evaluate each document chunk independently.
Determine if the document contains relevant information to help answer the request.

Reply with a JSON object containing `relevant_indices`, which is a list of the 0-based indices of all document chunks that are relevant. If none are relevant, return an empty list. Do not explain your decisions."""),
    ("user", "Request: {request}\n\nDocuments:\n{documents_list}")
])

grader_chain = grader_prompt | RETRIVER_LITE_MODEL.with_structured_output(RelevanceReport)

def docs_quality_node(state: RagState):
    documents = state["documents"]
    request = state["request"]

    if not documents:
        return {"good_retrieval": "no"}

    # Format the documents list for a single prompt
    documents_list = ""
    for i, doc in enumerate(documents):
        documents_list += f"[{i}] {doc.page_content}\n\n"

    try:
        result = grader_chain.invoke({
            "request": request,
            "documents_list": documents_list
        })
        relevant_indices = result.relevant_indices
    except Exception as e:
        print(f"Error in docs_quality_node single-call grading: {e}. Defaulting all as irrelevant.")
        relevant_indices = []

    # Calculate metrics
    no_count = len(documents) - len(relevant_indices)

    # 1-3 no -> yes (mostly relevant)
    if no_count <= 3:
        return {"good_retrieval": "yes"}
    # 7-10 no -> no (mostly irrelevant)
    elif no_count >= 7:
        return {"good_retrieval": "no"}
    # 4-6 no -> ambigious (mixed)
    else:
        return {"good_retrieval": "ambigious"}
