"""This module is responsible for providing configuration to the application using marshmallow."""

from os import getenv

import yaml
from entity.agent import PersistentAgentRequestDataShema
from marshmallow import Schema, ValidationError, fields, post_load, validates


class LogConfig:
    """Log configuration class."""

    def __init__(self, path, level, dev):
        self.path = path
        self.level = level
        self.dev = dev


class LogConfigSchema(Schema):
    """Schema for log configuration."""

    path = fields.Str(missing=None, description="Path to log file.")
    level = fields.Str(missing="INFO", description="Log level.")
    dev = fields.Boolean(
        missing=True, description="Use the pretty development renderer or not."
    )

    @validates("level")
    def validate_level(self, value):
        """Validate the log level."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if value.upper() not in allowed_levels:
            raise ValidationError("Invalid log level.")

    @post_load
    def make_log_config(self, data, **kwargs):
        """Create a LogConfig object after loading."""
        return LogConfig(**data)


class ConfigSchema(Schema):
    """Schema for the main configuration."""

    host = fields.Str(missing="0.0.0.0", description="The host of the application.")
    port = fields.Int(
        missing=5000,
        strict=True,
        validate=lambda p: 0 < p < 65536,
        description="The port of the application.",
    )
    root = fields.Str(
        missing="/", description="The root endpoint path of the application."
    )
    log = fields.Nested(LogConfigSchema, missing=LogConfigSchema().load({}))
    proxy = fields.List(
        fields.Nested(
            PersistentAgentRequestDataShema,
            missing=PersistentAgentRequestDataShema().load({}),
            description="The default Cloudscraper Proxy configuration.",
        ),
        missing=[{}],
    )

    @post_load
    def make_config(self, data, **kwargs):
        """Create a Config object after loading."""
        return Config(**data)


class Config:
    """Config class for the proxy service."""

    def __init__(self, host, port, root, log, proxy):
        self.host = host
        self.port = port
        self.root = root
        self.log = log
        self.proxy = proxy

    @classmethod
    def parse_config(cls, env_var="CLOUDSCRAPER_PROXY_CONFIG_PATH"):
        """
        Load the configuration either from environment variables or from a yaml config file.
        """
        path = getenv(env_var, "config.yml")
        data = {}
        try:
            with open(path, "r", encoding="utf8") as file:
                data = yaml.safe_load(file)
        except FileNotFoundError:
            pass
        except yaml.YAMLError as ex:
            raise yaml.YAMLError(
                f"There was an error parsing the configuration file at {path}: {ex}."
            )

        config_schema = ConfigSchema()
        config = config_schema.load(data)

        # Update the instance with values from environment variables.
        config.host = getenv("CLOUDSCRAPER_PROXY_HOST", config.host)
        config.port = int(getenv("CLOUDSCRAPER_PROXY_PORT", config.port))
        config.root = getenv("CLOUDSCRAPER_PROXY_WEB_ROOT", config.root)

        config.log.path = getenv("CLOUDSCRAPER_PROXY_LOG_PATH", config.log.path)
        config.log.level = getenv("CLOUDSCRAPER_PROXY_LOG_LEVEL", config.log.level)
        dev = getenv("CLOUDSCRAPER_PROXY_LOG_DEV", str(config.log.dev))
        config.log.dev = dev.lower() == "true"

        return config
