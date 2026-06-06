import unittest
import os
import json
import shutil
from pathlib import Path
from memory.database import setup_user_db, USER_DB_FILE
from memory.tools import update_knowledge_graph, recall_user_profile, save_user_profile
from memory.vector_tools import index_document, query_technical_docs
from skills.models import KnowledgeEntitySchema, UserProfileSchema, DocumentIndexSchema, VectorQuerySchema

class MockSession:
    def __init__(self, user_id="TestUser"):
        self.user_id = user_id
        self.id = "test_session_id"

class MockToolContext:
    def __init__(self, session, state=None):
        self.session = session
        self.state = state if state is not None else {}

class TestMemoryLevels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use a temporary database for testing
        cls.test_db = Path("memory/test_user_profile.db")
        if cls.test_db.exists():
            os.remove(cls.test_db)

        # Patch USER_DB_FILE in modules
        import memory.database
        import memory.tools
        memory.database.USER_DB_FILE = cls.test_db
        memory.tools.USER_DB_FILE = cls.test_db

        setup_user_db()

    @classmethod
    def tearDownClass(cls):
        if cls.test_db.exists():
            os.remove(cls.test_db)

    def test_level_2_multi_agent_state(self):
        """Test sharing state between turns."""
        session = MockSession()
        state = {}
        context = MockToolContext(session, state)

        entity = KnowledgeEntitySchema(
            entity_name="TestProject",
            entity_type="Project",
            details="A test project",
            metadata={"priority": "high"}
        )

        update_knowledge_graph(context, entity)

        self.assertIn("latest_entities", state)
        self.assertEqual(state["latest_entities"][-1], "TestProject")

    def test_level_3_and_5_persistence_and_custom_tools(self):
        """Test long-term persistence and structured user profile/KG."""
        session = MockSession("Casper")
        context = MockToolContext(session)

        # Save preference
        pref = UserProfileSchema(new_preferences={"theme": "dark"})
        save_user_profile(context, pref)

        # Recall
        data = recall_user_profile(context)
        self.assertEqual(data["preferences"]["theme"], "dark")

        # Check seeded data (Level 5)
        found_casper = False
        for entity in data["knowledge_graph"]:
            if entity["name"] == "Casper":
                found_casper = True
                self.assertIn("Netherlands", entity["details"])
                self.assertEqual(entity["metadata"]["location"], "Netherlands")
        self.assertTrue(found_casper)

    def test_level_6_multimodal_memory(self):
        """Test multimodal metadata in vector search."""
        test_file = "tests/test_multimodal.txt"
        with open(test_file, "w") as f:
            f.write("This is a test document for multimodal memory.\n\nIt contains info about a QR code scan.")

        try:
            doc_data = DocumentIndexSchema(
                filepath=test_file,
                metadata={"media_type": "image", "description": "QR Code for login"}
            )
            index_document(doc_data)

            query_data = VectorQuerySchema(query="QR code scan")
            results = query_technical_docs(query_data)

            found = False
            for res in results:
                if "metadata" in res and res["metadata"].get("media_type") == "image":
                    found = True
                    self.assertEqual(res["metadata"]["description"], "QR Code for login")
            self.assertTrue(found, "Multimodal metadata not found in results")
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

if __name__ == "__main__":
    unittest.main()
