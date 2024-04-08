from yaml_settings_pydantic import BaseYamlSettings
from functools import lru_cache


class Config(BaseYamlSettings):
    __yaml_files__ = 'config.yaml'
    devices: list
    pushgateway: dict


@lru_cache()
def getConfig():
    return Config()
