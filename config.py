from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    model_name: str = "claude-sonnet-4-6"
    max_tokens: int = 4096
    request_timeout: int = 60

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
