import os
from dotenv import load_dotenv
from app.courtroom.rag.embedding import get_embedding_model
from app.courtroom.rag.vectorstore import get_pinecone_index
from langchain_core.documents import Document
from langchain_community.retrievers import PineconeHybridSearchRetriever
from pinecone_text.sparse import BM25Encoder
import requests

load_dotenv()

# Get Pinecone API key
pinecone_api = os.getenv("PINECONE_API_KEY")

# Initialize the BM25 sparse encoder

bm25_encoder = BM25Encoder.default()

def rerank_documents(query: str, documents: list[Document], top_n: int = 4) -> list[Document]:
    """
    Reranks a list of documents against a query using Jina's Reranker API.
    """
    if not documents:
        return []
        
    jina_api_key = os.environ.get("JINA_API_KEY")
    if not jina_api_key:
        print("Warning: JINA_API_KEY not found. Skipping reranking.")
        return documents[:top_n]
        
    headers = {
        "Authorization": f"Bearer {jina_api_key}",
        "Content-Type": "application/json"
    }
    
    # Extract raw text from the documents to send to Jina
    doc_texts = [doc.page_content for doc in documents]
    
    payload = {
        "model": "jina-reranker-v2-base-multilingual",
        "query": query,
        "documents": doc_texts,
        "top_n": top_n
    }
    
    try:
        response = requests.post(
            "https://api.jina.ai/v1/rerank",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        
        # Build the new list of Documents sorted by reranker relevance
        reranked_docs = []
        for result in results:
            idx = result["index"]
            orig_doc = documents[idx]
            
            # Store the reranker score in metadata for debugging/evals
            orig_doc.metadata["relevance_score"] = result["relevance_score"]
            reranked_docs.append(orig_doc)
            
        return reranked_docs
        
    except Exception as e:
        print(f"Reranking failed: {e}. Falling back to initial search order.")
        return documents[:top_n]

def search_documents(query: str, top_k: int = 10) -> list[Document]:
    """
    Searches the Pinecone vector store using hybrid (dense + sparse) search and refines with a reranker.
    """
    index = get_pinecone_index()
    embedding_model = get_embedding_model()
    
    retriever = PineconeHybridSearchRetriever(
        embeddings=embedding_model,
        sparse_encoder=bm25_encoder,
        index=index
    )
    
    # 1. Fetch a large pool of 50 documents internally for the wide net
    retriever.k = 50
    initial_docs = retriever.invoke(query)
    
    # 2. Rerank and shrink down to the requested 'top_k' (default 4)
    reranked_docs = rerank_documents(query, initial_docs, top_n=top_k)
    
    return reranked_docs

if __name__ == "__main__":
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
