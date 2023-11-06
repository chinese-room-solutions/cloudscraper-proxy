import unittest
from unittest.mock import MagicMock

from controller.persistent_agent_controller import (
    construct_persistent_agent_blueprint,
)
from flask_testing import TestCase
from main import create_app
from parameterized import parameterized
from utils.dotdict import dotdict

UA = "Mozilla/5.0 (X11; Linux x86_64; rv:56.0; Waterfox) Gecko/20100101 Firefox/56.2.4"


class TestPersistentAgentController(TestCase):
    def create_app(self):
        app, _ = create_app()
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

    @parameterized.expand(
        [
            (
                "valid-agent",
                "/agent/persistent/0",
                dotdict(
                    {
                        "status_code": 200,
                        "json": {"user_agent": UA, "cf_clearance": ""},
                    }
                ),
            ),
            (
                "non-existing-agent",
                "/agent/persistent/1",
                dotdict(
                    {"status_code": 404, "json": {"code": 404, "status": "Not Found"}}
                ),
            ),
        ]
    )
    def test_agent_request_get(self, name, url, expected):
        response = self.client.get(url)
        self.assertEqual(response.status_code, expected.status_code)
        self.assertEqual(response.json, expected.json)

    @parameterized.expand(
        [
            (
                "valid-params",
                {"disableCloudflareV1": True},
                dotdict({"status_code": 201, "json": {"id": 0}}),
            ),
            (
                "invalid-params",
                {"interpreter": "javascript"},
                dotdict(
                    {
                        "status_code": 422,
                        "json": {
                            "code": 422,
                            "status": "Unprocessable Entity",
                            "errors": {
                                "json": {
                                    "interpreter": [
                                        "Must be one of: native, nodejs, js2py."
                                    ]
                                }
                            },
                        },
                    }
                ),
            ),
        ]
    )
    def test_agent_request_post(self, name, params, expected):
        self.mock_agent_pool.generate.return_value = (0, MagicMock())
        response = self.client.post(
            "/agent/persistent", content_type="application/json", json=params
        )
        if name == "valid-params":
            self.mock_agent_pool.generate.assert_called_once_with(**params)
        self.assertEqual(response.status_code, expected.status_code)
        self.assertEqual(response.json, expected.json)

    @parameterized.expand(
        [
            (
                "one-agent",
                "/agent/persistent/0",
                dotdict({"status_code": 200, "json": {"id": 0}}),
            ),
            (
                "non-existing-agent",
                "/agent/persistent/1",
                dotdict(
                    {"status_code": 404, "json": {"code": 404, "status": "Not Found"}}
                ),
            ),
            (
                "all-agents",
                "/agent/persistent",
                dotdict({"status_code": 200, "json": {"message": "All agents deleted"}}),
            ),
        ]
    )
    def test_agent_request_delete(self, name, url, expected):
        response = self.client.delete(url)
        if name == "one-agent":
            self.mock_agent_pool.pop.assert_called_once_with(0, None)
        if name == "all-agents":
            self.mock_agent_pool.clear.assert_called_once()
        self.assertEqual(response.status_code, expected.status_code)
        self.assertEqual(response.json, expected.json)


if __name__ == "__main__":
    unittest.main()
