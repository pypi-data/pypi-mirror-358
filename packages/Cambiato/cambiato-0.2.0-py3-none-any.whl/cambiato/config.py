r"""The configuration of Cambiato."""

# Standard library
import logging
import os
import sys
import tomllib
from pathlib import Path
from typing import Any

# Third party
import streamlit_passwordless as stp
from pydantic import ConfigDict, Field, field_validator
from sqlalchemy import URL

# Local
from cambiato import exceptions
from cambiato.models.core import BaseModel

logger = logging.getLogger(__name__)


# Name of the program.
PROG_NAME = 'Cambiato'

# The config directory of the program.
CONFIG_DIR = Path.home() / '.config' / PROG_NAME

# The name of the default config file.
CONFIG_FILENAME = f'{PROG_NAME}.toml'

# The full path to the default config file.
CONFIG_FILE_PATH = CONFIG_DIR / CONFIG_FILENAME

# The name of the environment variable, which points to the config file.
CONFIG_FILE_ENV_VAR = 'CAMBIATO_CONFIG_FILE'


class BaseConfigModel(BaseModel):
    r"""The base model that all configuration models inherit from."""

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        try:
            super().__init__(**kwargs)
        except exceptions.CambiatoError as e:
            raise exceptions.ConfigError(str(e)) from None


class DatabaseConfig(BaseConfigModel):
    r"""The database configuration for Cambiato.

    Parameters
    ----------
    url : str or sqlalchemy.URL, default 'sqlite:///Cambiato.db'
        The SQLAlchemy database url of the Cambiato database.

    autoflush : bool, default False
        Automatically flush pending changes within the session
        to the database before executing new SQL statements.

    expire_on_commit : bool, default False
        If True make the connection between the models and the database expire after a
        transaction within a session has been committed and if False make the database models
        accessible after the commit.

    create_database : bool, default True
        If True the database table schema will be created if it does not exist.

    connect_args : dict[Any, Any], default dict()
        Additional arguments sent to the database driver upon
        connection that further customizes the connection.

    engine_config : dict[str, Any], default dict()
        Additional keyword arguments passed to the :func:`sqlalchemy.create_engine` function.
    """

    url: str | URL = Field(default='sqlite:///Cambiato.db', validate_default=True)
    autoflush: bool = False
    expire_on_commit: bool = False
    create_database: bool = True
    connect_args: dict[Any, Any] = Field(default_factory=dict)
    engine_config: dict[str, Any] = Field(default_factory=dict)

    @field_validator('url')
    @classmethod
    def validate_url(cls, url: str | URL) -> stp.db.URL:
        r"""Validate the database url."""

        try:
            return stp.db.create_db_url(url)
        except stp.DatabaseInvalidUrlError as e:
            raise ValueError(f'{type(e).__name__} : {str(e)}') from None


class ConfigManager(BaseConfigModel):
    r"""Handles the configuration of Cambiato.

    Parameters
    ----------
    config_file_path : Path or None, default None
        The path to the config file from which the configuration was loaded.
        The special path '-' specifies that the config was loaded from stdin.
        If None the default configuration was loaded.

    database : cambiato.DatabaseConfig
        The database configuration.
    """

    model_config = ConfigDict(frozen=True)

    config_file_path: Path | None = None
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)


def load_config(path: Path | None = None) -> ConfigManager:
    r"""Load the configuration of Cambiato.

    The configuration can be loaded from four different sources listed
    below in the order in which they will override each other:

    1. A specified config file to `path` parameter.

    2. From stdin by specifying the `path` `pathlib.Path('-')`.

    3. A config file specified in environment variable "CAMBIATO_CONFIG_FILE".

    4. From the default config file location "~/.config/Cambiato/Cambiato.toml".

    5. If none of the above the default configuration will be loaded.

    Parameters
    ----------
    path : pathlib.Path or None, default None
        The path to the config file. Specify `Path('-')` for stdin. If None the configuration
        will be loaded from the config file environment variable "CAMBIATO_CONFIG_FILE" if it
        exists otherwise from the default config file at "~/.config/Cambiato/Cambiato.toml".
        If none of these sources exist the default configuration will be loaded.

    Returns
    -------
    ConfigManager
        An instance of the program's configuration.

    Raises
    ------
    cambiato.ConfigError
        If the configuration is invalid.

    cambiato.ConfigFileNotFoundError
        If the configuration file could not be found.

    cambiato.ParseConfigError
        If there are syntax errors in the config file.
    """

    if path is None:
        if (_file_path := os.getenv(CONFIG_FILE_ENV_VAR)) is None:
            file_path = CONFIG_FILE_PATH
        else:
            file_path = Path(_file_path)
    else:
        if path.name == '-':  # stdin
            file_path = None
        else:
            file_path = path

    if file_path:
        file_path_str = str(file_path)
        if file_path.is_dir():
            error_msg = f'The config file "{file_path}" must be a file not a directory!'
            raise exceptions.ConfigFileNotFoundError(message=error_msg, data=file_path)

        if file_path == CONFIG_FILE_PATH:
            if file_path.exists():
                config_content = file_path.read_text()
            else:
                config_content = None
        elif not file_path.exists():
            error_msg = f'The config file "{file_path}" does not exist!'
            raise exceptions.ConfigFileNotFoundError(message=error_msg, data=file_path)
        else:
            config_content = file_path.read_text()
    else:
        file_path_str = '-'
        config_content = sys.stdin.read()

    if not config_content:
        return ConfigManager(config_file_path=None)

    config_content = f"config_file_path = '{file_path_str}'\n{config_content}"

    try:
        config_from_toml = tomllib.loads(config_content)
    except (tomllib.TOMLDecodeError, TypeError) as e:
        error_msg = f'Syntax error in config : {e.args[0]}'
        raise exceptions.ParseConfigError(error_msg) from None

    return ConfigManager.model_validate(config_from_toml)
