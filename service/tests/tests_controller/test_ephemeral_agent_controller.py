import unittest
from unittest.mock import MagicMock, patch

from flask import Flask
from flask_testing import TestCase
from parameterized import parameterized

from controller.ephemeral_agent_controller import (
    construct_ephemeral_agent_blueprint,
)

UA = "Mozilla/5.0 (X11; Linux x86_64; rv:56.0; Waterfox) Gecko/20100101 Firefox/56.2.4"


class TestEphemeralAgentController(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False

        app.register_blueprint(construct_ephemeral_agent_blueprint())
        return app

    def test_agent_request_post(self):
        with patch("cloudscraper.get_cookie_string") as mock_get_cookie_string:
            mock_get_cookie_string.return_value = ("some_cf_clearance_value", UA)
            params = {"disableCloudflareV1": True}
            response = self.client.post(
                "/agent/ephemeral?url=http://example.com",
                content_type="application/json",
                json=params,
            )
            self.assert200(response)
            self.assertEqual(
                response.json,
                {
                    "User-Agent": UA,
                    "cf_clearance": "some_cf_clearance_value",
                },
            )

    def test_agent_request_missing_params(self):
        response = self.client.post("/agent/ephemeral")
        self.assert400(response)
        self.assertEqual(response.json, {"url": ["This field is required."]})

    def test_agent_request_invalid_params(self):
        params = {"interpreter": "javascript"}
        response = self.client.post(
            "/agent/ephemeral?url=http://example.com",
            content_type="application/json",
            json=params,
        )
        self.assert400(response)
        self.assertEqual(
            response.json, {"interpreter": ["Must be one of: native, nodejs, js2py."]}
        )


if __name__ == "__main__":
    unittest.main()
