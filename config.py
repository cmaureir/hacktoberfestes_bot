import configparser
import os

from logger import get_logger

LOGGER = get_logger(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_config(base_dir=BASE_DIR):
    config_file = os.path.join(base_dir, 'config.ini')
    if os.path.exists(config_file):
        # This is for local deploy with a config file
        config = configparser.ConfigParser()
        config.read(config_file)
        LOGGER.info("Configuration loaded from config file", extra={'file': config_file})
    else:
        # This is for Heroku where configvars are set as environ variables
        config = {
            "DEFAULT": {
                "Token": os.environ.get("Token"),
                "Guild": os.environ.get("Guild"),
                "Channel": os.environ.get("Channel"),
                "AdminChannel": os.environ.get("AdminChannel"),
                "Role": os.environ.get("Role"),
                "List": os.environ.get("List"),
                "ValidationField": os.environ.get("ValidationField")
            }
        }
        LOGGER.info("Configuration loaded from environment variables")
    return config
