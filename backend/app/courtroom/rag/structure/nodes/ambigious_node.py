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
from app.courtroom.rag.structure.nodes.supported_node import support_chain
from app.courtroom.rag.structure.nodes.partial_supported_node import partial_chain

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
    
    # Run the self-correction loop up to 5 times for the local brief
    local_state = dict(state)
    local_state["turn"] = 0
    local_state["why_loop"] = ""
    local_state["is_sup"] = False
    
    docs_text = "\n\n---\n\n".join([doc.page_content for doc in filtered_local]) if filtered_local else ""
    local_brief_docs = []
    
    while local_state["turn"] < 5:
        local_brief_docs = recompose(filtered_local, local_state)
        if not local_brief_docs:
            break
            
        summary_text = local_brief_docs[0].page_content
        
        # Audit the generated local brief
        audit_result = support_chain.invoke({
            "documents": docs_text,
            "summary": summary_text
        })
        
        if audit_result.is_supported:
            print(f"[Ambiguous: Local Branch] Local brief is 100% supported on turn {local_state['turn'] + 1}.")
            local_state["is_sup"] = True
            break
        else:
            local_state["turn"] += 1
            local_state["why_loop"] = audit_result.critique
            print(f"[Ambiguous: Local Branch] Local brief check failed on turn {local_state['turn']}. Critique: {audit_result.critique}")
            
    # If after 5 turns it is still not fully supported, run partial_chain to tag the local brief
    if not local_state["is_sup"] and local_brief_docs:
        print("[Ambiguous: Local Branch] Local brief not 100% supported after 5 turns. Running partial audit to segregate claims...")
        summary_text = local_brief_docs[0].page_content
        partial_report = partial_chain.invoke({
            "documents": docs_text,
            "summary": summary_text
        })
        local_brief = partial_report
    else:
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
    
    from langchain_core.documents import Document
    test_state = {
        "request": "So, for this case regarding privacy violations of Aadhaar data, we need recent Indian Supreme Court rulings on biometric privacy and IT Act 2000.",
        "documents": [
            Document(
                page_content="Under Section 33 of the Aadhaar Act, disclosure of identity information or authentication records can only be made pursuant to an order of a court not inferior to that of a District Judge.",
                metadata={"source": "Aadhaar Act"}
            )
        ]
    }
    
    test_courtstate = {
        "user_input": "Is biometric collection a violation of privacy under IT Act 2000?"
    }
    
    try:
        output = ambigious_node(test_state)
        print("\n================ FINAL MERGED BRIEF (AMBIGUOUS) ================")
        print(output["final_docs"][0].page_content)
        print("================================================================")
    except Exception as e:
        print(f"Error during node execution: {e}")
