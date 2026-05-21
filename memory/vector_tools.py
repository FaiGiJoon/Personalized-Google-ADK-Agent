import logging
import os
from typing import List, Dict, Any
from pathlib import Path

# Advanced RAG dependencies
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from skills.models import VectorQuerySchema, DocumentIndexSchema

logger = logging.getLogger("CasperC2.Vector")

# Global variables for the production-ready RAG
MODEL_NAME = "all-MiniLM-L6-v2"
INDEX_PATH = Path(__file__).parent / "faiss_index.bin"
DOCS_PATH = Path(__file__).parent / "indexed_docs.txt"

# Lazy initialization of the embedding model
_model = None

def get_model():
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def query_technical_docs(query_data: VectorQuerySchema) -> List[Dict[str, Any]]:
    """
    Advanced Vector Search (RAG) tool using FAISS.
    Allows Casper to ask questions about Snort rules, GAMEBOY_ANALYSIS.md, etc.
    """
    query = query_data.query
    collection = query_data.collection
    logger.info(f"Querying FAISS database for: {query} in collection: {collection}")

    if not INDEX_PATH.exists() or not DOCS_PATH.exists():
        logger.warning("FAISS index or docs file not found. Returning mock results.")
        return [{"source": "system", "content": "No documents indexed yet.", "relevance": 0.0}]

    try:
        # Load index and documents
        index = faiss.read_index(str(INDEX_PATH))
        with open(DOCS_PATH, "r") as f:
            documents = [line.strip().split("|", 1) for line in f.readlines()]

        # Generate query embedding
        model = get_model()
        query_embedding = model.encode([query]).astype('float32')

        # Search the index
        k = 3  # Number of results to return
        distances, indices = index.search(query_embedding, k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(documents):
                source, content = documents[idx]
                results.append({
                    "source": source,
                    "content": content,
                    "relevance": float(1 / (1 + dist))  # Simplified relevance score
                })
        return results
    except Exception as e:
        logger.error(f"Error during vector search: {e}")
        return [{"error": str(e)}]

def index_document(doc_data: DocumentIndexSchema) -> str:
    """Adds a document to the production-ready FAISS index."""
    filepath = doc_data.filepath

    # Ensure filepath is treated relative to project root if it's not absolute
    if not os.path.isabs(filepath):
        project_root = Path(__file__).resolve().parent.parent
        filepath = str(project_root / filepath)

    if not os.path.exists(filepath):
        return f"Error: File {filepath} not found."

    try:
        logger.info(f"Indexing document: {filepath}")

        with open(filepath, 'r') as f:
            content = f.read()

        # Split content into chunks (simple paragraph splitting for now)
        chunks = [c.strip() for c in content.split("\n\n") if len(c.strip()) > 20]

        if not chunks:
            return f"No indexable content found in {filepath}."

        model = get_model()
        embeddings = model.encode(chunks).astype('float32')

        # Load existing index or create a new one
        if INDEX_PATH.exists():
            index = faiss.read_index(str(INDEX_PATH))
        else:
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)

        index.add(embeddings)

        # Save index and document map
        faiss.write_index(index, str(INDEX_PATH))

        with open(DOCS_PATH, "a") as f:
            for chunk in chunks:
                # Replace newlines in chunk to keep it on one line in the text file
                clean_chunk = chunk.replace("\n", " ")
                f.write(f"{os.path.basename(filepath)}|{clean_chunk}\n")

        return f"Successfully indexed {len(chunks)} chunks from {filepath} into the FAISS store."
    except Exception as e:
        logger.error(f"Error during document indexing: {e}")
        return f"Error indexing {filepath}: {e}"
