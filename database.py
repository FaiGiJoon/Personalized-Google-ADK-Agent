import sqlite3
import os
from pathlib import Path

# Database file for long-term user profile/preferences
USER_DB_FILE = "user_profile.db"

def setup_user_db():
    """Initializes the SQLite database for storing user preferences."""
    with sqlite3.connect(USER_DB_FILE) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id TEXT NOT NULL, 
            pref_key TEXT NOT NULL, 
            pref_value TEXT NOT NULL,
            PRIMARY KEY (user_id, pref_key)
        );""")
    print(f"✅ User profile database '{USER_DB_FILE}' is ready.")

# Session database file for persistent conversation history
SESSIONS_DIR = Path(os.path.expanduser("~")) / ".personal_agent" / "sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)
SESSION_DB_FILE = SESSIONS_DIR / "sessions.db"
SESSION_URL = f"sqlite:///{SESSION_DB_FILE}"
