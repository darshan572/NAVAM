from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Look for .env in current directory or repo root
def find_env_file() -> str:
    for p in [Path.cwd() / ".env", Path(__file__).resolve().parents[3] / ".env", Path(__file__).resolve().parents[2] / ".env"]:
        if p.exists():
            return str(p)
    return ".env"

class Settings(BaseSettings):
    database_url: str = Field(default="postgresql://user:password@localhost/navam")
    database_url_sync: str | None = None
    redis_url: str = Field(default="redis://localhost:6379/0")
    secret_key: str = Field(default="supersecretkey")
    algorithm: str = Field(default="HS256")
    environment: str = Field(default="dev")
    log_level: str = "INFO"
    demo_mode: bool = True
    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "navam"
    keycloak_client_id: str = "navam-api"
    keycloak_client_secret: str = ""
    ml_serving_url: str = "http://localhost:8001"
    mlflow_tracking_uri: str = ""
    martin_url: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=find_env_file(), extra="ignore")

settings = Settings()
