import unittest
from unittest.mock import MagicMock

from flask import Flask
from flask_testing import TestCase
from parameterized import parameterized

from controller.persistent_agent_controller import (
    construct_persistent_agent_blueprint,
)
from utils.dotdict import dotdict

UA = "Mozilla/5.0 (X11; Linux x86_64; rv:56.0; Waterfox) Gecko/20100101 Firefox/56.2.4"


class TestPersistentAgentController(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config["TESTING"] = True

        # Mock agent functionality
        mock_agent = MagicMock()
        mock_agent.cookies.get_dict.return_value = {"cf_clearance": ""}
        mock_agent.headers.get.return_value = UA

        # Mock agent pool functionality
        self.mock_agent_pool = MagicMock()
        self.mock_agent_pool.__contains__.side_effect = (
            lambda key: True if key == 0 else False
        )
        self.mock_agent_pool.__getitem__.return_value = mock_agent

        app.register_blueprint(construct_persistent_agent_blueprint(self.mock_agent_pool))
        return app

    def test_agent_request_post(self):
        params = {"disableCloudflareV1": True}
        self.mock_agent_pool.generate.return_value = (0, MagicMock())
        response = self.client.post(
            "/agent/persistent", content_type="application/json", json=params
        )
        self.mock_agent_pool.generate.assert_called_once_with(**params)
        self.assert200(response)
        self.assertEqual(response.json, {"id": 0})

    def test_agent_request_delete(self):
        response = self.client.delete("/agent/persistent/0")
        self.assert200(response)
        self.mock_agent_pool.pop.assert_called_once_with(0, None)

        response = self.client.delete("/agent/persistent")
        self.assert200(response)
        self.mock_agent_pool.clear.assert_called_once()

    @parameterized.expand(
        [
            (
                "/agent/persistent/0",
                dotdict(
                    {"status_code": 200, "json": {"User-Agent": UA, "cf_clearance": ""}}
                ),
            ),
            ("/agent/persistent/1", dotdict({"status_code": 404, "json": None})),
        ]
    )
    def test_agent_request_get(self, url, expected):
        response = self.client.get(url)
        self.assertEqual(response.status_code, expected.status_code)
        self.assertEqual(response.json, expected.json)


if __name__ == "__main__":
    unittest.main()
