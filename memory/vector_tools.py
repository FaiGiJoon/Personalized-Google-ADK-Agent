import logging
import os
import json
from typing import List, Dict, Any
from pathlib import Path

# Advanced RAG dependencies with explicit checks
DEPENDENCIES_INSTALLED = False
try:
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer
    DEPENDENCIES_INSTALLED = True
except ImportError:
    pass

from skills.models import VectorQuerySchema, DocumentIndexSchema

logger = logging.getLogger("CasperC2.Vector")

if not DEPENDENCIES_INSTALLED:
    logger.error("Missing core RAG dependencies (faiss, numpy, or sentence_transformers).")

# Global variables for the production-ready RAG
MODEL_NAME = "all-MiniLM-L6-v2"
INDEX_PATH = Path(__file__).parent / "faiss_index.bin"
DOCS_PATH = Path(__file__).parent / "indexed_docs.txt"

# Legacy cleanup: ensure indexed_docs is JSONL
if DOCS_PATH.exists():
    try:
        with open(DOCS_PATH, "r") as f:
            first_line = f.readline()
            if first_line and not first_line.strip().startswith("{"):
                logger.warning("Legacy pipe-separated indexed_docs.txt found. Purging for clean JSONL transition.")
                DOCS_PATH.unlink()
                if INDEX_PATH.exists():
                    INDEX_PATH.unlink()
    except Exception as e:
        logger.error(f"Error during legacy cleanup: {e}")

# Lazy initialization of the embedding model and FAISS index
_model = None
_index = None
_documents = []
_last_index_mtime = 0

def get_model():
    global _model
    if not DEPENDENCIES_INSTALLED:
        raise ImportError("FAISS or SentenceTransformer not installed.")
    if _model is None:
        logger.info(f"Loading embedding model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def get_index_and_docs():
    global _index, _documents, _last_index_mtime

    if not DEPENDENCIES_INSTALLED:
        return None, []

    if not INDEX_PATH.exists() or not DOCS_PATH.exists():
        return None, []

    current_mtime = INDEX_PATH.stat().st_mtime
    if _index is None or current_mtime > _last_index_mtime:
        logger.info(f"Loading/Reloading FAISS index from {INDEX_PATH}")
        _index = faiss.read_index(str(INDEX_PATH))
        _last_index_mtime = current_mtime

        # Reload documents as well
        _documents = []
        with open(DOCS_PATH, "r") as f:
            for line in f:
                try:
                    _documents.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    return _index, _documents

def query_technical_docs(query_data: VectorQuerySchema) -> List[Dict[str, Any]]:
    """
    Advanced Vector Search (RAG) tool using FAISS.
    Allows Casper to ask questions about Snort rules, GAMEBOY_ANALYSIS.md, etc.
    """
    query = query_data.query
    collection = query_data.collection
    logger.info(f"Querying FAISS database for: {query} in collection: {collection}")

    index, documents = get_index_and_docs()
    if index is None:
        logger.warning("FAISS index or docs file not found. Returning mock results.")
        return [{"source": "system", "content": "No documents indexed yet.", "relevance": 0.0}]

    try:
        # Generate query embedding
        model = get_model()
        query_embedding = model.encode([query]).astype('float32')

        # Search the index
        # We fetch more results (k=10) if a collection filter is applied
        # to ensure we have enough relevant matches after filtering.
        k = 10 if collection != "default" else 5
        distances, indices = index.search(query_embedding, k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(documents):
                doc = documents[idx]
                source = doc.get("source", "unknown")
                content = doc.get("content", "")
                metadata = doc.get("metadata", {})

                # Collection filtering
                if collection != "default":
                    doc_collection = metadata.get("collection")
                    if doc_collection != collection:
                        continue

                results.append({
                    "source": source,
                    "content": content,
                    "metadata": metadata,
                    "relevance": float(1 / (1 + dist))  # Simplified relevance score
                })
        return results
    except Exception as e:
        logger.error(f"Error during vector search: {e}")
        return [{"error": str(e)}]

def index_document(doc_data: DocumentIndexSchema) -> str:
    """
    Adds a document to the production-ready FAISS index.
    Supports Level 6 Multimodal Memory via metadata (e.g., image descriptions).
    """
    filepath = doc_data.filepath
    metadata = doc_data.metadata or {}

    # Ensure filepath is treated relative to project root if it's not absolute
    if not os.path.isabs(filepath):
        project_root = Path(__file__).resolve().parent.parent
        filepath = str(project_root / filepath)

    if not os.path.exists(filepath):
        return f"Error: File {filepath} not found."

    # Prevent duplicate indexing of the same file
    _, documents = get_index_and_docs()
    filename = os.path.basename(filepath)
    if any(doc.get("source") == filename for doc in documents):
        logger.info(f"File {filename} is already indexed. Skipping.")
        return f"Document {filename} is already indexed."

    try:
        logger.info(f"Indexing document: {filepath}")

        if not DEPENDENCIES_INSTALLED:
            return "Error: FAISS or SentenceTransformer not installed. Indexing unavailable."

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
                doc_entry = {
                    "source": os.path.basename(filepath),
                    "content": chunk,
                    "metadata": metadata
                }
                f.write(json.dumps(doc_entry) + "\n")

        return f"Successfully indexed {len(chunks)} chunks from {filepath} into the FAISS store (Multimodal metadata included)."
    except Exception as e:
        logger.error(f"Error during document indexing: {e}")
        return f"Error indexing {filepath}: {e}"
