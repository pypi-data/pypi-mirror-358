import os
import time
import socket
from dotenv import load_dotenv
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

# Set up logger
logger = logging.getLogger("audittrail")
logger.setLevel(logging.DEBUG)
logger.propagate = True


class Settings(BaseSettings):
    # AppAuth Settings
    application_name: str = ""
    application_version: str = ""
    # Logging Settings
    elasticsearch_url: str = ""
    mongodb_url: str = ""
    hostname: str = socket.gethostname()
    ip_address: str = socket.gethostbyname(hostname)
    env_file: str = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(dotenv_path=env_file)
    model_config = SettingsConfigDict(env_file=env_file)


@lru_cache(maxsize=1)
def get_audittrail_setting() -> Settings:
    return Settings()


def init_audittrail(
    application_name: str,
    application_version: str,
    elasticsearch_url: str,
    mongodb_url: str,
):

    env_file = os.path.join(os.path.dirname(__file__), ".env")
    with open(env_file, "w") as f:
        f.write(f'application_name="{application_name}"\n')
        f.write(f'application_version="{application_version}"\n')
        f.write(f'elasticsearch_url="{elasticsearch_url}"\n')
        f.write(f'mongodb_url="{mongodb_url}"\n')

    time.sleep(3)
    os.chmod(env_file, 0o777)
    # load the settings
    audittrail_settings = get_audittrail_setting().model_dump()
    # print("Audittrail settings: ", audittrail_settings)


if __name__ == "__main__":
    init_audittrail(
        application_name="test_application",
        application_version="1.0.0",
        elasticsearch_url="http://localhost:9200",
        mongodb_url="mongodb://localhost:27017",
    )
