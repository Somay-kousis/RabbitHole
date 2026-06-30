import os 
import time
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from app.courtroom.rag.embedding import get_embedding_model
from langchain_core.documents import Document
from pinecone_text.sparse import BM25Encoder 

load_dotenv()

import nltk
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
local_nltk_dir = os.path.join(project_root, "nltk_data")
os.makedirs(local_nltk_dir, exist_ok=True)
nltk.data.path.insert(0, local_nltk_dir)
if not os.path.exists(os.path.join(local_nltk_dir, "corpora", "stopwords")):
    try:
        nltk.download('stopwords', download_dir=local_nltk_dir, quiet=True)
    except Exception as e:
        print(f"Warning: Failed to download nltk stopwords: {e}")

# Initialize the BM25 sparse encoder from local parameters if available
def load_bm25_encoder():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    params_path = os.path.join(current_dir, "bm25_params.json")
    bm25 = BM25Encoder()
    if os.path.exists(params_path):
        bm25.load(params_path)
    else:
        print("Warning: Local BM25 parameters not found at app/courtroom/rag/bm25_params.json. Falling back to default (might download)...")
        try:
            bm25 = BM25Encoder.default()
        except Exception as e:
            print(f"Failed to load default BM25 encoder: {e}. Using dummy fitted encoder.")
            bm25.fit(["biometric Aadhaar right to privacy IT Act 2000 constitutional law precedent"])
    return bm25

bm25_encoder = load_bm25_encoder()


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
            metric="dotproduct",
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
    
    # Check how many vectors already exist in Pinecone
    try:
        stats = index.describe_index_stats()
        existing_count = stats.get("total_vector_count", 0)
        if not isinstance(existing_count, int):
            existing_count = stats.total_vector_count
        print(f"Pinecone index currently contains {existing_count} vectors.")
    except Exception as e:
        print(f"Could not retrieve index stats ({e}). Starting from the beginning.")
        existing_count = 0

    print(f"Embedding and uploading {len(documents)} chunks to Pinecone in batches of {batch_size}...")
    
    for i in range(0, len(documents), batch_size):
        # Skip batches that are already uploaded
        if i + batch_size <= existing_count:
            continue
            
        batch = documents[i : i + batch_size]
        batch_num = i // batch_size + 1
        
        # If we skipped some, let the user know we are resuming
        if i >= existing_count and i - batch_size < existing_count:
            print(f"Resuming upload from batch {batch_num} (chunk {i})...")
            
        print(f"Processing batch {batch_num}...")
        
        # Retry loop for handling network hiccups
        retries = 5
        delay = 2
        
        while retries > 0:
            try:
                # 1. Get dense embeddings for the batch
                texts = [doc.page_content for doc in batch]
                embeddings = embedding_model.embed_documents(texts)
                
                # 2. Get sparse embeddings for the batch
                sparse_embeddings = bm25_encoder.encode_documents(texts)  # <--- Generate sparse vectors
                
                # 3. Format vectors for Pinecone upsert (including sparse_values)
                vectors = []
                for idx, (doc, vector) in enumerate(zip(batch, embeddings)):
                    chunk_id = f"chunk_{i + idx}"
                    vectors.append({
                        "id": chunk_id,
                        "values": vector,
                        "sparse_values": sparse_embeddings[idx],  # <--- Add sparse values here
                        "metadata": {
                            "text": doc.page_content,
                            "source": doc.metadata.get("source", "unknown"),
                            "category": doc.metadata.get("category", "unknown"),
                            "doc_type": doc.metadata.get("doc_type", "unknown")
                        }
                    })
                    
                # 4. Upsert to Pinecone
                index.upsert(vectors=vectors)
                break
                
            except Exception as e:
                retries -= 1
                print(f"Connection error on batch {batch_num}: {e}")
                if retries == 0:
                    raise e
                print(f"Retrying in {delay} seconds ({retries} retries left)...")
                time.sleep(delay)
                delay *= 2
                
        time.sleep(1)
        
    print("All documents successfully uploaded to Pinecone!")
