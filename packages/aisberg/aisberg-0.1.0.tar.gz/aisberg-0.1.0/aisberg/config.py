from typing import Union

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Variables attendues
    aisberg_api_key: Union[str, None] = None
    aisberg_base_url: Union[str, None] = None
    timeout: int = 30

    # Pour indiquer le fichier .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Singleton partagé dans tout le SDK
settings = Settings()
