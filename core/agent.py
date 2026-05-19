import logging
import sys
import os
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CasperC2")

# Ensure project root is in sys.path for absolute imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

def load_system_prompt(mode: str = "Security Mode") -> str:
    """Reads the specified mode's instructions from PROMPTS.md."""
    prompts_path = os.path.join(project_root, "PROMPTS.md")
    if not os.path.exists(prompts_path):
        logger.warning("PROMPTS.md not found. Using default instructions.")
        return "You are Casper's C2 agent. Security-First mindset is active."

    try:
        with open(prompts_path, 'r') as f:
            content = f.read()

        # Use regex to find the section for the requested mode
        pattern = rf"## {mode}\n(.*?)(?=\n## |\Z)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
    except Exception as e:
        logger.error(f"Error reading PROMPTS.md: {e}")

    return "You are Casper's C2 agent. Security-First mindset is active."

# Check if google.adk is available
try:
    from google.adk.agents import LlmAgent
    from google.adk.tools import FunctionTool
    ADK_AVAILABLE = True
except ImportError:
    logger.error("google.adk module not found. Some functionalities will be limited.")
    ADK_AVAILABLE = False
    class LlmAgent:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

# Import memory tools
try:
    from memory.tools import save_user_profile, recall_user_profile, update_knowledge_graph
    from memory.database import setup_user_db
    from memory.vector_tools import query_technical_docs, index_document
except ImportError as e:
    logger.warning(f"Memory modules could not be imported: {e}")
    save_user_profile = recall_user_profile = update_knowledge_graph = None
    query_technical_docs = index_document = None
    def setup_user_db(): pass

# Import skills
try:
    from skills.security.security_skills import validate_snort_rule, check_quishing_threats
    from skills.gaming.gaming_skills import optimize_pbr_team
    from skills.browser_skills import run_chrome_automation
except ImportError as e:
    logger.warning(f"Skill modules could not be imported: {e}")
    validate_snort_rule = check_quishing_threats = optimize_pbr_team = run_chrome_automation = None

# Ensure database is ready
setup_user_db()

# Tool preparation
casper_tools = []
if ADK_AVAILABLE:
    if save_user_profile: casper_tools.append(FunctionTool(save_user_profile))
    if recall_user_profile: casper_tools.append(FunctionTool(recall_user_profile))
    if update_knowledge_graph: casper_tools.append(FunctionTool(update_knowledge_graph))
    if query_technical_docs: casper_tools.append(FunctionTool(query_technical_docs))
    if index_document: casper_tools.append(FunctionTool(index_document))
    if validate_snort_rule: casper_tools.append(FunctionTool(validate_snort_rule))
    if check_quishing_threats: casper_tools.append(FunctionTool(check_quishing_threats))
    if optimize_pbr_team: casper_tools.append(FunctionTool(optimize_pbr_team))
    if run_chrome_automation: casper_tools.append(FunctionTool(run_chrome_automation))

# The Casper C2 Agent - Defaults to Brain Mode for better contextual understanding
casper_agent = LlmAgent(
    name="Casper_C2_Agent",
    model="gemini-2.0-flash",
    tools=casper_tools,
    instruction=load_system_prompt("Brain Mode"),
)
