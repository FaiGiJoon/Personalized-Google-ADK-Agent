# Casper C2 Agent

The Casper C2 Agent is a centralized Command & Control (C2) system designed for security research, automation development, and personal assistance. It leverages the Google Agent Development Kit (ADK) to provide a modular and extensible agentic framework.

## Google ADK Usage

This project utilizes the following core components of the Google ADK (Agent Development Kit):

- **LlmAgent**: Located in `core/agent.py`, the `LlmAgent` is the primary agent class. It is configured with a name, a Gemini model (e.g., `gemini-2.0-flash`), a set of tools, and system instructions loaded from `PROMPTS.md`.
- **FunctionTool**: Python functions from the `memory` and `skills` modules are wrapped using `FunctionTool`. This allows the `LlmAgent` to dynamically invoke these functions during execution.
- **SqliteSessionService**: In `interface/cli.py`, this service is used to manage conversation sessions. It stores session history in a local SQLite database, allowing for persistent context across restarts.
- **Runner**: The `Runner` class (in `interface/cli.py`) orchestrates the interaction between the user, the `LlmAgent`, and the `PersistentSessionService`. It handles the execution flow and manages message history.

## ADK Memory Stack

Casper C2 implements the 6 Levels of ADK Memory as defined in the Google Codelabs:

1.  **Session & State (Level 1)**: Conversation context is maintained using ADK `Session` and `State`.
2.  **Multi-Agent State (Level 2)**: Agents share structured state information via the session scratchpad.
3.  **Persistence (Level 3)**: `SqliteSessionService` ensures memory survives reboots.
4.  **Callbacks (Level 4)**: An `after_tool_callback` in `core/agent.py` automatically logs tool usage history to the session state.
5.  **Custom Tools (Level 5)**: Specialized tools in `memory/tools.py` manage long-term user profiles and the Knowledge Graph.
6.  **Multimodal Memory (Level 6)**: RAG capabilities in `memory/vector_tools.py` provide a foundation for multimodal retrieval.

For a detailed guide, see [ADK_MEMORY_GUIDE.md](docs/ADK_MEMORY_GUIDE.md).

## Agents CLI Workflow

This repository follows the `agents-cli` workflow for building, evaluating, and deploying agents. For a detailed quickstart on using the CLI, see [AGENTS_CLI_QUICKSTART.md](docs/AGENTS_CLI_QUICKSTART.md).

## Implementation Details

The project is organized into several modules:

- **core/**: Contains the `agent.py` file which initializes the `LlmAgent` and prepares the tools.
- **interface/**: Contains `cli.py`, providing a command-line interface for interacting with the agent. It supports mode switching (Security, Dev, Assistant, Brain) via commands like `/mode Security`.
- **memory/**: Manages both long-term memory (Knowledge Graph and User Profile in SQLite) and working memory. `vector_tools.py` provides simulated RAG capabilities.
- **skills/**: Houses specialized functionality such as Snort rule validation, linguistic threat detection, and browser automation.

## Getting Started

### Prerequisites

- Python 3.11+
- Google API Key (set in `.env` or as an environment variable `GOOGLE_API_KEY`)

### Installation

1. Install the Google ADK and other dependencies:
   ```bash
   pip install google-adk python-dotenv
   ```

2. (Optional) Install additional skill dependencies as needed.

### Running the Agent

Start the agent by running the main entry point:

```bash
python3 main.py
```

### Commands

- **/mode [ModeName]**: Switch the agent's operational mode (e.g., `/mode Security`, `/mode Dev`, `/mode Assistant`, `/mode Brain`).
- **exit** or **quit**: Terminate the session.
