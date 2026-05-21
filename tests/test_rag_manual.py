import sys
import os
from pathlib import Path

# Ensure project root is in sys.path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from memory.vector_tools import index_document, query_technical_docs
from skills.models import DocumentIndexSchema, VectorQuerySchema

def test_rag():
    print("Testing FAISS RAG implementation...")

    # Index a sample file
    sample_file = "README.md"
    if not os.path.exists(sample_file):
        with open(sample_file, "w") as f:
            f.write("# Sample Document\n\nThis is a sample document for testing Casper C2's new FAISS-based memory system.")

    print(f"Indexing {sample_file}...")
    index_result = index_document(DocumentIndexSchema(filepath=sample_file))
    print(f"Index Result: {index_result}")

    # Query the index
    query = "FAISS memory system"
    print(f"Querying for: '{query}'...")
    query_result = query_technical_docs(VectorQuerySchema(query=query))
    print(f"Query Result: {query_result}")

    if any(query in res.get("content", "") for res in query_result):
        print("SUCCESS: RAG functioning as expected.")
    else:
        print("WARNING: Could not find query content in results. Check indexing logic.")

if __name__ == "__main__":
    test_rag()
