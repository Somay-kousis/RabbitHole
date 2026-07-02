import os
import json
from app.courtroom.models.llm import RETRIEVER_MODEL
from app.courtroom.rag.structure.graph.states import RagState
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

# Clerk prompt: analyzes query from all POVs dynamically and maps to available documents
request_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a senior legal clerk assisting a courtroom agent.
    
    Your job is to analyze the case query dynamically from all possible legal, human, ecological, commercial, and constitutional dimensions. 
    Brainstorm the diverse, real-world problems, disputes, and struggles people might face under every possible point of view relative to this query.
    Do not limit yourself to specific domains; explore all facets of the issue.
    
    Here is the case we are currently proceeding with:
    {case}
    
    Here are the ONLY legal documents and cases available in our database:
    
    LAWS AVAILABLE:
    {available_laws}
    
    LANDMARK CASES AVAILABLE:
    {available_cases}
    
    Based on your multi-dimensional brainstorming of the issue, write a concise summary of the case and select all available documents needed to address these problems from every possible perspective. You must respond in this exact format:
    'So, for this case [brief summary of the dispute and its multi-perspective issues], we need: [comma-separated list of document titles]'"""),
])

request_chain = request_prompt | RETRIEVER_MODEL | StrOutputParser()

from app.courtroom.utils.progress import update_progress

def level_one_refine_node(state: RagState, config=None):
    update_progress(config, "🏛️ Clerk is mapping query to available laws & landmark cases...")
    # 1. Invoke the clerk chain to synthesize the case and find file names
    req_output = request_chain.invoke({
        "case": state["query"],
        "available_laws": laws_str,
        "available_cases": cases_str
    })
    
    # 2. Return updates to the state
    return {
        "request": req_output,
        "turn": 0
    }
