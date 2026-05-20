import sqlite3
import os
from pathlib import Path

# Database file for long-term user profile/preferences and Knowledge Graph
MEMORY_DIR = Path(__file__).parent
USER_DB_FILE = MEMORY_DIR / "user_profile.db"

def setup_user_db():
    """Initializes the SQLite database for storing user preferences and knowledge graph."""
    with sqlite3.connect(USER_DB_FILE) as conn:
        # User preferences (General Long-Term Memory)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id TEXT NOT NULL,
            pref_key TEXT NOT NULL,
            pref_value TEXT NOT NULL,
            PRIMARY KEY (user_id, pref_key)
        );""")

        # Knowledge Graph (Project-specific Long-Term Memory)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_graph (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            entity_name TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            details TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, entity_name)
        );""")

        # Working Memory (Contextual session-based memory)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS working_memory (
            session_id TEXT NOT NULL,
            context_key TEXT NOT NULL,
            context_value TEXT NOT NULL,
            PRIMARY KEY (session_id, context_key)
        );""")

        # Seed with Casper's expanded project portfolio and focus areas
        casper_projects = [
            ('Law-Assistent-Agency-A2A', 'Project', 'Ecosystem A2A infrastructure for understanding Netherlands Law. TypeScript, MIT.'),
            ('WiiBridge', 'Project', 'macOS HID bridge for Nintendo Wii controllers. Swift.'),
            ('GBA-e-Reader-Retro-Playbox', 'Project', 'GBA e-Reader dot code generator tool. Python.'),
            ('USBC-SATA-SSD-Chrome-Automator', 'Project', 'Python-based automation to redirect Chrome downloads to external SATA SSD.'),
            ('Gmail-Real-Time-Cybersecurity-Scanner', 'Project', 'Real-time protection against email threats in Gmail. JavaScript.'),
            ('Gevi', 'Project', 'TypeScript project.'),
            ('Tailscale-for-MikroTik', 'Project', 'Tailscale in container on MikroTik optimized for SD card storage. RouterOS Script.'),
            ('Axis-VMD-Automation', 'Project', 'Automation framework for Video Motion Detection on Axis network devices. Python.'),
            ('LuminaSuite', 'Project', 'Automated DS and Wii U Save-State Backup Utility. Python.'),
            ('omegaT-fork', 'Project', 'Fork of official OmegaT repo. Java.'),
            ('Google-Apps-Script-Built-in-Bot', 'Project', 'Automation using Google Sheets. JavaScript, MIT.'),
            ('Geo-Asset-Twin', 'Project', 'Geometric Asset Optimizer with 3D bin-packing and Bun.serve. TypeScript.'),
            ('Ghost-Protocol', 'Project', 'Adaptive VPN & Tunneling Manager for MikroTik. TypeScript.'),
            ('macOS-Local-OCR-LLM-Game-Translation', 'Project', 'Python utility for local OCR and LLM game translation.'),
            ('PokeSync', 'Project', 'Pokemon save file synchronization across devices. Python.'),
            ('secure-ollama-openclaw', 'Project', 'Reverse proxy setup for Ollama and OpenClaw. Shell.'),
            ('Pokemon-3DS-Randomizer', 'Project', 'TypeScript-based Pokemon 3DS randomization tool.'),
            ('Nintendo-DS-Emulator-Layout-Calculator', 'Project', 'Automated geometric calculations for DS emulator layouts. TypeScript.'),
            ('FaiGiJoon.github.io', 'Project', 'Personal vibe-coded website. HTML.'),
            ('my-citra-saves', 'Project', 'Testing repository for PokeSync save file sharing.'),
            ('CodeBuddyByGemini', 'Project', 'IDE/Agentic Code Debugger. TypeScript.'),
            ('Mirror-Database-Extracting', 'Project', 'Python-based database extraction utility.'),
            ('F32-Ghydra', 'Project', 'TypeScript project related to Ghidra.'),
            ('Jira-Automation-Gemini-A2A', 'Project', 'Jira automation using Gemini A2A. Python.'),
            ('Benchmark-FF', 'Project', 'Python-based benchmarking tool.'),
            ('chrome-devtools-mcp', 'Project', 'MCP server for Chrome DevTools. TypeScript.'),
            ('timesfm', 'Project', 'Time Series Foundation Model by Google Research. Python.'),
            ('cloud-run-mcp', 'Project', 'MCP server to deploy apps to Cloud Run. JavaScript.'),
            ('Pokemon-3DS-Randomizer-tool', 'Project', 'Testing area for OpenClaw. TypeScript.'),
            ('Casper', 'Person', 'Security researcher and automation developer. Likes Google ecosystem (Gemini CLI, Workspace CLI, Jules). Works with emulators and RouterOS.')
        ]

        conn.executemany("""
            INSERT OR IGNORE INTO knowledge_graph (user_id, entity_name, entity_type, details)
            VALUES ('Casper', ?, ?, ?);
        """, casper_projects)

    print(f"OK: User profile database '{USER_DB_FILE}' is ready.")

# Session database file for persistent conversation history (ADK PersistentSessionService)
SESSIONS_DIR = Path(os.path.expanduser("~")) / ".personal_agent" / "sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)
SESSION_DB_FILE = SESSIONS_DIR / "sessions.db"
SESSION_URL = f"sqlite:///{SESSION_DB_FILE}"
