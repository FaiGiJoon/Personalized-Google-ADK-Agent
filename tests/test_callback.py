import unittest
from unittest.mock import MagicMock
from core.agent import log_tool_usage_callback

class TestCallback(unittest.TestCase):
    def test_log_tool_usage_callback(self):
        # Mock tool
        tool = MagicMock()
        tool.name = "test_tool"

        # Mock tool_context with state
        tool_context = MagicMock()
        tool_context.state = {}

        # Args and response (can be anything for this test)
        args = {"arg1": "val1"}
        tool_response = {"status": "ok"}

        # Execute callback
        result = log_tool_usage_callback(tool, args, tool_context, tool_response)

        # Verify state was updated
        self.assertIn("tool_history", tool_context.state)
        self.assertEqual(tool_context.state["tool_history"], ["test_tool"])

        # Verify response is returned correctly
        self.assertEqual(result, tool_response)

        # Call again to test accumulation
        log_tool_usage_callback(tool, args, tool_context, tool_response)
        self.assertEqual(tool_context.state["tool_history"], ["test_tool", "test_tool"])

if __name__ == "__main__":
    unittest.main()
