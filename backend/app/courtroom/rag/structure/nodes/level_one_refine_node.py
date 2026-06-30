import os
import json
from pydantic import BaseModel
from app.courtroom.models.llm import RETRIVER_LITE_MODEL, RETRIEVER_MODEL
from app.courtroom.rag.structure.graph.states import RagState
from app.courtroom.graph.state import CourtroomState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

current_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_dir, "law.json")
try:
    with open(json_path, "r") as f:
        available_docs = json.load(f)
except Exception:
    available_docs = {"laws": {}, "cases": {}}

# Format lists for the prompt
laws_str = ""
for category, docs in available_docs.get("laws", {}).items():
    laws_str += f"- {category}: {', '.join(docs)}\n"

cases_str = ""
for category, docs in available_docs.get("cases", {}).items():
    cases_str += f"- {category}: {', '.join(docs)}\n"

class needed(BaseModel):
    needed: bool

# 1. Clerk prompt: summarizes dispute & lists exactly which available files are needed
request_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a legal clerk assisting a courtroom agent.
    
    Here is the case we are currently proceeding with:
    {case}
    
    Here are the ONLY legal documents and cases available in our database:
    
    LAWS AVAILABLE:
    {available_laws}
    
    LANDMARK CASES AVAILABLE:
    {available_cases}
    
    Write a concise summary of the case issue and select which available documents are needed. You must respond in this exact format:
    'So, for this case [brief summary of the dispute], we need: [comma-separated list of document titles]'"""),
])

# 2. Decision prompt: checks if retrieval is needed or not
needed_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are being provided a user's query, you have to decide whether the query needs retrieval for laws and cases documents of India or not, strictly reply with True or False"),
    ("user", "{query} for my query I need {request}")
])

request_chain = request_prompt | RETRIEVER_MODEL | StrOutputParser()
needed_chain = needed_prompt | RETRIVER_LITE_MODEL.with_structured_output(needed)

def level_one_refine_node(state: RagState):
    # 1. Invoke the clerk chain to synthesize the case and find file names
    req_output = request_chain.invoke({
        "case": state["query"],
        "available_laws": laws_str,
        "available_cases": cases_str
    })
    
    # 2. Use the output in the decision chain
    is_needed = needed_chain.invoke({
        "query": state["query"],
        "request": req_output
    })
    
    # 3. Return updates to the state
    return {
        "request": req_output,
        "retriever_needed": is_needed.needed,
        "turn": 0
    }

