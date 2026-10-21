import logging
import sys
import os
import re
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CasperC2")

# Ensure project root is in sys.path for absolute imports
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Personal profile: single source of truth for who the agent serves and the
# machine it runs on (the Alienware laptop). See profile.py to edit.
try:
    from personal_profile import personal_context_block, OWNER
    PERSONAL_CONTEXT = personal_context_block()
    OWNER_NAME = OWNER.name
except Exception as e:  # pragma: no cover - profile is optional at import time
    logger.warning(f"profile.py could not be loaded: {e}")
    PERSONAL_CONTEXT = ""
    OWNER_NAME = "Casper"


def _personalize(instruction: str) -> str:
    """Prepend the owner/machine context to any instruction block."""
    if PERSONAL_CONTEXT:
        return f"{PERSONAL_CONTEXT}\n{instruction}"
    return instruction


def load_system_prompt(mode: str = "Security Mode") -> str:
    """Reads the specified mode's instructions from PROMPTS.md."""
    prompts_path = os.path.join(project_root, "PROMPTS.md")
    if not os.path.exists(prompts_path):
        logger.warning("PROMPTS.md not found. Using default instructions.")
        return _personalize("You are Casper's personal agent. Security-First mindset is active.")

    try:
        # Force UTF-8: PROMPTS.md contains em-dashes/unicode, and Windows
        # (Alienware) defaults to cp1252, which raises UnicodeDecodeError.
        with open(prompts_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Use regex to find the section for the requested mode
        pattern = rf"## {mode}\n(.*?)(?=\n## |\Z)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return _personalize(match.group(1).strip())
    except Exception as e:
        logger.error(f"Error reading PROMPTS.md: {e}")

    return _personalize("You are Casper's personal agent. Security-First mindset is active.")

from typing import Dict, Any, Optional, List

# Check if google.adk is available
try:
    from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent, ParallelAgent
    from google.adk.tools import FunctionTool, ToolContext
    ADK_AVAILABLE = True
except ImportError:
    logger.error("google.adk module not found. Some functionalities will be limited.")
    ADK_AVAILABLE = False
    class LlmAgent:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    class ToolContext:
        def __init__(self, session=None, state=None):
            self.session = session
            self.state = state if state is not None else {}
    SequentialAgent = LoopAgent = ParallelAgent = LlmAgent

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
    from skills.security.security_skills import validate_snort_rule, check_quishing_threats, validate_yara_rule
    from skills.gaming.gaming_skills import optimize_pbr_team
    from skills.browser_skills import run_chrome_automation
except ImportError as e:
    logger.warning(f"Skill modules could not be imported: {e}")
    validate_snort_rule = check_quishing_threats = validate_yara_rule = optimize_pbr_team = run_chrome_automation = None

# Ensure database is ready
setup_user_db()

def log_tool_usage_callback(
    tool: Any,
    args: Dict[str, Any],
    tool_context: ToolContext,
    tool_response: Any,
) -> Any:
    """
    Level 4 Memory: Callback to log tool usage into the session state.
    """
    if "tool_history" not in tool_context.state:
        tool_context.state["tool_history"] = []

    tool_name = getattr(tool, "name", str(tool))
    tool_context.state["tool_history"].append(tool_name)

    logger.info(f"Callback: Logged usage of tool '{tool_name}' to session state.")
    return tool_response

# Shared configuration
MODEL_NAME = "gemini-2.0-flash"

ORCHESTRATOR_GUIDANCE = (
    "You are Casper's C2 Root Agent. You orchestrate requests to specialized agents.\n"
    "- Communication & Quality Standards: Maintain clear, concise, and professional communication. Do not use emojis. Confirm user intent when ambiguous and ensure responses end with a clear resolution or next step.\n"
    "- Use 'Security_Agent' for security, Snort, YARA, or threat analysis.\n"
    "- Use 'Dev_Agent' for coding and development tasks.\n"
    "- Use 'Assistant_Agent' for personal tasks, PBR, or browser automation.\n"
    "- Use 'Brain_Agent' for deep context, memory, or technical docs.\n"
    "- Use 'Research_and_Verify_Workflow' when the user wants a deep research followed by a security audit.\n"
    "Always take end-to-end ownership and route requests to the optimal sub-agent."
)

def get_root_instruction(mode_instruction: str = "") -> str:
    """Returns the full instruction for the Root Agent with optional mode-specific guidance."""
    base = f"{PERSONAL_CONTEXT}\n{ORCHESTRATOR_GUIDANCE}" if PERSONAL_CONTEXT else ORCHESTRATOR_GUIDANCE
    if mode_instruction:
        return f"Root Agent Guidance: {mode_instruction}\n\n{base}"
    return base

def create_specialized_agents():
    """Factory to create specialized agents to avoid sharing instances between parents."""
    security_tools = []
    if ADK_AVAILABLE:
        if validate_snort_rule: security_tools.append(FunctionTool(validate_snort_rule))
        if validate_yara_rule: security_tools.append(FunctionTool(validate_yara_rule))
        if check_quishing_threats: security_tools.append(FunctionTool(check_quishing_threats))

    security_agent = LlmAgent(
        name="Security_Agent",
        model=MODEL_NAME,
        tools=security_tools,
        instruction=load_system_prompt("Security Mode"),
        description="Handles network security, rule validation (Snort/YARA), and threat detection."
    )

    dev_agent = LlmAgent(
        name="Dev_Agent",
        model=MODEL_NAME,
        tools=[],
        instruction=load_system_prompt("Dev Mode"),
        description="Assists with software development, code optimization, and debugging."
    )

    assistant_tools = []
    if ADK_AVAILABLE:
        if save_user_profile: assistant_tools.append(FunctionTool(save_user_profile))
        if recall_user_profile: assistant_tools.append(FunctionTool(recall_user_profile))
        if optimize_pbr_team: assistant_tools.append(FunctionTool(optimize_pbr_team))
        if run_chrome_automation: assistant_tools.append(FunctionTool(run_chrome_automation))

    assistant_agent = LlmAgent(
        name="Assistant_Agent",
        model=MODEL_NAME,
        tools=assistant_tools,
        instruction=load_system_prompt("Assistant Mode"),
        description="Handles personal assistance, user profiling, gaming optimizations, and web automation."
    )

    brain_tools = []
    if ADK_AVAILABLE:
        if update_knowledge_graph: brain_tools.append(FunctionTool(update_knowledge_graph))
        if query_technical_docs: brain_tools.append(FunctionTool(query_technical_docs))
        if index_document: brain_tools.append(FunctionTool(index_document))

    brain_agent = LlmAgent(
        name="Brain_Agent",
        model=MODEL_NAME,
        tools=brain_tools,
        instruction=load_system_prompt("Brain Mode"),
        description="Maintains long-term memory, knowledge graphs, and technical documentation indexing."
    )

    return security_agent, dev_agent, assistant_agent, brain_agent

# Create primary instances for the root agent
security_agent, dev_agent, assistant_agent, brain_agent = create_specialized_agents()

# Create separate instances for the workflow to avoid "already has a parent" error
w_security_agent, _, _, w_brain_agent = create_specialized_agents()

# Workflow Agents
# A SequentialAgent runs its sub-agents one after another.
research_and_verify_workflow = SequentialAgent(
    name="Research_and_Verify_Workflow",
    description="Automated workflow to research a topic and then verify its security implications.",
    sub_agents=[w_brain_agent, w_security_agent]
)

# Root Agent - The entry point and supervisor
root_agent = LlmAgent(
    name="Casper_C2_Root",
    model=MODEL_NAME,
    sub_agents=[security_agent, dev_agent, assistant_agent, brain_agent, research_and_verify_workflow],
    instruction=get_root_instruction(),
    parallel_worker=True,
    after_tool_callback=log_tool_usage_callback
)

# Alias for compatibility
casper_agent = root_agent
