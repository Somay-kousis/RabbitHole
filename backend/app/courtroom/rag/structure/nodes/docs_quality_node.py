from typing import Literal
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from app.courtroom.models.llm import RETRIVER_LITE_MODEL
from app.courtroom.rag.structure.graph.states import RagState

class GoodRetrieve(BaseModel):
    good_retrieval: Literal["yes", "no"]

grader_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are given a document chunk and a request. Decide if the document is relevant to the request. Reply with only 'yes' or 'no'. No explanation."),
    ("user", "Request: {request}\n\nDocument: {document}")
])

grader_chain = grader_prompt | RETRIVER_LITE_MODEL.with_structured_output(GoodRetrieve)

def docs_quality_node(state: RagState):
    documents = state["documents"]
    request = state["request"]

    no_count = 0
    for doc in documents:
        result = grader_chain.invoke({
            "request": request,
            "document": doc.page_content
        })
        if result.good_retrieval == "no":
            no_count += 1

    # 1-3 no -> yes (mostly relevant)
    if no_count <= 3:
        return {"good_retrieval": "yes"}
    # 7-10 no -> no (mostly irrelevant)
    elif no_count >= 7:
        return {"good_retrieval": "no"}
    # 4-6 no -> ambigious (mixed)
    else:
        return {"good_retrieval": "ambigious"}
