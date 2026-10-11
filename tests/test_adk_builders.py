import unittest
from unittest.mock import patch

import google.auth.credentials
from google.adk.agents import LoopAgent, LlmAgent, ParallelAgent, SequentialAgent

from backend_adk.adk_agents import BUILDERS, SystemDesignRouter


class AdkBuilderTests(unittest.TestCase):
    def test_every_adk_builder_constructs_without_live_credentials(self) -> None:
        mock_credentials = google.auth.credentials.AnonymousCredentials()

        with patch("google.auth.default", return_value=(mock_credentials, "test-project")):
            agents = {agent_id: builder("mock") for agent_id, builder in BUILDERS.items()}

        self.assertEqual(len(agents), 9)
        self.assertIsInstance(agents["basic"], LlmAgent)
        self.assertIsInstance(agents["llm"], LlmAgent)
        self.assertIsInstance(agents["sequential"], SequentialAgent)
        self.assertIsInstance(agents["parallel"], ParallelAgent)
        self.assertIsInstance(agents["loop"], LoopAgent)
        self.assertIsInstance(agents["custom"], SystemDesignRouter)
        self.assertIsInstance(agents["search"], LlmAgent)
        self.assertIsInstance(agents["tools"], LlmAgent)
        self.assertIsInstance(agents["bigquery"], LlmAgent)

    def test_bigquery_toolset_is_read_only(self) -> None:
        mock_credentials = google.auth.credentials.AnonymousCredentials()

        with patch("google.auth.default", return_value=(mock_credentials, "test-project")):
            agent = BUILDERS["bigquery"]("vertex")

        self.assertEqual(agent.tools[0]._tool_settings.write_mode.value, "blocked")


if __name__ == "__main__":
    unittest.main()