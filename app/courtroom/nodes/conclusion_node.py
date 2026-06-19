from app.courtroom.models.llm import CONCLUSION_MODEL
from app.courtroom.graph.state import CourtroomState
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from app.courtroom.prompts.conclusion_prompt import CONCLUSION_PROMPT

class ConclusionOutput(BaseModel):
    conclusion: str


conclusion_prompt = ChatPromptTemplate.from_messages([
    ("system", CONCLUSION_PROMPT),
    ("human", "Courtroom State:\n{state}")
])

conclusion_chain = (
    conclusion_prompt
    | CONCLUSION_MODEL.with_structured_output(ConclusionOutput)
)


def conclusion_node(state: CourtroomState):
    result = conclusion_chain.invoke({
        "state": state
    })

    return {
        "conclusion": result.conclusion
    }
