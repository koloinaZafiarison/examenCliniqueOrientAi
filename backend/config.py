from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    database_url: str = "postgresql+psycopg://postgres:Dovahkiin150@localhost:5432/OrientAi"


settings = Settings()
