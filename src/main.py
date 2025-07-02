import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.api.auth.router import router as auth_backend_router, users_router
from src.api.auth.schemas import UserRead, UserCreate, UserUpdate
from src.api.v1.routers.profile_router import router as profile_router
from src.api.v1.routers.wb_accounts_router import router as wb_accounts_router
from src.config import config
from src.config.loader import fastapi_users, ensure_directory_exists

app = FastAPI(
    title="WMS Rest API",
    # version=config.DOCKER_IMAGE_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS.split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(profile_router, prefix="/api/v1")
app.include_router(wb_accounts_router, prefix="/api/v1")

app.include_router(auth_backend_router, prefix="/api")
app.include_router(users_router, prefix="/api")


app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/api/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/api/users",
    tags=["users"],
)


@app.on_event("startup")
async def startup_event():
    ensure_directory_exists(
        [
            ["src", "assets"],
            ["src", "assets", "reports"]
        ]
    )
