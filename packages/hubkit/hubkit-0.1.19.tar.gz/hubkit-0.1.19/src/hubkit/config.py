import logging
import os
import tomllib

DEFAULT_CONFIG_PATH = "~/.config/hubkit/config.toml"
CONFIG_PATH_ENV_VAR = "HUBKIT_CONFIG_PATH"


def load_config():
    """
    Load configuration from TOML file.
    Returns the config dictionary or exits if configuration file is missing or invalid.
    """
    config_path = DEFAULT_CONFIG_PATH
    if CONFIG_PATH_ENV_VAR in os.environ:
        config_path = os.environ[CONFIG_PATH_ENV_VAR]

    if not os.path.exists(os.path.expanduser(config_path)):
        logging.error(f"Config file not found at {config_path}. Please create it with the required settings.")
        exit(1)

    with open(os.path.expanduser(config_path), "rb") as f:
        try:
            return tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            logging.error(f"Error parsing config file: {e}")
            exit(1)


def get_requestbin_config():
    """
    Get RequestBin specific configuration.
    Returns a tuple of (server_url, requestbin_app, access_token).
    Exits if any required configuration is missing.
    """
    config = load_config()

    server_url = config.get('server', {}).get('url')
    requestbin_app = config.get('requestbin', {}).get('app')
    access_token = config.get('requestbin', {}).get('access_token')

    if server_url is None or requestbin_app is None or access_token is None:
        logging.error("Missing required RequestBin configuration")
        exit(1)

    return server_url, requestbin_app, access_token
