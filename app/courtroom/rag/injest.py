import os
from app.courtroom.rag.document_loader import load_documents, split_documents
from app.courtroom.rag.vectorstore import get_pinecone_index, add_documents_to_pinecone

def main():
    # 1. Load files from disk
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    print(f"Loading documents from {data_dir}...")
    raw_docs = load_documents(data_dir)
    
    # 2. Split them into chunks
    chunks = split_documents(raw_docs)
    
    # 3. Connect and Upload
    index = get_pinecone_index()
    add_documents_to_pinecone(chunks, index)

if __name__ == "__main__":
    main()
