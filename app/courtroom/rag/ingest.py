import os
import sys
from dotenv import load_dotenv

# Add project root to sys.path so we can import app.*
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables
load_dotenv(os.path.join(project_root, ".env"))

from app.courtroom.rag.document_loader import load_documents, split_documents
from app.courtroom.rag.vector_store import get_vector_store, add_documents_to_store

def main():
    print("Starting ingestion pipeline...")
    
    # 1. Load Documents
    base_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    print(f"Loading documents from {base_dir}...")
    docs = load_documents(base_dir)
    print(f"Loaded {len(docs)} documents.")
    
    if not docs:
        print("No documents found. Exiting.")
        return
        
    # 2. Split Documents
    print("Splitting documents into chunks...")
    split_docs = split_documents(docs)
    print(f"Created {len(split_docs)} chunks.")
    
    # 3 & 4. Get Vector Store and Add Documents
    print("Connecting to vector store and computing embeddings...")
    vector_store = get_vector_store()
    add_documents_to_store(split_docs, vector_store)
    
    print("Ingestion pipeline complete! Data is now embedded and stored locally.")

if __name__ == "__main__":
    main()
