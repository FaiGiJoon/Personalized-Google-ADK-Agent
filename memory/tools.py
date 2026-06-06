import sqlite3
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Ensure project root is in sys.path
project_root = str(Path(__file__).resolve().parent.parent)
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

from skills.models import UserProfileSchema, KnowledgeEntitySchema

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

def save_user_profile(tool_context: ToolContext, profile_data: UserProfileSchema) -> str:
    """Saves or updates user preferences in the persistent database."""
    user_id = tool_context.session.user_id
    new_preferences = profile_data.new_preferences
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
            SELECT entity_name, entity_type, details, metadata
            FROM knowledge_graph
            WHERE user_id = ? OR user_id = 'Casper'
        """, (user_id,)).fetchall()

        for name, type_, details, metadata_str in kg_rows:
            result["knowledge_graph"].append({
                "name": name,
                "type": type_,
                "details": details,
                "metadata": json.loads(metadata_str) if metadata_str else {}
            })

    return result

def update_knowledge_graph(tool_context: ToolContext, entity_data: KnowledgeEntitySchema) -> str:
    """
    Adds or updates an entity in Casper's Knowledge Graph.
    Level 2 Memory: Shares the updated entity in tool_context.state for multi-agent coordination.
    """
    user_id = tool_context.session.user_id
    entity_name = entity_data.entity_name
    entity_type = entity_data.entity_type
    details = entity_data.details
    metadata = json.dumps(entity_data.metadata) if entity_data.metadata else None

    # Level 2: Update session state to share info with other agents/turns
    if "latest_entities" not in tool_context.state:
        tool_context.state["latest_entities"] = []
    tool_context.state["latest_entities"].append(entity_name)

    with sqlite3.connect(USER_DB_FILE) as conn:
        conn.execute("""
            INSERT INTO knowledge_graph (user_id, entity_name, entity_type, details, metadata)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, entity_name)
            DO UPDATE SET entity_type = excluded.entity_type, details = excluded.details, metadata = excluded.metadata, last_updated = CURRENT_TIMESTAMP;
        """, (user_id, entity_name, entity_type, details, metadata))
    return f"Knowledge Graph updated for: {entity_name}. State updated with latest entity."
