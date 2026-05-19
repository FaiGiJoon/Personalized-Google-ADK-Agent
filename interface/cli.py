import asyncio
import os
import sys
from dotenv import load_dotenv

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from google.adk.runners import Runner
    from google.adk.sessions import PersistentSessionService
    from google.genai import types
    ADK_COMPONENTS_AVAILABLE = True
except ImportError:
    print("Warning: google.adk or google.genai modules not found. CLI will run in mock mode.")
    ADK_COMPONENTS_AVAILABLE = False

from core.agent import casper_agent, load_system_prompt
from memory.database import SESSION_URL

load_dotenv()

async def run_chat():
    print(f"\n{'='*60}\nCASPER C2 AGENT\n{'='*60}")

    user_id = "Casper"
    app_name = casper_agent.name

    if ADK_COMPONENTS_AVAILABLE:
        # Initialize Persistent Session Service
        session_service = PersistentSessionService(url=SESSION_URL)

        # Check for existing sessions or create a new one
        sessions = await session_service.list_sessions(app_name=app_name, user_id=user_id)
        if sessions:
            session = sessions[0]
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
    print("Special Commands: /mode [Security|Dev|Assistant]\n")

    while True:
        try:
            user_input = input("Casper: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input:
                continue

            # Mode switching command
            if user_input.startswith("/mode "):
                mode_name = user_input.split(" ", 1)[1].strip()
                new_instruction = load_system_prompt(f"{mode_name} Mode")
                casper_agent.instruction = new_instruction
                print(f"Switched to {mode_name} Mode.\n")
                continue

            print("\nProcessing...", end="\r")

            if ADK_COMPONENTS_AVAILABLE:
                final_response = ""
                async for event in runner.run_async(
                    user_id=user_id,
                    session_id=session.id,
                    new_message=types.Content(parts=[types.Part(text=user_input)], role="user")
                ):
                    if event.is_final_response():
                        final_response = event.content.parts[0].text

                print(f"Agent: {final_response}\n")
            else:
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
