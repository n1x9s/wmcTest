import os
import smtplib
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from loguru import logger
from pydantic import Field
from pydantic.v1 import BaseSettings, validator, root_validator

dotenv_path = os.path.join(os.path.dirname(__file__), '../../', '.env')
load_dotenv()


class Config(BaseSettings):
    # DOCKER_IMAGE_VERSION: str = Field(..., env='DOCKER_IMAGE_VERSION')

    POSTGRES_USER: str = Field(..., env='POSTGRES_USER')
    POSTGRES_PASSWORD: str = Field(..., env='POSTGRES_PASSWORD')
    POSTGRES_DB: str = Field(..., env='POSTGRES_DB')
    POSTGRES_HOST: str = Field(..., env='POSTGRES_HOST')
    POSTGRES_PORT: int = Field(..., env='POSTGRES_PORT')

    # SMTP_SERVER: str = Field(..., env='SMTP_SERVER')
    # SMTP_PORT: int = Field(..., env='SMTP_PORT')
    # SMTP_USER: str = Field(..., env='SMTP_USER')
    # SMTP_PASSWORD: str = Field(..., env='SMTP_PASSWORD')

    JWT_SECRET: str = Field(..., env='JWT_SECRET')

    COOKIE_MAX_AGE: int = Field(..., env='COOKIE_MAX_AGE')

    JWT_ACCESS_LIFETIME_SECONDS: int = Field(..., env='JWT_ACCESS_LIFETIME_SECONDS')
    JWT_REFRESH_LIFETIME_SECONDS: int = Field(..., env='JWT_REFRESH_LIFETIME_SECONDS')

    CORS_ORIGINS: str = Field(..., env='CORS_ORIGINS')

    BASE_DIR: Path = Path(__file__).parent.parent.parent  # это на уровне с файлом .env

    # Валидация на пустые поля
    @validator("*", pre=True)
    def check_empty_str(cls, value, field):
        if isinstance(value, str) and not value.strip():
            raise ValueError(f"'{field.name}' не может быть пустым")
        return value

    @root_validator
    def check_postgres_connection(cls, values):
        try:
            conn = psycopg2.connect(
                host=values['POSTGRES_HOST'],
                port=values['POSTGRES_PORT'],
                database=values['POSTGRES_DB'],
                user=values['POSTGRES_USER'],
                password=values['POSTGRES_PASSWORD']
            )
            conn.close()
        except psycopg2.OperationalError as e:
            raise ValueError(f"Ошибка подключения к PostgreSQL: {e}")
        except Exception as e:
            raise ValueError(f"Postgres Error: {e}")
        return values

    # @root_validator
    # def check_smtp_connection(cls, values):
    #     try:
    #         with smtplib.SMTP(values['SMTP_SERVER'], values['SMTP_PORT']) as server:
    #             server.starttls()  # Включаем TLS шифрование
    #             server.login(values['SMTP_USER'], values['SMTP_PASSWORD'])
    #     except smtplib.SMTPAuthenticationError as e:
    #         raise ValueError(f"Ошибка аутентификации SMTP: {e}")
    #     except smtplib.SMTPConnectError as e:
    #         raise ValueError(f"Ошибка подключения к SMTP серверу: {e}")
    #     except smtplib.SMTPException as e:
    #         raise ValueError(f"Ошибка SMTP: {e}")
    #     except Exception as e:
    #         raise ValueError(f"SMTP Error: {e}")
    #     return values


config = Config()
logger.info("Config loaded: {}", config.dict())
