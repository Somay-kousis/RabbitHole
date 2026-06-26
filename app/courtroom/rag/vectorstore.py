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

