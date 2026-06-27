from app.courtroom.rag.embedding import get_embedding_model
from app.courtroom.rag.vectorstore import get_pinecone_index
from langchain_core.documents import Document

def search_documents(query:str, k: int = 4) -> list[Document]:
    """
    Searches the Pinecone vector store for documents similar to the query.
    Returns the top 'k' matching documents as LangChain Document objects.
    """

    index = get_pinecone_index()
    embedding_model = get_embedding_model()
    query_vector = embedding_model.embed_query(query)

    response = index.query(
        vector=query_vector,
        top_k=k,
        include_metadata=True
    )

    documents = []
    for match in response.get("matches", []):
        metadata = match.get("metadata", {})
        
        # Pop the text out of metadata so it isn't duplicated in the metadata dict
        text = metadata.pop("text", "")
        
        doc = Document(
            page_content=text,
            metadata=metadata
        )
        documents.append(doc)
        
    return documents    

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

