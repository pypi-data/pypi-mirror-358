from pydantic import (
    BaseSettings,
)


class Settings(BaseSettings):
    """Settings."""

    api_token: str = "change_me"
    gui_password: str = "change_me"
    database_path: str = "./rabbitmq-consumer-log-server.db"
    views_directory: str = "views"
    static_files_directory: str = "static"
    keep_days: int = 45

    class Config:
        """Config."""

        secrets_dir = "/etc/rabbitmq-consumer-log-server"


settings = Settings()
