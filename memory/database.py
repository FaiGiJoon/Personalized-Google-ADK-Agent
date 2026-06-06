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
            metadata TEXT, -- JSON field for extra attributes (ADK Level 5/6)
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
            ('Law-Assistent-Agency-A2A', 'Project', 'Ecosystem A2A infrastructure for understanding Netherlands Law. TypeScript, MIT.', '{"tech_stack": ["TypeScript"], "license": "MIT"}'),
            ('WiiBridge', 'Project', 'macOS HID bridge for Nintendo Wii controllers. Swift.', '{"platform": "macOS", "language": "Swift"}'),
            ('GBA-e-Reader-Retro-Playbox', 'Project', 'GBA e-Reader dot code generator tool. Python.', '{"language": "Python"}'),
            ('USBC-SATA-SSD-Chrome-Automator', 'Project', 'Python-based automation to redirect Chrome downloads to external SATA SSD.', '{"language": "Python", "tags": ["automation"]}'),
            ('Gmail-Real-Time-Cybersecurity-Scanner', 'Project', 'Real-time protection against email threats in Gmail. JavaScript.', '{"language": "JavaScript", "security_focus": true}'),
            ('Gevi', 'Project', 'TypeScript project.', '{"language": "TypeScript"}'),
            ('Tailscale-for-MikroTik', 'Project', 'Tailscale in container on MikroTik optimized for SD card storage. RouterOS Script.', '{"platform": "MikroTik", "tags": ["networking"]}'),
            ('Axis-VMD-Automation', 'Project', 'Automation framework for Video Motion Detection on Axis network devices. Python.', '{"language": "Python", "tags": ["security"]}'),
            ('LuminaSuite', 'Project', 'Automated DS and Wii U Save-State Backup Utility. Python.', '{"language": "Python", "tags": ["gaming"]}'),
            ('omegaT-fork', 'Project', 'Fork of official OmegaT repo. Java.', '{"language": "Java"}'),
            ('Google-Apps-Script-Built-in-Bot', 'Project', 'Automation using Google Sheets. JavaScript, MIT.', '{"language": "JavaScript", "platform": "Google Apps Script"}'),
            ('Geo-Asset-Twin', 'Project', 'Geometric Asset Optimizer with 3D bin-packing and Bun.serve. TypeScript.', '{"language": "TypeScript", "tags": ["3D"]}'),
            ('Ghost-Protocol', 'Project', 'Adaptive VPN & Tunneling Manager for MikroTik. TypeScript.', '{"language": "TypeScript", "platform": "MikroTik"}'),
            ('macOS-Local-OCR-LLM-Game-Translation', 'Project', 'Python utility for local OCR and LLM game translation.', '{"language": "Python", "tags": ["AI", "gaming"]}'),
            ('PokeSync', 'Project', 'Pokemon save file synchronization across devices. Python.', '{"language": "Python", "tags": ["gaming"]}'),
            ('secure-ollama-openclaw', 'Project', 'Reverse proxy setup for Ollama and OpenClaw. Shell.', '{"language": "Shell"}'),
            ('Pokemon-3DS-Randomizer', 'Project', 'TypeScript-based Pokemon 3DS randomization tool.', '{"language": "TypeScript", "tags": ["gaming"]}'),
            ('Nintendo-DS-Emulator-Layout-Calculator', 'Project', 'Automated geometric calculations for DS emulator layouts. TypeScript.', '{"language": "TypeScript", "tags": ["gaming"]}'),
            ('FaiGiJoon.github.io', 'Project', 'Personal vibe-coded website. HTML.', '{"language": "HTML"}'),
            ('my-citra-saves', 'Project', 'Testing repository for PokeSync save file sharing.', '{"tags": ["gaming"]}'),
            ('CodeBuddyByGemini', 'Project', 'IDE/Agentic Code Debugger. TypeScript.', '{"language": "TypeScript", "tags": ["AI"]}'),
            ('Mirror-Database-Extracting', 'Project', 'Python-based database extraction utility.', '{"language": "Python"}'),
            ('F32-Ghydra', 'Project', 'TypeScript project related to Ghidra.', '{"language": "TypeScript"}'),
            ('Jira-Automation-Gemini-A2A', 'Project', 'Jira automation using Gemini A2A. Python.', '{"language": "Python", "tags": ["AI", "automation"]}'),
            ('Benchmark-FF', 'Project', 'Python-based benchmarking tool.', '{"language": "Python"}'),
            ('chrome-devtools-mcp', 'Project', 'MCP server for Chrome DevTools. TypeScript.', '{"language": "TypeScript"}'),
            ('timesfm', 'Project', 'Time Series Foundation Model by Google Research. Python.', '{"language": "Python", "tags": ["AI"]}'),
            ('cloud-run-mcp', 'Project', 'MCP server to deploy apps to Cloud Run. JavaScript.', '{"language": "JavaScript", "platform": "Cloud Run"}'),
            ('Pokemon-3DS-Randomizer-tool', 'Project', 'Testing area for OpenClaw. TypeScript.', '{"language": "TypeScript"}'),
            ('Casper', 'Person', 'Security researcher and automation developer based in the Netherlands. Expert in Google ecosystem (Gemini, Workspace, Cloud Run), networking (MikroTik, RouterOS), and retro-gaming emulators.', '{"location": "Netherlands", "focus": ["Security", "Automation", "Emulators"], "expertise": ["Google ADK", "Python", "TypeScript"]}')
        ]

        conn.executemany("""
            INSERT OR IGNORE INTO knowledge_graph (user_id, entity_name, entity_type, details, metadata)
            VALUES ('Casper', ?, ?, ?, ?);
        """, casper_projects)

    print(f"OK: User profile database '{USER_DB_FILE}' is ready.")

# Session database file for persistent conversation history (ADK PersistentSessionService)
SESSIONS_DIR = Path(os.path.expanduser("~")) / ".personal_agent" / "sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)
SESSION_DB_FILE = SESSIONS_DIR / "sessions.db"
SESSION_URL = f"sqlite:///{SESSION_DB_FILE}"
