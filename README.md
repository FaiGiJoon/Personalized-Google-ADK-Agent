# Casper C2 Agent

The **Casper C2 Agent** is a centralized Command & Control (C2) hub built using the Google ADK (Agent Development Kit) framework. It is designed to assist with security research, development automation, and personal technical management, specifically tailored for Casper's extensive portfolio of projects.

## 🚀 Overview

Casper C2 operates with a "Security-First" mindset, integrating long-term memory, a knowledge graph, and specialized skills to provide context-aware assistance. It leverages the Gemini 2.0 Flash model to interact with various tools and databases.

## 🏗️ Architecture

The project follows a modular architecture:

- **`core/`**: Contains the core agent logic (`agent.py`) and handles system prompt management.
- **`interface/`**: Provides the CLI interface (`cli.py`) for interacting with the agent.
- **`memory/`**: Manages data persistence, including:
    - **SQLite Database**: Long-term memory for user profiles and knowledge graphs.
    - **Vector Search (RAG)**: Simulated technical documentation search for deeper context.
- **`skills/`**: Houses specialized skill modules:
    - **Security**: Snort 3 rule validation and linguistic threat (quishing) detection.
    - **Gaming**: Pokemon Battle Revolution (PBR) team optimization.
    - **Browser**: Scriptable automation via Chrome Automator.

## 🛠️ Operational Modes

The agent can switch between different modes at runtime to adjust its behavior:

- **🛡️ Security Mode**: Focuses on the security and integrity of the ecosystem. Validates Snort rules and monitors for threats.
- **💻 Dev Mode**: Acts as a Lead Engineer, assisting with code quality, refactoring, and architectural decisions.
- **🤖 Assistant Mode**: Handles general inquiries and information retrieval, leveraging the Knowledge Graph.
- **🧠 Brain Mode** (Default): Serves as an "External Brain," providing deep contextual understanding and architectural synthesis across all 29+ repositories.

## ⌨️ Getting Started

### Prerequisites

- Python 3.10+
- Google ADK (Agent Development Kit)
- `google-genai`
- `python-dotenv`

### Running the Agent

To start the C2 session, run:

```bash
python3 main.py
```

### Commands

Within the CLI, you can use the following commands:

- `/mode [Security|Dev|Assistant|Brain]`: Switches the agent's operational mode.
- `exit` or `quit`: Terminate the session.

## 🛡️ Security Features

- **Snort Rule Validation**: Ensures Snort 3 rules are correctly formatted and secure.
- **Quishing Detection**: Analyzes linguistic patterns in emails to identify phishing threats.
- **Secure Defaults**: Proactively checks for hardcoded keys and insecure configurations.

---
*Built with ❤️ for Casper's technical ecosystem.*
