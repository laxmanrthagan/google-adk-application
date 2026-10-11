import unittest

from backend_adk.mock_model import MockInterviewModel


class MockModelTests(unittest.TestCase):
    def test_mock_model_uses_an_adk_model_id_and_tool_capabilities(self) -> None:
        model = MockInterviewModel(model="gemini-2.5-flash", agent_key="skill_match_agent")

        self.assertEqual(model.agent_key, "skill_match_agent")
        self.assertTrue(model.capabilities.output_schema_and_tools)


if __name__ == "__main__":
    unittest.main()