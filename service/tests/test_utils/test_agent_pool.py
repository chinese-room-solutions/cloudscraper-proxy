import unittest
from unittest.mock import MagicMock, patch

from utils.agent_pool import AgentPool


class TestAgentPool(unittest.TestCase):
    def test_generate(self):
        with patch("utils.agent_pool.cloudscraper") as mock_cloudscraper:
            # Mock the cloudscraper create_scraper function
            mock_cloudscraper.create_scraper.return_value = MagicMock()

            # Create an AgentPool and generate an agent
            agent_pool = AgentPool()
            agent_id, agent = agent_pool.generate()

            # Assert the agent id and agent
            self.assertEqual(agent_id, 0)
            self.assertEqual(agent, mock_cloudscraper.create_scraper.return_value)

            # Generate another agent and assert the agent id and agent
            agent_id, agent = agent_pool.generate()
            self.assertEqual(agent_id, 1)
            self.assertEqual(agent, mock_cloudscraper.create_scraper.return_value)


if __name__ == "__main__":
    unittest.main()
