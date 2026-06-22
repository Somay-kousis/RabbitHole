import os
import sys

# Add project root to sys.path so we can run this standalone
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, ".env"))

from app.courtroom.rag.vector_store import get_vector_store

def search_documents(query: str, k: int = 4):
    """
    Searches the Neo4j vector store for documents similar to the query.
    Returns the top 'k' matching documents.
    """
    vector_store = get_vector_store()
    
    if vector_store is None:
        raise ValueError("Vector store is not initialized. Make sure the database exists.")
        
    print(f"Executing search: '{query}'...")
    results = vector_store.similarity_search(query, k=k)
    return results

if __name__ == "__main__":
    # A quick test to verify retrieval is working
    test_query = "What is the rarest of rare doctrine?"
    
    try:
        results = search_documents(test_query)
        print(f"\nFound {len(results)} results.\n")
        
        for i, doc in enumerate(results):
            print(f"--- Result {i+1} ---")
            print(f"Source: {doc.metadata.get('source', 'Unknown')}")
            print(f"Category: {doc.metadata.get('category', 'Unknown')}")
            print(f"Preview: {doc.page_content[:250]}...\n")
            
    except Exception as e:
        print(f"Error during retrieval: {e}")
