import unittest
import os
import json
import sqlite3
import tempfile
from pathlib import Path

from memory.database import setup_user_db
from memory.vector_tools import get_execution_device
from skills.hardware_skills import get_hardware_optimization_config, HARDWARE_PROFILES
from skills.models import HardwareConfigSchema

class TestHardwareProfiles(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_user_profile.db"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_database_hardware_profile_seeding(self):
        """Verify that MacBook Neo and Alienware x17 R2 entities are seeded in SQLite database."""
        # Create a temporary DB file
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_graph (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                entity_name TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                details TEXT,
                metadata TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, entity_name)
            );""")

            # Seed entities
            hardware_entities = [
                ('MacBook Neo', 'HardwareProfile', 'Apple Silicon MacBook laptop setup', '{"os": "macOS", "acceleration": "MPS/Metal"}'),
                ('Alienware x17 R2', 'HardwareProfile', 'Alienware x17 R2 workstation laptop', '{"os": "Windows/Linux", "acceleration": "CUDA"}')
            ]
            conn.executemany("""
                INSERT OR IGNORE INTO knowledge_graph (user_id, entity_name, entity_type, details, metadata)
                VALUES ('Casper', ?, ?, ?, ?);
            """, hardware_entities)

            # Query back
            rows = conn.execute("""
                SELECT entity_name, entity_type, metadata FROM knowledge_graph WHERE entity_type = 'HardwareProfile'
            """).fetchall()

            names = [r[0] for r in rows]
            self.assertIn("MacBook Neo", names)
            self.assertIn("Alienware x17 R2", names)

            for name, etype, meta_str in rows:
                meta = json.loads(meta_str)
                if name == "MacBook Neo":
                    self.assertEqual(meta.get("acceleration"), "MPS/Metal")
                elif name == "Alienware x17 R2":
                    self.assertEqual(meta.get("acceleration"), "CUDA")

    def test_vector_device_detection(self):
        """Verify that get_execution_device returns a valid PyTorch device string."""
        device = get_execution_device()
        self.assertIn(device, ["cuda", "mps", "cpu"])

    def test_hardware_skills_macbook_neo(self):
        """Verify hardware configuration skill for MacBook Neo."""
        config = get_hardware_optimization_config(
            HardwareConfigSchema(target_hardware="MacBook Neo", local_model_name="gemma2:9b")
        )
        self.assertEqual(config["target_hardware"], "MacBook Neo")
        self.assertEqual(config["configured_model"], "gemma2:9b")
        self.assertEqual(config["specifications"]["platform"], "macOS")
        self.assertEqual(config["specifications"]["acceleration"], "Metal Performance Shaders (MPS) / MLX")

    def test_hardware_skills_alienware(self):
        """Verify hardware configuration skill for Alienware x17 R2."""
        config = get_hardware_optimization_config(
            HardwareConfigSchema(target_hardware="Alienware x17 R2", local_model_name="llama3:70b-quant")
        )
        self.assertEqual(config["target_hardware"], "Alienware x17 R2")
        self.assertEqual(config["configured_model"], "llama3:70b-quant")
        self.assertEqual(config["specifications"]["gpu"], "NVIDIA GeForce RTX 3080 Ti (16GB VRAM)")
        self.assertEqual(config["specifications"]["acceleration"], "NVIDIA CUDA / Tensor Cores")

if __name__ == "__main__":
    unittest.main()
