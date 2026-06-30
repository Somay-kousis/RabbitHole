import os
import glob
import json
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_documents(data_dir: str) -> list[Document]:
    """
    Loads all .txt, .json, and .jsonl documents from the given data directory.
    """
    documents = []

    patterns = ["*.txt", "*.json", "*.jsonl"]
    filepaths = []
    
    for pattern in patterns:
        search_pattern = os.path.join(data_dir, "**", pattern)
        filepaths.extend(glob.glob(search_pattern, recursive=True))
    
    for filepath in filepaths:
        try:
            # Extract category and type (cases/laws) from the path
            parts = filepath.split(os.sep)
            metadata = {"source": filepath}
            try:
                data_idx = parts.index("data")
                if len(parts) > data_idx + 2:
                    metadata["doc_type"] = parts[data_idx + 1]
                    metadata["category"] = parts[data_idx + 2]
            except ValueError:
                pass

            if filepath.endswith('.txt'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                doc = Document(page_content=content, metadata=metadata.copy())
                documents.append(doc)
                
            elif filepath.endswith('.jsonl'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f):
                        if not line.strip(): continue
                        try:
                            data = json.loads(line)
                            line_metadata = metadata.copy()
                            line_metadata["line_number"] = i
                            doc = Document(page_content=json.dumps(data, indent=2), metadata=line_metadata)
                            documents.append(doc)
                        except json.JSONDecodeError:
                            pass
                            
            elif filepath.endswith('.json'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        doc = Document(page_content=json.dumps(data, indent=2), metadata=metadata.copy())
                        documents.append(doc)
                    except json.JSONDecodeError:
                        pass
            
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            
    return documents

def split_documents(documents: list[Document]) -> list[Document]:
    """
    Splits documents into smaller chunks for embedding.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    return text_splitter.split_documents(documents)

if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    docs = load_documents(base_dir)
    print(f"Successfully loaded {len(docs)} documents.")
    
    split_docs = split_documents(docs)
    print(f"Split into {len(split_docs)} chunks.")
    if split_docs:
        print("Example chunk metadata:", split_docs[0].metadata)
