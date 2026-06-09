# Casper C2 Agent

The Casper C2 Agent is a centralized Command & Control (C2) system designed for security research, automation development, and personal assistance. It leverages the Google Agent Development Kit (ADK) to provide a modular and extensible agentic framework.

## Multi-Agent Architecture

Casper C2 utilizes a hierarchical multi-agent structure to handle complex tasks efficiently:

- **Casper_C2_Root**: The supervisor agent that orchestrates requests and transfers them to the most appropriate specialized agent.
- **Security_Agent**: Handles network security, Snort/YARA rule validation, and threat detection (e.g., quishing).
- **Dev_Agent**: Assists with software development, code optimization, and debugging for Casper's project portfolio.
- **Assistant_Agent**: Manages personal assistance, user profiling, PBR gaming optimizations, and web-based research via Chrome automation.
- **Brain_Agent**: Maintains long-term memory, knowledge graphs, and technical documentation indexing across all repositories.

### Automated Workflows

The system also includes pre-defined workflows for multi-step tasks:
- **Research_and_Verify_Workflow**: A sequential workflow that performs deep research followed by a security audit of the findings.

## Google ADK Usage

This project utilizes the following core components of the Google ADK:

- **LlmAgent**: The primary agent class, configured with specialized instructions and tools.
- **SequentialAgent**: Used to chain multiple agents for complex workflows.
- **FunctionTool**: Wraps Python functions from the `memory` and `skills` modules.
- **SqliteSessionService**: Manages persistent conversation history in a local SQLite database.
- **Runner**: Orchestrates the interaction between the user, agents, and session services.

## ADK Memory Stack

Casper C2 implements the 6 Levels of ADK Memory:

1.  **Session & State (Level 1)**: Conversation context maintained via ADK `Session` and `State`.
2.  **Multi-Agent State (Level 2)**: Agents share structured state information (e.g., `latest_entities`) via the session scratchpad.
3.  **Persistence (Level 3)**: `SqliteSessionService` ensures memory survives reboots.
4.  **Callbacks (Level 4)**: An `after_tool_callback` automatically logs tool usage history to the session state.
5.  **Custom Tools (Level 5)**: Specialized tools manage long-term user profiles and the Knowledge Graph in SQLite.
6.  **Multimodal Memory (Level 6)**: RAG capabilities in `memory/vector_tools.py` provide multimodal retrieval foundations.

## Testing & Verification

To ensure reliability, the project includes a "Virtual Session" test suite that simulates full agent interactions without consuming API tokens.

### Running the Virtual Test
```bash
python3 -m unittest tests/test_virtual_session.py
```
This test mocks the Gemini model to verify:
- Root agent orchestration and sub-agent selection.
- Correct tool invocation across all modes.
- Cross-agent state sharing and long-term memory persistence.
- Session resumption and history preservation.

### Running All Tests
```bash
python3 -m unittest discover tests
```

## Getting Started

### Prerequisites
- Python 3.11+
- Google API Key (set in `.env` as `GOOGLE_API_KEY`)

### Installation
```bash
pip install -r requirements.txt
```

### Running the Agent
```bash
python3 main.py
```

### Commands
- **/mode [Security|Dev|Assistant|Brain]**: Switch the agent's operational focus.
- **exit** or **quit**: Terminate the session.
