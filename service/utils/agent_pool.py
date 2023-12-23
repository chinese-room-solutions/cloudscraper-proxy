"""Agent pool for proxy service."""

import sys

import cloudscraper


class AgentPool(dict):
    def __init__(self, *args, **kwargs):
        """Initialize the agent pool.

        Args:
            **kwargs: Keyword arguments for cloudscraper. See cloudscraper documentation for more details.
        """

        dict.__init__(self, *args, **kwargs)
        self.agent_id = 0

    def generate(self, **kwargs) -> tuple[int, cloudscraper.CloudScraper]:
        """Generate a new agent.

        Args:
            **kwargs: Keyword arguments for cloudscraper to override self.params parameters.
                See cloudscraper documentation for more details.

        Returns:
            tuple(int, cloudscraper.CloudScraper): The agent id and the agent.
        """

        if self.agent_id == sys.maxsize:
            self.agent_id = 1
        else:
            self.agent_id += 1
        self[self.agent_id] = cloudscraper.create_scraper(**kwargs)

        return self.agent_id, self[self.agent_id]

    def clear(self) -> None:
        """Clear the agent pool."""

        self.agent_id = 0
        return super().clear()
