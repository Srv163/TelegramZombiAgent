import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    TG_API_ID: int = int(os.getenv("TG_API_ID", "0"))
    TG_API_HASH: str = os.getenv("TG_API_HASH", "")
    SOURCE_USERNAMES: list[str] = [x.strip() for x in os.getenv("SOURCE_USERNAMES","").split(",") if x.strip()]
    TARGET_CHANNEL_ID: str = os.getenv("TARGET_CHANNEL_ID","")
    BOT_TOKEN: str = os.getenv("BOT_TOKEN","")

    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY") or None

    POSTGRES_DB: str = os.getenv("POSTGRES_DB","zombie")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER","zombie")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD","zombie_password")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST","db")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT","5432"))

    POLL_INTERVAL_SEC: int = int(os.getenv("POLL_INTERVAL_SEC","90"))
    ZOMBIE_LEVEL: int = int(os.getenv("ZOMBIE_LEVEL","2"))
    POST_LENGTH: str = os.getenv("POST_LENGTH","medium")
    PUBLISH_DELAY_MIN: int = int(os.getenv("PUBLISH_DELAY_MIN","45"))
    PUBLISH_DELAY_MAX: int = int(os.getenv("PUBLISH_DELAY_MAX","180"))
    TIMEZONE: str = os.getenv("TIMEZONE","Europe/Amsterdam")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL","INFO")

    SESSION_DIR: str = "/sessions"
    MEDIA_DIR: str = "/media"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()