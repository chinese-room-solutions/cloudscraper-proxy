"""Main entry point for the backend service."""

import logging
from datetime import datetime
from json import dumps, loads
from json.encoder import JSONEncoder

from controller.ephemeral_agent_controller import (
    construct_ephemeral_agent_blueprint,
)
from controller.persistent_agent_controller import construct_persistent_agent_blueprint
from controller.proxy_controller import construct_proxy_blueprint
from flask import Flask
from flask.json.provider import JSONProvider
from flask_smorest import Api
from structlog import get_logger
from utils.agent_pool import AgentPool
from utils.config import Config
from utils.logger import StructlogHandler, setup_logging

config = Config.get_config()
setup_logging(filename=config.log.path, log_level=config.log.level, dev=config.log.dev)
log = get_logger(__name__)


class CustomJSONEncoder(JSONEncoder):
    """Custom JSON encoder to handle datetime objects."""

    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        return super(CustomJSONEncoder, self).default(o)


class CustomJSONProvider(JSONProvider):
    """Custom JSON encoder to handle datetime objects."""

    def dumps(self, obj, **kwargs):
        return dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s: str | bytes, **kwargs):
        return loads(s, **kwargs)


def create_app() -> tuple[Flask, Api]:
    """Create the Flask app."""

    app = Flask(__name__)
    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.addHandler(StructlogHandler())
    werkzeug_logger.setLevel(logging.ERROR)
    werkzeug_logger.propagate = False
    app.json = CustomJSONProvider(app)

    app.config["APPLICATION_ROOT"] = config.root
    app.config["WTF_CSRF_ENABLED"] = False

    app.config["API_TITLE"] = "Cloudscraper Proxy API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/apispec"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    api = Api(app)

    return app, api


def register_blueprints(app: Api, agent_pool: AgentPool):
    """Register the blueprints."""

    app.register_blueprint(construct_persistent_agent_blueprint(agent_pool))
    app.register_blueprint(construct_ephemeral_agent_blueprint())
    app.register_blueprint(construct_proxy_blueprint(agent_pool))


app, api = create_app()
agent_pool = AgentPool()
register_blueprints(api, agent_pool)

if __name__ == "__main__":
    log.info(
        "Starting development Cloudscraper Proxy service.",
        host=config.host,
        port=config.port,
    )
    app.run(
        host=config.host,
        port=config.port,
        threaded=True,
    )
