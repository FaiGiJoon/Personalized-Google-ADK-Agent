# Building Stateful and Personalized Agents with ADK

This guide covers the core concepts and 6 levels of memory as defined in the Google Codelab: "Building Stateful and Personalized Agents with ADK".

## The "Goldfish" Problem
Without memory, every interaction with an AI agent is a blank slate. The intelligence is there, but the continuity is missing. For an AI agent to be truly useful, it needs to remember.

## Your Mission
Solve the Goldfish Problem by building agents that remember, learn, and adapt through 6 Levels of Agent Memory.

| Level | Concept | The "Superpower" |
| :--- | :--- | :--- |
| **Level 1** | Session & State | Holding a conversation without forgetting |
| **Level 2** | Multi-Agent State | Sharing notes between team members |
| **Level 3** | Persistence | Remembering you even after a system reboot |
| **Level 4** | Callbacks | Updating memory completely autonomously |
| **Level 5** | Custom Tools | Reading & writing structured user profiles |
| **Level 6** | Multimodal Memory | "Seeing" and remembering photos & videos |

## The ADK Memory Stack
The Google Agent Development Kit (ADK) provides a structured way to handle memory:

1.  **Session**: The container for a conversation. It holds the history of what was said.
2.  **State**: A key-value "scratchpad" attached to the session. Agents use this to store specific facts (e.g., `destination="Tokyo"`).
3.  **MemoryService**: Long-term storage. This is where we keep things forever, like user preferences or analyzed documents.

---

## Detailed Levels

### 1. Session & State
- **Concept**: Context is King. Session memory allows an agent to understand pronouns (e.g., "it") by referring back to previous turns.
- **Implementation**: Reuse the `session.id` to maintain conversation context. The `Session` object is the short-term memory buffer.

### 2. Multi-Agent State
- **Concept**: "The Telephone Game". When multiple agents work together, they share a "folder" (the State).
- **Implementation**: Use `State` (a dictionary in the `Session`) to pass structured information. Use `output_key` to write to state and `{placeholders}` in instructions to read from it.

### 3. Persistence
- **Concept**: "The Reboot Problem". Standard memory is often in-memory and lost on restart. Persistence saves sessions to a database.
- **Implementation**: Use `DatabaseSessionService` (e.g., with SQLite) to ensure conversations survive server restarts and enable long-term history analysis.

### 4. Callbacks
- **Concept**: "The Spy". Updating memory automatically based on agent actions, not just words.
- **Implementation**: Use `after_tool_callback` to watch the agent and take notes. Use `ToolContext` to write to `State` from inside the callback.

### 5. Custom Tools
- **Concept**: "Structured Memory". Treat memory as a tool (Read/Write) for complex data like user profiles.
- **Implementation**: Give the agent tools like `save_user_preferences` and `recall_user_preferences`. Let the LLM manage its own long-term storage.

### 6. Multimodal Memory
- **Concept**: "The Human Experience". Remembering images, videos, and audio.
- **Implementation**: Use Vertex AI Memory Bank to ingest, understand, and retrieve multimodal content, connecting dots across different media types.
