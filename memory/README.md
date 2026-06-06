# Casper C2 Memory System

This module implements the 6 Levels of Agent Memory as defined in the Google Agent Development Kit (ADK) documentation.

## 6 Levels of Memory Implementation

### Level 1: Session & State
Managed by the `google.adk` framework. Conversation history is maintained within the `Session` object, and a key-value `State` scratchpad is available for short-term context.
- **Reference**: `interface/cli.py` (via `SqliteSessionService`).

### Level 2: Multi-Agent State (Enhanced)
Implemented by sharing data via `tool_context.state`. When entities are updated in the Knowledge Graph, their names are recorded in the shared state, allowing other agents or future turns to maintain contextual awareness.
- **Implementation**: `memory/tools.py` -> `update_knowledge_graph` updates `tool_context.state["latest_entities"]`.

### Level 3: Persistence
Short-term session memory is persisted to a local SQLite database using the ADK's `SqliteSessionService`. This ensures that conversation context survives agent restarts.
- **Implementation**: `interface/cli.py` -> `SqliteSessionService(db_path=SESSION_DB_FILE)`.

### Level 4: Callbacks
Autonomous memory updates are handled via an `after_tool_callback`. This callback automatically logs tool usage history into the session state without requiring explicit agent instructions.
- **Implementation**: `core/agent.py` -> `log_tool_usage_callback`.

### Level 5: Custom Tools (Enhanced)
Long-term, structured memory is managed through dedicated tools that interact with a persistent User Profile and Knowledge Graph database. The schema includes metadata support for rich entity descriptions.
- **Tools**: `save_user_profile`, `recall_user_profile`, `update_knowledge_graph`.
- **Storage**: `memory/user_profile.db`.

### Level 6: Multimodal Memory (Enhanced)
Simulated multimodal retrieval (RAG) is implemented using FAISS. The system supports indexing and querying technical documents with attached multimodal metadata (e.g., image descriptions, media URLs).
- **Tools**: `index_document`, `query_technical_docs`.
- **Implementation**: `memory/vector_tools.py` supports storing and retrieving JSON metadata alongside text embeddings.

## Technical Details

- **Database**: SQLite (for structured data and session persistence).
- **Vector Store**: FAISS (for semantic search and RAG).
- **Embedding Model**: `all-MiniLM-L6-v2` (via SentenceTransformers).
- **Schema Validation**: Pydantic models in `skills/models.py`.
