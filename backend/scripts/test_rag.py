#!/usr/bin/env python3
import os
import sys

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.courtroom.rag.structure.graph.graph import graph as rag_graph

def test_rag_pipeline(query: str):
    print(f"\n================ STARTING RAG SUB-GRAPH TEST RUN ================")
    print(f"Query: {query}\n")
    
    # Initialize state for RAG sub-graph
    initial_state = {
        "query": query,
        "turn": 0,
        "why_loop": "",
        "is_sup": False,
        "good_retrieval": "yes",
        "retriever_needed": True
    }
    
    # Compile the RAG sub-graph
    compiled_rag = rag_graph.compile()
    
    # Stream the graph execution node-by-node
    try:
        for event in compiled_rag.stream(initial_state):
            for node_name, state_update in event.items():
                print(f"[EVENT] Node Finished: {node_name}")
                
                # Print key state updates if they occurred in the node
                if "request" in state_update:
                    print(f"  -> Clerk synthesized request query: {state_update['request']}")
                if "retriever_needed" in state_update:
                    print(f"  -> Retriever needed: {state_update['retriever_needed']}")
                if "documents" in state_update:
                    docs = state_update["documents"]
                    print(f"  -> Retrieved {len(docs)} documents.")
                if "decomposed_docs" in state_update:
                    print(f"  -> Decomposed into sub-queries.")
                if "filtered_docs" in state_update:
                    print(f"  -> Filtered down to {len(state_update['filtered_docs'])} relevant chunks.")
                if "is_sup" in state_update:
                    status = "Passed" if state_update["is_sup"] else "Failed"
                    print(f"  -> Self-RAG Support Check: {status}")
                if "final_docs" in state_update and state_update["final_docs"]:
                    print("\n--- RAG Brief Generated ---")
                    print(state_update["final_docs"][0].page_content)
                    print("---------------------------\n")
                    
        print("RAG Pipeline successfully completed execution.")
    except Exception as e:
        print(f"\n[CRITICAL ERROR] RAG execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Use a default test query or take one from command line arguments
    if len(sys.argv) > 1:
        test_query = " ".join(sys.argv[1:])
    else:
        test_query = "Is biometric collection under Aadhaar a violation of the Right to Privacy under Article 21 and the IT Act 2000?"
        
    test_rag_pipeline(test_query)
