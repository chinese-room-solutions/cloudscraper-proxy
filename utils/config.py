"""This module is responsible for providing configuration to the application."""

from os import getenv
from typing import Optional

from pydantic import BaseModel, Field, validator
from yaml import YAMLError, load
from yaml.loader import BaseLoader


class LogConfig(BaseModel):
    """Log configuration class.

    Attributes:
        path (str): The log file path.
        level (str): The log level.
        dev (bool): Whether to use the pretty development renderer or not.
    """

    path: str = Field(None, description="Path to log file.")
    level: str = Field("INFO", description="Log level.")
    dev: bool = Field(
        True, description="Whether to use the pretty development renderer or not."
    )

    @classmethod
    @validator("level")
    def validate_level(cls, v):
        """Validate the log level."""

        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError("Invalid log level.")
        return v


class Config(BaseModel):
    """Config class for the proxy service, loads configuration from yaml config file.

    Attributes:
        host (str): The host of the application.
        port (int): The port of the application.
        root (str): The root endpoint path of the application.
        log (LogConfig): The log configuration.
    """

    host: str = Field("0.0.0.0", description="The host of the application.")
    port: int = Field(8080, gt=0, lt=65536, description="The port of the application.")
    root: str = Field("/", description="The root endpoint path of the application.")
    log: Optional[LogConfig] = Field(
        default_factory=LogConfig, description="The log configuration."
    )

    @classmethod
    def get_config(cls, env_var: str = "CLOUDSCRAPER_PROXY_CONFIG_PATH"):
        """
        Load the configuration either from environment variables or from
        a yaml config file.

        Args:
            env_var (str, optional): The environment variable to use to load the config
                file path. Defaults to "CLOUDSCRAPER_PROXY_CONFIG_PATH".
        """

        path = getenv(env_var, "config.yml")
        try:
            with open(path, encoding="utf8") as file:
                data = load(file, Loader=BaseLoader) or {}
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not find the configuration file at {path}.")
        except YAMLError as ex:
            raise YAMLError(
                f"There was an error parsing the configuration file at {path}: {ex}."
            )

        config = cls(**data)

        # Update the instance with values from environment variables.
        config.host = getenv("CLOUDSCRAPER_PROXY_HOST", config.host)
        config.port = int(getenv("CLOUDSCRAPER_PROXY_PORT", config.port))
        config.root = getenv("CLOUDSCRAPER_PROXY_WEB_ROOT", config.root)

        config.log.path = getenv("CLOUDSCRAPER_PROXY_LOG_PATH", config.log.path)
        config.log.level = getenv("CLOUDSCRAPER_PROXY_LOG_LEVEL", config.log.level)
        dev = getenv("CLOUDSCRAPER_PROXY_LOG_DEV", config.log.dev)
        config.log.dev = dev or dev == "True"

        return config
