from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from app.courtroom.models.llm import RETRIEVER_MODEL
from app.courtroom.rag.structure.graph.states import RagState
from app.courtroom.graph.state import CourtroomState

# Import local pipeline functions
from app.courtroom.rag.structure.function.decompose import decompose
from app.courtroom.rag.structure.function.filter import filter_docs
from app.courtroom.rag.structure.function.recompose import recompose

# Import web pipeline functions
from app.courtroom.rag.structure.function.rewrite_query import rewrite_query
from app.courtroom.rag.structure.function.web_search import web_search
from app.courtroom.rag.structure.function.recompose_web import recompose_web

# Merger Prompt
merge_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a senior legal editor. Your job is to merge two legal research briefs into a single, unified legal brief for the courtroom.
    
    You are given:
    1. An OFFICIAL legal brief (derived from local database documents).
    2. An UNOFFICIAL legal brief (derived from web search results, containing source tags like <TimesOfIndia>, <BarAndBench>, <@username_x_post>, etc.).
    
    CRITICAL RULES:
    - Merge the findings logically by topic or legal issue.
    - Every claim, provision, or case derived from the OFFICIAL brief must be clearly tagged with [OFFICIAL].
    - Every claim, event, or citation derived from the UNOFFICIAL brief must retain its original source tag (e.g. <TimesOfIndia>, <@username_x_post>) and be clearly tagged with [UNOFFICIAL].
    - Maintain a highly professional and legal tone. Do not invent any facts."""),
    ("user", "OFFICIAL BRIEF:\n{local_brief}\n\nUNOFFICIAL BRIEF:\n{web_brief}")
])

merge_chain = merge_prompt | RETRIEVER_MODEL | StrOutputParser()

def ambigious_node(state: RagState):
    """
    Orchestrates the ambiguous RAG pipeline:
    1. Runs the Local RAG pipeline (Decompose -> Filter -> Recompose).
    2. Runs the Web RAG pipeline (Rewrite -> Web Search -> Recompose Web).
    3. Merges both summaries, tagging official vs. unofficial web sources.
    """
    print(f"\n--- [AMBIGIOUS RAG PIPELINE] Starting parallel Local + Web RAG... ---")
    
    # 1. RUN LOCAL PIPELINE
    print("\n[Ambiguous: Local Branch] Executing local document RAG...")
    decomposed_local = decompose(state)
    filtered_local = filter_docs(decomposed_local, state)
    local_brief_docs = recompose(filtered_local, state)
    local_brief = local_brief_docs[0].page_content if local_brief_docs else "No local legal context found."
    
    # 2. RUN WEB PIPELINE
    print("\n[Ambiguous: Web Branch] Executing web search RAG...")
    web_queries = rewrite_query(state["request"])
    web_results = web_search(web_queries)
    web_brief_docs = recompose_web(web_results, state)
    web_brief = web_brief_docs[0].page_content if web_brief_docs else "No web search context found."
    
    # 3. MERGE AND TAG
    print("\n[Ambiguous: Merger] Merging official and unofficial context briefs...")
    merged_brief = merge_chain.invoke({
        "local_brief": local_brief,
        "web_brief": web_brief
    })
    print("Merger complete.")
    
    final_doc = Document(
        page_content=merged_brief,
        metadata={
            "type": "recomposed_merged_brief",
            "local_docs_count": len(filtered_local),
            "web_sources_count": len(web_results)
        }
    )
    
    # Save the intermediate pipeline stages in state for auditing
    return {
        "decomposed_docs": decomposed_local,
        "filtered_docs": filtered_local,
        "final_docs": [final_doc]
    }

if __name__ == "__main__":
    # Test ambigious_node in isolation
    from dotenv import load_dotenv
    load_dotenv()
    
    test_state = {
        "request": "So, for this case regarding privacy violations of Aadhaar data, we need recent Indian Supreme Court rulings on biometric privacy and IT Act 2000."
    }
    
    test_courtstate = {
        "user_input": "Is biometric collection a violation of privacy under IT Act 2000?"
    }
    
    try:
        output = ambigious_node(test_state, test_courtstate)
        print("\n================ FINAL MERGED BRIEF (AMBIGUOUS) ================")
        print(output["final_docs"][0].page_content)
        print("================================================================")
    except Exception as e:
        print(f"Error during node execution: {e}")
