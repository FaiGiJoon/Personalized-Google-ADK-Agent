import unittest
import asyncio
import os
import shutil
import json
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

# Force mock mode for ADK if needed, but here we want to test the real logic with mocked LLM
from core.agent import casper_agent
from memory.database import setup_user_db, USER_DB_FILE
import memory.database
import memory.tools

# ADK imports
from google.adk.runners import Runner
from google.adk.sessions.sqlite_session_service import SqliteSessionService
from google.genai import types

class TestVirtualAgentSession(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Setup temporary databases
        self.test_dir = Path("tests/tmp_virtual_test")
        self.test_dir.mkdir(parents=True, exist_ok=True)

        self.user_db = self.test_dir / "test_user_profile.db"
        self.session_db = self.test_dir / "test_sessions.db"

        # Patch the database paths
        self.patcher1 = patch("memory.database.USER_DB_FILE", self.user_db)
        self.patcher2 = patch("memory.tools.USER_DB_FILE", self.user_db)
        self.patcher1.start()
        self.patcher2.start()

        setup_user_db()

        self.session_service = SqliteSessionService(db_path=str(self.session_db))
        self.app_name = "CasperC2_VirtualTest"
        self.user_id = "VirtualCasper"
        self.runner = Runner(
            agent=casper_agent,
            session_service=self.session_service,
            app_name=self.app_name
        )

    async def asyncTearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    @patch("google.genai.Client")
    async def test_full_session_flow(self, mock_client_class):
        """Simulate a multi-turn session with tool calls and state verification."""

        # Mocking the Gemini client and its async methods
        mock_client = mock_client_class.return_value

        # --- TURN 1: Validate Snort Rule ---
        transfer_call = types.Part(
            function_call=types.FunctionCall(
                name="transfer_to_agent",
                args={"agent_name": "Security_Agent"}
            )
        )
        resp1_root = types.GenerateContentResponse(
            candidates=[types.Candidate(content=types.Content(parts=[transfer_call], role="model"), finish_reason="STOP")]
        )

        snort_call = types.Part(
            function_call=types.FunctionCall(
                name="validate_snort_rule",
                args={"rule": 'alert tcp any any -> any 80 (msg:"Test"; sid:1000001;)'}
            )
        )
        resp2_security = types.GenerateContentResponse(
            candidates=[types.Candidate(content=types.Content(parts=[snort_call], role="model"), finish_reason="STOP")]
        )

        resp3_final = types.GenerateContentResponse(
            candidates=[types.Candidate(content=types.Content(parts=[types.Part(text="The Snort rule is valid.")], role="model"), finish_reason="STOP")]
        )

        mock_client.aio.models.generate_content = AsyncMock(side_effect=[resp1_root, resp2_security, resp3_final])

        session = await self.session_service.create_session(app_name=self.app_name, user_id=self.user_id)

        async for event in self.runner.run_async(
            user_id=self.user_id,
            session_id=session.id,
            new_message=types.Content(parts=[types.Part(text="Check this snort rule.")], role="user")
        ):
            pass

        # Verify Tool History (Level 4 Memory)
        session_data = await self.session_service.get_session(session_id=session.id, app_name=self.app_name, user_id=self.user_id)
        state = session_data.state
        self.assertIn("tool_history", state)
        self.assertIn("transfer_to_agent", state["tool_history"])

        # --- TURN 2: Knowledge Graph Update ---
        transfer_brain = types.Part(
            function_call=types.FunctionCall(
                name="transfer_to_agent",
                args={"agent_name": "Brain_Agent"}
            )
        )
        resp4_root = types.GenerateContentResponse(
            candidates=[types.Candidate(content=types.Content(parts=[transfer_brain], role="model"), finish_reason="STOP")]
        )

        # Brain_Agent calls update_knowledge_graph.
        # Nested structure as expected by Pydantic model in ADK
        kg_call = types.Part(
            function_call=types.FunctionCall(
                name="update_knowledge_graph",
                args={
                    "entity_data": {
                        "entity_name": "VirtualProject",
                        "entity_type": "Project",
                        "details": "High priority project",
                        "metadata": {"priority": "high"}
                    }
                }
            )
        )
        resp5_brain = types.GenerateContentResponse(
            candidates=[types.Candidate(content=types.Content(parts=[kg_call], role="model"), finish_reason="STOP")]
        )

        resp6_final = types.GenerateContentResponse(
            candidates=[types.Candidate(content=types.Content(parts=[types.Part(text="Updated.")], role="model"), finish_reason="STOP")]
        )

        mock_client.aio.models.generate_content.side_effect = [resp4_root, resp5_brain, resp6_final]

        async for event in self.runner.run_async(
            user_id=self.user_id,
            session_id=session.id,
            new_message=types.Content(parts=[types.Part(text="Remember VirtualProject priority.")], role="user")
        ):
            pass

        # Verify Level 5 Memory (Persistence in User DB)
        from memory.tools import recall_user_profile
        class MockContext:
            def __init__(self, user_id):
                self.session = MagicMock(user_id=user_id)

        profile = recall_user_profile(MockContext(self.user_id))
        found = False
        for entity in profile["knowledge_graph"]:
            if entity["name"] == "VirtualProject":
                found = True
                self.assertEqual(entity["type"], "Project")
                self.assertEqual(entity["details"], "High priority project")
        self.assertTrue(found, "VirtualProject entity was not found in Knowledge Graph")

        # Verify Level 2 Memory (State in Session)
        session_data = await self.session_service.get_session(session_id=session.id, app_name=self.app_name, user_id=self.user_id)
        self.assertIn("latest_entities", session_data.state)
        self.assertIn("VirtualProject", session_data.state["latest_entities"])

if __name__ == "__main__":
    unittest.main()
