#!/usr/bin/env python3
import os
import sys

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.courtroom.rag.document_loader import load_documents, split_documents
from pinecone_text.sparse import BM25Encoder

def main():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "app", "courtroom", "data")
    print(f"Loading documents from {data_dir}...")
    raw_docs = load_documents(data_dir)
    chunks = split_documents(raw_docs)
    
    if not chunks:
        print("No documents or chunks found to fit BM25 on. Creating a dummy fit.")
        texts = ["biometric Aadhaar right to privacy IT Act 2000 constitutional law precedent"]
    else:
        print(f"Loaded {len(chunks)} chunks.")
        texts = [doc.page_content for doc in chunks]
        
    print("Fitting BM25Encoder...")
    bm25 = BM25Encoder()
    bm25.fit(texts)
    
    out_path = os.path.join(os.path.dirname(__file__), "..", "app", "courtroom", "rag", "bm25_params.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    print(f"Saving BM25 parameters to {out_path}...")
    bm25.dump(out_path)
    print("BM25 parameters fitted and saved successfully!")

if __name__ == "__main__":
    main()
