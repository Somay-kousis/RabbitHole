import os 
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from app.courtroom.rag.embedding import get_embedding_model
from langchain_core.documents import Document

load_dotenv()

def get_pinecone_index(index_name: str = "courtroom-knowledge"):
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("PINECONE_API_KEY is not set in environment variables.")

    pc = Pinecone(api_key=api_key)

    if index_name not in pc.list_indexes().names():
        print(f"Creating index '{index_name}'...")
        pc.create_index(
            name=index_name,
            dimension=1024,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        print("Index created successfully.")
        
    return pc.Index(index_name)

def add_documents_to_pinecone(documents: list[Document], index, batch_size: int = 100):
    if not documents:
        print("No documents to add.")
        return
        
    embedding_model = get_embedding_model()
    print(f"Embedding and uploading {len(documents)} chunks to Pinecone in batches of {batch_size}...")
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i : i + batch_size]
        print(f"Processing batch {i//batch_size + 1}...")
        
        # 1. Get embeddings for the batch
        texts = [doc.page_content for doc in batch]
        embeddings = embedding_model.embed_documents(texts)
        
        # 2. Format vectors for Pinecone upsert
        vectors = []
        for idx, (doc, vector) in enumerate(zip(batch, embeddings)):
            chunk_id = f"chunk_{i + idx}"
            vectors.append({
                "id": chunk_id,
                "values": vector,
                "metadata": {
                    "text": doc.page_content,
                    "source": doc.metadata.get("source", "unknown"),
                    "category": doc.metadata.get("category", "unknown"),
                    "doc_type": doc.metadata.get("doc_type", "unknown")
                }
            })
            
        # 3. Upsert to Pinecone
        index.upsert(vectors=vectors)
        
    print("All documents successfully uploaded to Pinecone!")


    
    