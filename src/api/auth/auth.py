import uuid
from typing import Optional

import jwt
from fastapi_users.authentication import JWTStrategy, AuthenticationBackend, BearerTransport
from jwt import ExpiredSignatureError, InvalidTokenError

from src.config import config

from wms_services.models import User
# For using Bearer
bearer_transport = BearerTransport(tokenUrl="api/auth/jwt/login")

SECRET = config.JWT_SECRET


class CustomJWTStrategy(JWTStrategy):
    async def read_token(self, token: str, user_manager) -> Optional[User]:
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            user_id = payload.get("subject", {}).get("sub")

            if user_id:
                user = await user_manager.get(uuid.UUID(user_id, version=4))
                return user
            return None
        except (jwt.PyJWTError, ValueError):
            return None


def get_jwt_strategy() -> JWTStrategy:
    return CustomJWTStrategy(secret=SECRET, lifetime_seconds=config.JWT_ACCESS_LIFETIME_SECONDS)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


async def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
        return payload
    except ExpiredSignatureError:
        raise Exception("Token has expired")
    except InvalidTokenError:
        raise Exception("Invalid token")
    except Exception as e:
        raise Exception("Something went wrong. May be the token has another key")
