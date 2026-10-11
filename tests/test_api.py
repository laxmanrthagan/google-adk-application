import unittest

from fastapi.testclient import TestClient

from backend_adk.catalog import AGENTS
from backend_adk.main import app


class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_and_agent_catalog(self) -> None:
        health = self.client.get("/api/health")
        catalog = self.client.get("/api/agents")

        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()["provider"], "mock")
        self.assertEqual(catalog.status_code, 200)
        self.assertEqual(len(catalog.json()["agents"]), len(AGENTS))

    def test_every_catalog_agent_runs_through_the_api(self) -> None:
        for agent in AGENTS:
            with self.subTest(agent=agent["id"]):
                response = self.client.post(
                    "/api/run",
                    json={
                        "agent_id": agent["id"],
                        "role": "Staff Platform Engineer",
                        "company": "Northstar",
                        "seniority": "Staff",
                        "job_description": "Python cloud architecture reliability APIs",
                        "question": "Design a reliable event platform",
                        "answer": "I built Python APIs and improved reliability.",
                    },
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["agent"]["id"], agent["id"])
                self.assertEqual(response.json()["provider"], "mock")
                self.assertTrue(response.json()["response"])

    def test_unknown_agent_is_rejected(self) -> None:
        response = self.client.post("/api/run", json={"agent_id": "unknown"})

        self.assertEqual(response.status_code, 404)

    def test_mock_search_bigquery_and_function_tools_run_inside_adk(self) -> None:
        shared_context = {
            "role": "Staff Platform Engineer",
            "company": "Northstar",
            "job_description": "Python cloud reliability APIs",
            "answer": "Built Python APIs",
        }

        search = self.client.post("/api/run", json={**shared_context, "agent_id": "search"}).json()
        bigquery = self.client.post("/api/run", json={**shared_context, "agent_id": "bigquery"}).json()
        skill_match = self.client.post("/api/run", json={**shared_context, "agent_id": "tools"}).json()

        self.assertIn("No live search was performed", search["response"])
        self.assertIn("no cloud query ran", bigquery["response"])
        self.assertIn("Keyword overlap", skill_match["response"])


if __name__ == "__main__":
    unittest.main()