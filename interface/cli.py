import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is in sys.path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from google.adk.runners import Runner
    from google.adk.sessions.sqlite_session_service import SqliteSessionService
    from google.genai import types
    ADK_COMPONENTS_AVAILABLE = True
except ImportError:
    print("Warning: google.adk or google.genai modules not found. CLI will run in mock mode.")
    ADK_COMPONENTS_AVAILABLE = False

from core.agent import casper_agent, load_system_prompt, get_root_instruction
from memory.database import SESSION_URL, SESSION_DB_FILE

load_dotenv()

async def get_user_input(prompt: str) -> str:
    """Non-blocking input using asyncio.to_thread."""
    return await asyncio.to_thread(input, prompt)

async def run_chat():
    print(f"\n{'='*60}\nCASPER C2 AGENT\n{'='*60}")

    user_id = "Casper"
    app_name = casper_agent.name

    if ADK_COMPONENTS_AVAILABLE:
        # Initialize SQLite Session Service
        # SqliteSessionService expects a path, not a URL
        session_service = SqliteSessionService(db_path=str(SESSION_DB_FILE))

        # Check for existing sessions or create a new one
        response = await session_service.list_sessions(app_name=app_name, user_id=user_id)
        if response.sessions:
            session = response.sessions[0]
            print(f"Resuming existing C2 session: {session.id}")
        else:
            session = await session_service.create_session(app_name=app_name, user_id=user_id)
            print(f"Created new C2 session: {session.id}")

        runner = Runner(
            agent=casper_agent,
            session_service=session_service,
            app_name=app_name
        )
    else:
        print("Running in MOCK MODE - ADK not installed.")
        session = type('obj', (object,), {'id': 'mock_session'})()

    print("\nCasper C2 is ready! (Type 'exit' or 'quit' to stop)\n")
    print("Special Commands: /mode [Security|Dev|Assistant|Brain]\n")

    while True:
        try:
            # Use non-blocking input
            user_input = (await get_user_input("Casper: ")).strip()

            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input:
                continue

            # Mode switching command
            if user_input.startswith("/mode "):
                mode_name = user_input.split(" ", 1)[1].strip()
                new_instruction = load_system_prompt(f"{mode_name} Mode")
                # In multi-agent mode, we update the root_agent's general guidance
                casper_agent.instruction = get_root_instruction(new_instruction)
                print(f"\n[SYSTEM] Root Agent guidance updated to: {mode_name} Mode")
                print(f"[SYSTEM] The Root Agent will still orchestrate between specialized sub-agents.")
                print(f"{'-'*40}\n")
                continue

            print("\nProcessing...", end="\r")

            if ADK_COMPONENTS_AVAILABLE:
                final_response = ""
                # runner.run_async allows for non-blocking streaming of responses
                async for event in runner.run_async(
                    user_id=user_id,
                    session_id=session.id,
                    new_message=types.Content(parts=[types.Part(text=user_input)], role="user")
                ):
                    if event.is_final_response():
                        final_response = event.content.parts[0].text

                print(f"Agent: {final_response}\n")
            else:
                # Simulate some async work in mock mode
                await asyncio.sleep(0.5)
                print(f"Agent: [MOCK] I received your message: '{user_input}'. Current Mode: {casper_agent.instruction[:20]}...\n")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"An error occurred: {e}")

    print(f"\n{'='*60}\nDISCONNECTING CASPER C2...\n{'='*60}")

if __name__ == "__main__":
    # If GEMINI_API_KEY is not set, warn the user
    if not os.getenv("GOOGLE_API_KEY") and not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_CLOUD_PROJECT"):
        print("Warning: No API key or Project ID found. Please set GOOGLE_API_KEY or GOOGLE_CLOUD_PROJECT.")

    try:
        asyncio.run(run_chat())
    except EOFError:
        pass
