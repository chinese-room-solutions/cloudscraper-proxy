import unittest
from unittest.mock import MagicMock

from controller.proxy_controller import construct_proxy_blueprint, filter_headers
from flask_testing import TestCase
from main import create_app
from parameterized import parameterized
from utils.dotdict import dotdict


class TestProxyController(TestCase):
    def create_app(self):
        app, _ = create_app()
        app.config["TESTING"] = True

        # Mock agent pool functionality
        self.mock_agent_pool = MagicMock()
        self.mock_agent_pool.__contains__.side_effect = (
            lambda key: True if key == 0 else False
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.content = b"response content"
        mock_response.iter_content.return_value = [mock_response.content]
        self.mock_agent_pool.__getitem__.return_value = MagicMock(
            request=MagicMock(return_value=mock_response)
        )

        app.register_blueprint(construct_proxy_blueprint(self.mock_agent_pool))
        return app

    @parameterized.expand(
        [
            (
                "valid-agent",
                "/proxy?agent_id=0&dst=http://example.com",
                dotdict(
                    {
                        "status_code": 200,
                        "data": b"response content",
                    }
                ),
            ),
            (
                "non-existent-agent",
                "/proxy?agent_id=1&dst=http://example.com",
                dotdict(
                    {
                        "status_code": 404,
                        "json": {"code": 404, "status": "Not Found"},
                    }
                ),
            ),
            (
                "missing-params",
                "/proxy?agent_id=0",
                dotdict(
                    {
                        "status_code": 422,
                        "json": {
                            "code": 422,
                            "status": "Unprocessable Entity",
                            "errors": {
                                "query": {"dst": ["Missing data for required field."]}
                            },
                        },
                    }
                ),
            ),
        ]
    )
    def test_proxy_request_get(self, name, url, expected):
        response = self.client.get(url)
        self.assertEqual(response.status_code, expected.status_code)
        if expected.data is not None:
            self.assertEqual(response.data, expected.data)
        if expected.json is not None:
            self.assertEqual(response.json, expected.json)

    def test_filter_headers(self):
        headers = {
            "Accept": "text/html",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Host": "example.com",
            "User-Agent": "test-agent",
            "X-Custom-Header": "custom-value",
        }

        filtered = filter_headers(headers)
        self.assertNotIn("Accept", filtered)
        self.assertNotIn("Accept-Encoding", filtered)
        self.assertNotIn("Connection", filtered)
        self.assertNotIn("Host", filtered)
        self.assertNotIn("User-Agent", filtered)
        self.assertIn("X-Custom-Header", filtered)
        self.assertEqual(filtered["X-Custom-Header"], "custom-value")


if __name__ == "__main__":
    unittest.main()
