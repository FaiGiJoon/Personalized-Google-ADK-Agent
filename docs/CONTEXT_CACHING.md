# Gemini Context Caching Strategy for Casper C2

## Overview
To reduce latency and costs for the Casper C2 agent, we implement Gemini's Context Caching. This is particularly effective for large, static contexts such as `PROMPTS.md` and the extensive Knowledge Graph.

## Target Data
1.  **System Instructions (`PROMPTS.md`):** Contains the primary behavioral guidelines for all four operational modes (Security, Dev, Assistant, Brain).
2.  **Knowledge Graph:** A comprehensive list of Casper's 29+ projects and personal context, currently stored in SQLite and periodically injected into the context.

## Caching Strategy

### 1. Pre-caching System Prompts
The `PROMPTS.md` file should be pre-cached as a `CachedContent` object. This ensures that every session starts with the full context of all modes without re-uploading the data.

```python
from google.genai import Client, types

client = Client(api_key="YOUR_API_KEY")

# Create a cache for the system instructions
system_instructions = open("PROMPTS.md").read()
cache = client.caches.create(
    model="models/gemini-2.0-flash",
    config=types.CreateCacheConfig(
        system_instruction=system_instructions,
        ttl_seconds=3600 * 24, # Cache for 24 hours
    )
)
```

### 2. Knowledge Graph Injection
Since the Knowledge Graph changes less frequently than the conversation but more frequently than the system prompts, it can be cached as a secondary layer or appended to the system instruction cache if it exceeds 32k tokens.

### 3. Usage in Sessions
When initializing the `Runner` or `LlmAgent`, reference the `cache_name` to leverage the cached content.

```python
# When running a session
response = client.models.generate_content(
    model="models/gemini-2.0-flash",
    contents=user_input,
    config=types.GenerateContentConfig(
        cached_content=cache.name
    )
)
```

## Benefits
-   **Reduced Latency:** Faster Time-To-First-Token (TTFT) by avoiding repeated processing of large system prompts.
-   **Cost Optimization:** Lower token usage for repeated context in long-running sessions.
-   **Consistency:** Ensures the "Brain Mode" always has access to the full project portfolio.

## Future Implementation
Integrate the `PersistentSessionService` with a dynamic caching layer that refreshes the cache whenever `PROMPTS.md` or the `knowledge_graph` table is significantly updated.
