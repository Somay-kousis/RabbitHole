import os
import sys

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.courtroom.graph.builder import courtroom_app

def run_test():
    print("================ STARTING COURTROOM GRAPH TEST RUN ================")
    
    # Initialize a mock state for testing
    initial_state = {
        "user_input": "Is biometric collection under Aadhaar a violation of the Right to Privacy under Article 21 and the IT Act 2000?",
        "turn_count": 1,
        "perspectives": [
            {
                "id": 1, 
                "role": "State Advocate defending Aadhaar for national security and public benefits distribution", 
                "active": True,
                "background_motives": "Protect national identity systems and state authority."
            },
            {
                "id": 2, 
                "role": "Privacy Rights Activist advocating for absolute individual sovereignty", 
                "active": True,
                "background_motives": "Prevent government surveillance and preserve individual autonomy."
            }
        ],
        "judiciary_corrupt": False
    }
    
    config = {"configurable": {"thread_id": "test_thread"}}
    
    # Stream the graph execution
    try:
        for event in courtroom_app.stream(initial_state, config=config):
            for node_name, state_update in event.items():
                print(f"\n[EVENT] Node Finished: {node_name}")
                
                # Check for critical state changes to print out
                if "final_docs" in state_update and state_update["final_docs"]:
                    print("\n--- RAG Brief Generated ---")
                    print(state_update["final_docs"][0].page_content[:500] + "...")
                
                if "perspectives" in state_update:
                    for p in state_update["perspectives"]:
                        if "public_statement" in p:
                            print(f"\n--- Perspective {p['id']} Statement ({p['role']}) ---")
                            print(p["public_statement"])
                
                if "judiciary" in state_update:
                    print("\n--- Judiciary Verdict & Reasoning ---")
                    print(f"Reasoning: {state_update['judiciary'].get('reasoning')[:300]}...")
                    print(f"Verdict: {state_update['judiciary'].get('verdict')}")
                    
        print("\nGraph successfully completed execution up to the HITL interrupt.")
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Graph execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
