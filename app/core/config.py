from fastapi_mail import ConnectionConfig
from pydantic import EmailStr, PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    PROJECT_NAME: str
    DEBUG_MODE: bool = False
    API_V1_STR: str = "v1"

    DB_DRIVER: str | None = None
    DB_SERVER: str | None = None
    DB_PORT: int | None = None
    DB_DATABASE: str | None = None
    DB_USERNAME: str | None = None
    DB_PASSWORD: str | None = None

    # admin acount (Opsional)
    ADMIN_USERNAME: str | None = ""
    ADMIN_PASSWORD: str | None = ""
    ADMIN_EMAIL: EmailStr | None = "admin@example.com"

    # JWT
    JWT_SECRET_KEY: str
    JWT_LIFETIME_SECONDS: int = 604800  # 7 days
    JWT_AUDIENCE: str = "users:auth"

    RESET_PASSWORD_SECRET_KEY: str
    RESET_PASSWORD_LIFETIME_SECONDS: int = 3600  # 1 hours

    VERIFICATION_SECRET_KEY: str
    VERIFICATION_LIFETIME_SECONDS: int = 3600  # 1 hours

    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_USERNAME: str | None = None
    MAIL_FROM: str | None = None
    MAIL_PASSWORD: str | None = None
    MAIL_SSL_TLS: bool = True

    CLOUDINARY_CLOUD_NAME: str | None = None
    CLOUDINARY_API_KEY: str | None = None
    CLOUDINARY_API_SECRET: str | None = None

    @computed_field
    @property
    def db_url(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme=self.DB_DRIVER,
            username=self.DB_USERNAME,
            password=self.DB_PASSWORD,
            host=self.DB_SERVER,
            port=self.DB_PORT,
            path=self.DB_DATABASE,
        )  # type: ignore

    @computed_field
    @property
    def mail_config(self) -> ConnectionConfig:
        return ConnectionConfig(
            MAIL_USERNAME=self.MAIL_USERNAME,
            MAIL_PASSWORD=self.MAIL_PASSWORD,
            MAIL_FROM=self.MAIL_FROM,
            MAIL_PORT=self.MAIL_PORT,
            MAIL_SERVER=self.MAIL_SERVER,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=self.MAIL_SSL_TLS,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
        )


def _singleton(cls):
    _instances = {}

    def warp():
        if cls not in _instances:
            _instances[cls] = cls()
        return _instances[cls]

    return warp


Settings = _singleton(Settings)  # type: ignore


def get_settings() -> "Settings":
    """Mendapatkan setting

    Returns
    -------
        Settings: instance settings

    """
    return Settings()  # type: ignore


settings = get_settings()

if __name__ == "__main__":
    print(settings)
