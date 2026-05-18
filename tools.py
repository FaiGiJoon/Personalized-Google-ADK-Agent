import sqlite3
import json
from typing import Dict, Any
from google.adk.tools import ToolContext, FunctionTool
try:
    from .database import USER_DB_FILE
except (ImportError, ValueError):
    from database import USER_DB_FILE

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
    """Retrieves all stored preferences for the current user."""
    user_id = tool_context.session.user_id
    preferences = {}
    with sqlite3.connect(USER_DB_FILE) as conn:
        rows = conn.execute("""
            SELECT pref_key, pref_value 
            FROM user_preferences 
            WHERE user_id = ?
        """, (user_id,)).fetchall()
        
        if not rows:
            return {"message": "No previous profile found for this user."}
        
        for key, value_str in rows:
            preferences[key] = json.loads(value_str)
            
    return preferences

# ADK Tool wrappers
save_profile_tool = FunctionTool(save_user_profile)
recall_profile_tool = FunctionTool(recall_user_profile)
