import os
import uuid

from fastapi_users import FastAPIUsers
from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.api.auth.auth import auth_backend
from src.api.auth.manager import get_user_manager
from wms_services.models import User
from . import config

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)


DATABASE_URL = f"postgresql+asyncpg://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}"


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


def ensure_directory_exists(pathdirs: list[list[str]]):
    """
    ensure_directory_exists([["src", "assets"], ["src", "assets", "reports"]])
    :param pathdirs:
    :return:
    """
    for path in pathdirs:
        pathdir = config.BASE_DIR.joinpath(*path)
        if not os.path.exists(pathdir):
            os.makedirs(pathdir)
            logger.info(f"Directory '{pathdir}' created.")
        else:
            logger.info(f"Directory '{pathdir}' already exists.")


# REPORT_DIR = config.BASE_DIR.joinpath("src", "assets", "reports")
