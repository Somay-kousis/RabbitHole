import os
import time
from langchain_neo4j import Neo4jVector
from langchain_core.documents import Document
from .embedding import get_embedding_model

def get_vector_store():
    """
    Initializes and returns the Neo4j vector store if the index exists.
    Returns None if the index has not been created yet.
    """
    embedding_model = get_embedding_model()
    
    neo4j_uri = os.environ.get("NEO4J_URI")
    neo4j_username = os.environ.get("NEO4J_USERNAME")
    neo4j_password = os.environ.get("NEO4J_PASSWORD")
    
    try:
        vector_store = Neo4jVector.from_existing_index(
            embedding=embedding_model,
            url=neo4j_uri,
            username=neo4j_username,
            password=neo4j_password,
            index_name="courtroom_knowledge",
            node_label="Chunk",
            text_node_property="text",
            embedding_node_property="embedding",
        )
        return vector_store
    except ValueError:
        # Index doesn't exist yet, we will create it on the first batch insertion
        return None

def add_documents_to_store(documents: list[Document], vector_store, batch_size: int = 25):
    """
    Adds split documents to the vector store in batches with a delay to avoid rate limits.
    If vector_store is None, it creates the index using the first batch.
    """
    if not documents:
        print("No documents to add.")
        return
        
    neo4j_uri = os.environ.get("NEO4J_URI")
    neo4j_username = os.environ.get("NEO4J_USERNAME")
    neo4j_password = os.environ.get("NEO4J_PASSWORD")
    embedding_model = get_embedding_model()
        
    print(f"Adding {len(documents)} chunks to the Neo4j vector store in batches of {batch_size}...")
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        print(f"Uploading batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size} ({len(batch)} chunks)...")
        
        # Add a retry loop for Neo4j connection timeouts
        retries = 3
        while retries > 0:
            try:
                if vector_store is None:
                    # First batch ever: create the database index with from_documents
                    vector_store = Neo4jVector.from_documents(
                        batch,
                        embedding_model,
                        url=neo4j_uri,
                        username=neo4j_username,
                        password=neo4j_password,
                        index_name="courtroom_knowledge",
                        node_label="Chunk",
                        text_node_property="text",
                        embedding_node_property="embedding",
                    )
                else:
                    # Subsequent batches
                    vector_store.add_documents(batch)
                break # Success, break out of retry loop
            except Exception as e:
                print(f"Connection error: {e}. Retrying in 30 seconds...")
                retries -= 1
                time.sleep(30)
                # If we fail to connect, we can force a new connection by resetting vector_store
                # if it's a persistent timeout issue. But Langchain handles reconnection usually.
                if retries == 0:
                    raise e
        
        # Wait 10 seconds between batches to respect rate limits
        if i + batch_size < len(documents):
            print("Waiting 10 seconds to avoid rate limit...")
            time.sleep(10)
            
    print("Documents successfully added to the Neo4j vector store.")
