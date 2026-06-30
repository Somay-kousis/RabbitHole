from app.courtroom.rag.structure.graph.states import RagState
from app.courtroom.graph.state import CourtroomState
from app.courtroom.rag.structure.function.rewrite_query import rewrite_query
from app.courtroom.rag.structure.function.web_search import web_search
from app.courtroom.rag.structure.function.recompose_web import recompose_web

def incorrect_node(state: RagState):
    """
    Orchestrates the web search RAG pipeline:
    1. Rewrites the RAG request into up to 10 distinct queries.
    2. Runs the queries against Jina Search.
    3. Synthesizes the results into a final_docs brief.
    """
    print(f"\n--- [WEB SEARCH PIPELINE] Squeezing query for web search... ---")
    
    # 1. Rewrite queries
    queries = rewrite_query(state["request"])
    print(f"Generated {len(queries)} search queries:")
    for idx, q in enumerate(queries):
        print(f"  {idx+1}. {q}")
        
    # 2. Execute searches in parallel
    print(f"\nExecuting searches against Jina Search API...")
    search_results = web_search(queries)
    print(f"Retrieved {len(search_results)} unique web documents.")
    
    # 3. Recompose (Synthesize with citation tags)
    print(f"\nSynthesizing brief with source citation tags...")
    final_docs = recompose_web(search_results, state)
    print(f"Synthesis complete.")
    
    return {
        "final_docs": final_docs
    }

if __name__ == "__main__":
    # Test incorrect_node in isolation
    from dotenv import load_dotenv
    load_dotenv()
    
    test_state = {
        "request": "So, for this case regarding privacy violations of Aadhaar data, we need recent Indian Supreme Court rulings on biometric privacy and IT Act 2000."
    }
    
    test_courtstate = {
        "user_input": "Is biometric collection a violation of privacy under IT Act 2000?"
    }
    
    try:
        output = incorrect_node(test_state, test_courtstate)
        print("\n================ FINAL RECOMPOSED BRIEF (WEB) ================")
        print(output["final_docs"][0].page_content)
        print("==============================================================")
    except Exception as e:
        print(f"Error during node execution: {e}")
