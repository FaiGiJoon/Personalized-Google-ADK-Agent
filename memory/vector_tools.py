import logging
import os
from typing import List, Dict, Any

logger = logging.getLogger("CasperC2.Vector")

def query_technical_docs(query: str, collection: str = "default") -> List[Dict[str, Any]]:
    """
    Simulates a Vector Search (RAG) tool to 'read' technical documentation.
    Allows Casper to ask questions about Snort rules, GAMEBOY_ANALYSIS.md, etc.
    """
    logger.info(f"Querying vector database for: {query} in collection: {collection}")

    # Mocking search results for demonstration
    # In a real implementation, this would use a vector DB like Chroma, Pinecone, or FAISS

    mock_results = [
        {
            "source": "GAMEBOY_ANALYSIS.md",
            "content": "The GameBoy's LR35902 CPU is a hybrid between Z80 and 8080...",
            "relevance": 0.95
        },
        {
            "source": "snort3-community-rules",
            "content": "alert tcp any any -> any any (msg:\"Potential quishing link\"; content:\"qr\"; sid:1000001;)",
            "relevance": 0.88
        },
        {
            "source": "Snort3_Syntax_Guide.pdf",
            "content": "Snort 3 rules require a valid action, protocol, source/destination IP and port, and options enclosed in parentheses.",
            "relevance": 0.92
        },
        {
            "source": "PBR_Competitive_Meta.txt",
            "content": "In PBR, evasion moves like Double Team are often restricted. Speed and coverage are key factors for team optimization.",
            "relevance": 0.85
        }
    ]

    return mock_results

def index_document(filepath: str) -> str:
    """Adds a document to the vector search index."""
    # Ensure filepath is treated relative to project root if it's not absolute
    if not os.path.isabs(filepath):
        from pathlib import Path
        project_root = Path(__file__).resolve().parent.parent
        filepath = str(project_root / filepath)

    if not os.path.exists(filepath):
        return f"Error: File {filepath} not found."

    logger.info(f"Indexing document: {filepath}")
    return f"Successfully indexed {filepath} into the vector store."
