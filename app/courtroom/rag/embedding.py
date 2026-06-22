from langchain_community.embeddings import JinaEmbeddings
import os

def get_embedding_model():
    """
    Returns the configured embedding model for the RAG pipeline.
    Requires JINA_API_KEY environment variable.
    """
    jina_api_key = os.environ.get("JINA_API_KEY")
    if not jina_api_key:
        print("Warning: JINA_API_KEY not found in environment variables.")
        
    return JinaEmbeddings(
        jina_api_key=jina_api_key,
        model_name="jina-embeddings-v2-base-en"
    )
