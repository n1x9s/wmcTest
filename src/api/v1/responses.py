from starlette import status

COMMON_RESPONSES = {
    status.HTTP_401_UNAUTHORIZED: {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "example": {"detail": "Unauthorized"}
            }
        },
    },
    status.HTTP_403_FORBIDDEN: {
        "description": "Нет доступа",
        "content": {
            "application/json": {
                "example": {"detail": "У вас нет прав"}
            }
        },
    },
    status.HTTP_400_BAD_REQUEST: {
        "description": "Ошибка запроса",
        "content": {
            "application/json": {
                "example": {"detail": "Ошибка в запросе"}
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Ошибка сервера",
        "content": {
            "application/json": {
                "example": {"detail": "Внутренняя ошибка сервера"}
            }
        },
    }
}
