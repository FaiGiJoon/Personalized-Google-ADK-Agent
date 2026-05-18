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

        # Seed with Casper's primary focus areas if they don't exist
        conn.execute("""
            INSERT OR IGNORE INTO knowledge_graph (user_id, entity_name, entity_type, details)
            VALUES ('Casper', 'PokeSync', 'Project', 'Primary focus area: Pokemon data synchronization and analysis.');
        """)
        conn.execute("""
            INSERT OR IGNORE INTO knowledge_graph (user_id, entity_name, entity_type, details)
            VALUES ('Casper', 'Gmail_Security_Automation', 'Project', 'Primary focus area: Automation for Gmail security and threat detection.');
        """)

    print(f"✅ User profile database '{USER_DB_FILE}' is ready.")

# Session database file for persistent conversation history (ADK PersistentSessionService)
SESSIONS_DIR = Path(os.path.expanduser("~")) / ".personal_agent" / "sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)
SESSION_DB_FILE = SESSIONS_DIR / "sessions.db"
SESSION_URL = f"sqlite:///{SESSION_DB_FILE}"
