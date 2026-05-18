import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the current directory to sys.path to ensure we can import local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from google.adk.runners import Runner
from google.adk.sessions import PersistentSessionService
from google.genai import types
from agent import personal_agent
from database import SESSION_URL

load_dotenv()

async def run_chat():
    print(f"\n{'='*60}\n🌟 MY PERSONAL AGENT 🌟\n{'='*60}")
    
    # Initialize Persistent Session Service
    session_service = PersistentSessionService(url=SESSION_URL)
    
    user_id = "jules_user"
    app_name = personal_agent.name

    # Check for existing sessions or create a new one
    sessions = await session_service.list_sessions(app_name=app_name, user_id=user_id)
    if sessions:
        session = sessions[0]
        print(f"🔄 Resuming existing session: {session.id}")
    else:
        session = await session_service.create_session(app_name=app_name, user_id=user_id)
        print(f"🆕 Created new session: {session.id}")

    runner = Runner(
        agent=personal_agent,
        session_service=session_service,
        app_name=app_name
    )

    print("\nAssistant is ready! (Type 'exit' or 'quit' to stop)\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input:
                continue

            print("\nThinking...", end="\r")
            
            final_response = ""
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=types.Content(parts=[types.Part(text=user_input)], role="user")
            ):
                if event.is_final_response():
                    final_response = event.content.parts[0].text
            
            print(f"Agent: {final_response}\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"An error occurred: {e}")

    print(f"\n{'='*60}\n👋 GOODBYE!\n{'='*60}")

if __name__ == "__main__":
    # If GEMINI_API_KEY is not set, warn the user
    if not os.getenv("GOOGLE_API_KEY") and not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_CLOUD_PROJECT"):
        print("⚠️ Warning: No API key or Project ID found. Please set GOOGLE_API_KEY or GOOGLE_CLOUD_PROJECT.")
    
    try:
        asyncio.run(run_chat())
    except EOFError:
        pass
