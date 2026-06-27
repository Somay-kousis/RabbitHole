import os
from dotenv import load_dotenv
from app.courtroom.rag.embedding import get_embedding_model
from app.courtroom.rag.vectorstore import get_pinecone_index
from langchain_core.documents import Document
from langchain_community.retrievers import PineconeHybridSearchRetriever
from pinecone_text.sparse import BM25Encoder

load_dotenv()

# Get Pinecone API key
pinecone_api = os.getenv("PINECONE_API_KEY")

# Initialize the BM25 sparse encoder
bm25_encoder = BM25Encoder.default()

def search_documents(query: str, k: int = 4) -> list[Document]:
    """
    Searches the Pinecone vector store using hybrid (dense + sparse) search.
    """
    index = get_pinecone_index()
    embedding_model = get_embedding_model()
    
    # 1. Initialize the LangChain Hybrid Retriever
    retriever = PineconeHybridSearchRetriever(
        embeddings=embedding_model,
        sparse_encoder=bm25_encoder,
        index=index
    )
    
    # Configure it to retrieve 'k' results
    retriever.k = k
    
    # 2. Invoke the hybrid search
    return retriever.invoke(query)

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
