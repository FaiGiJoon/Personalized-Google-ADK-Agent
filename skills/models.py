from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class SnortRuleSchema(BaseModel):
    rule: str = Field(..., description="The Snort 3 rule string to validate.")

class QuishingSchema(BaseModel):
    content: str = Field(..., description="The content (email, message, etc.) to analyze for quishing or linguistic threats.")

class PBRTeamSchema(BaseModel):
    team_data: Dict[str, Any] = Field(..., description="The PBR team data in JSON/dictionary format to optimize.")

class BrowserAutomationSchema(BaseModel):
    script_name: str = Field(..., description="The name of the Chrome automation script to run.")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Optional parameters for the automation script.")

class UserProfileSchema(BaseModel):
    new_preferences: Dict[str, Any] = Field(..., description="A dictionary of user preferences to save or update.")

class KnowledgeEntitySchema(BaseModel):
    entity_name: str = Field(..., description="The name of the entity to add or update in the Knowledge Graph.")
    entity_type: str = Field(..., description="The type of the entity (e.g., 'Project', 'Person', 'Tool').")
    details: str = Field(..., description="Detailed description or information about the entity.")

class VectorQuerySchema(BaseModel):
    query: str = Field(..., description="The natural language query to search for in technical documentation.")
    collection: str = Field("default", description="The collection name to search within (e.g., 'snort', 'pbr').")

class DocumentIndexSchema(BaseModel):
    filepath: str = Field(..., description="The local filesystem path to the document to be indexed.")
