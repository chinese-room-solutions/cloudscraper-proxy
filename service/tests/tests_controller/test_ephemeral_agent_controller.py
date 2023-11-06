import unittest
from unittest.mock import patch

from controller.ephemeral_agent_controller import (
    construct_ephemeral_agent_blueprint,
)
from flask_testing import TestCase
from main import create_app
from parameterized import parameterized
from utils.dotdict import dotdict

UA = "Mozilla/5.0 (X11; Linux x86_64; rv:56.0; Waterfox) Gecko/20100101 Firefox/56.2.4"


class TestEphemeralAgentController(TestCase):
    def create_app(self):
        app, _ = create_app()
        app.config["TESTING"] = True
        app.register_blueprint(construct_ephemeral_agent_blueprint())
        return app

    @parameterized.expand(
        [
            (
                "ok",
                "/agent/ephemeral?url=http://example.com",
                {"disableCloudflareV1": True},
                dotdict(
                    {
                        "status_code": 201,
                        "json": {
                            "user_agent": UA,
                            "cf_clearance": "some_cf_clearance_value",
                        },
                    }
                ),
            ),
            (
                "missing-params",
                "/agent/ephemeral",
                {},
                dotdict(
                    {
                        "status_code": 422,
                        "json": {
                            "code": 422,
                            "status": "Unprocessable Entity",
                            "errors": {
                                "query": {"url": ["Missing data for required field."]}
                            },
                        },
                    }
                ),
            ),
            (
                "invalid-params",
                "/agent/ephemeral?url=http://example.com",
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
    def test_agent_request_post(self, name, url, params, expected):
        with patch("cloudscraper.get_cookie_string") as mock_get_cookie_string:
            mock_get_cookie_string.return_value = ("some_cf_clearance_value", UA)
            response = self.client.post(
                url,
                content_type="application/json",
                json=params,
            )
            self.assertEqual(response.status_code, expected.status_code)
            self.assertEqual(response.json, expected.json)


if __name__ == "__main__":
    unittest.main()
