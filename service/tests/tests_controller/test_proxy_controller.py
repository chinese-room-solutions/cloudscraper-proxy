import unittest
from unittest.mock import MagicMock, patch

from flask import Flask
from flask_testing import TestCase

from controller.proxy_controller import construct_proxy_blueprint, filter_headers


class TestProxyController(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False

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

    def test_proxy_request_valid_agent(self):
        response = self.client.get("/proxy?agent_id=0&dst=http://example.com")
        self.assert200(response)
        self.assertEqual(response.data, b"response content")

    def test_proxy_request_invalid_agent(self):
        response = self.client.get("/proxy?agent_id=1&dst=http://example.com")
        self.assert404(response)

    def test_proxy_request_missing_params(self):
        response = self.client.get("/proxy?agent_id=0")
        self.assert400(response)
        self.assertEqual(response.json, {"dst": ['Missing data for required field.']})

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
