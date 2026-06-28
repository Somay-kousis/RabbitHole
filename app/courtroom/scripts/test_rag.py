import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("Project root:", current_dir)

print("Attempting to compile RAG Graph...")
try:
    from app.courtroom.rag.structure.graph.graph import graph as rag_graph
    compiled_rag = rag_graph.compile()
    print("✓ RAG Graph compiled successfully!")
except Exception as e:
    print("✗ RAG Graph compilation failed!")
    import traceback
    traceback.print_exc()

print("\nAttempting to compile Courtroom Graph...")
try:
    from app.courtroom.graph.builder import courtroom_app
    print("✓ Courtroom Graph compiled successfully!")
except Exception as e:
    print("✗ Courtroom Graph compilation failed!")
    import traceback
    traceback.print_exc()
