from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Backend API"
    dashscope_api_key: str
    dashscope_model_name: str
    api_prefix: str
    data_dir: str = "data"
    working_dir: str
    database_url: str
    async_database_url: str
    vector_database_url: str
    async_vector_database_url: str
    vector_schema_name: str
    vector_table_name: str
    chat_schema_name: str
    chat_table_name: str
    chunk_size: int = 512
    chunk_overlap: int = 50
    tracer_provider_endpoint: str = "http://localhost:6006/v1/traces"

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()
