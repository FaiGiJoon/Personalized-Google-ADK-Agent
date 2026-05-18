import sqlite3
import json
import os
import sys
from typing import Dict, Any, List

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from memory.database import USER_DB_FILE
except ImportError:
    # Fallback for different execution contexts
    try:
        from .database import USER_DB_FILE
    except ImportError:
        USER_DB_FILE = os.path.join(os.path.dirname(__file__), "user_profile.db")

# Optional ADK import
try:
    from google.adk.tools import ToolContext
except ImportError:
    # Fallback ToolContext for type hinting or if google.adk is missing
    class ToolContext:
        def __init__(self, session):
            self.session = session
    class Session:
        def __init__(self, user_id):
            self.user_id = user_id

def save_user_profile(tool_context: ToolContext, new_preferences: Dict[str, Any]) -> str:
    """Saves or updates user preferences in the persistent database."""
    user_id = tool_context.session.user_id
    with sqlite3.connect(USER_DB_FILE) as conn:
        for key, value in new_preferences.items():
            conn.execute("""
                INSERT INTO user_preferences (user_id, pref_key, pref_value)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, pref_key)
                DO UPDATE SET pref_value = excluded.pref_value;
            """, (user_id, key, json.dumps(value)))
    return f"Successfully updated preferences: {list(new_preferences.keys())}"

def recall_user_profile(tool_context: ToolContext) -> Dict[str, Any]:
    """Retrieves all stored preferences and knowledge graph entities for the current user."""
    user_id = tool_context.session.user_id
    result = {"preferences": {}, "knowledge_graph": []}

    with sqlite3.connect(USER_DB_FILE) as conn:
        # Fetch preferences
        rows = conn.execute("""
            SELECT pref_key, pref_value
            FROM user_preferences
            WHERE user_id = ?
        """, (user_id,)).fetchall()

        for key, value_str in rows:
            result["preferences"][key] = json.loads(value_str)

        # Fetch knowledge graph entities
        kg_rows = conn.execute("""
            SELECT entity_name, entity_type, details
            FROM knowledge_graph
            WHERE user_id = ? OR user_id = 'Casper'
        """, (user_id,)).fetchall()

        for name, type_, details in kg_rows:
            result["knowledge_graph"].append({
                "name": name,
                "type": type_,
                "details": details
            })

    return result

def update_knowledge_graph(tool_context: ToolContext, entity_name: str, entity_type: str, details: str) -> str:
    """Adds or updates an entity in Casper's Knowledge Graph."""
    user_id = tool_context.session.user_id
    with sqlite3.connect(USER_DB_FILE) as conn:
        conn.execute("""
            INSERT INTO knowledge_graph (user_id, entity_name, entity_type, details)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, entity_name)
            DO UPDATE SET entity_type = excluded.entity_type, details = excluded.details, last_updated = CURRENT_TIMESTAMP;
        """, (user_id, entity_name, entity_type, details))
    return f"Knowledge Graph updated for: {entity_name}"
