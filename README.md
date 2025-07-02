# WMS REST API

## Запуск

!! Создать файл `.env` в корне и наполнить необходимыми переменными (см. `.env.example`)

Если менялась структура БД или первый запуск, то после запуска следует проверить, что применились ли миграции, если нет, то применить их вручную, выполнив команды в интерактивном виде внутри контейнера

```shell
docker exec -it restapi sh -c "poetry run alembic upgrade head"
```

!! При перезапуске Backend, если изменилась кодовая база, следует удалить старые контейнеры, удалить старый образ и создать новый, достаточно выполнить `docker compose up -d`, который сам соберет образ, если его не существует. **ИЛИ** изменить значение `IMAGE_VERSION` в `.env` и собрать новый образ

### Нативно

Для разработки можно запускать, используя uvicorn

Установка зависимостей

```shell
poetry install
```

```shell
poetry run uvicorn src.main:app
```

### Docker compose (рекомендуется для продакшена)

!! Необходимо создать Docker сеть

```shell
docker network create wms-restapi
```

```shell
docker compose up -d
```

Web RESP API: http://127.0.0.1:8400/

Docs: http://127.0.0.1:8400/docs

### Test окружение

!!! тестовое окружение запускается в докере

1. Создать тестовую сеть

```shell
docker network create wms-restapi-test 
```

2. Создать файл `.env.test` в корне проекта и наполнить его (за пример брать `env.example`)
3. запустить тестовый композ файл

```shell
docker compose --env-file .env.test -f docker-compose-test.yaml up -d
```

Web RESP API: http://127.0.0.1:8401/

Docs: http://127.0.0.1:8401/docs

## Миграции

Создание миграции

```shell
poetry run alembic revision --autogenerate
```

это сгенерирует файл миграции в папке `migrations/version` в корне проекта

Применить миграцию

```shell
poetry run alembic upgrade head
```

это применяет миграцию к БД

## Возможные ошибки

### Миграции

При применении миграции может быть ошибка

```shell
NameError: name 'fastapi_users_db_sqlalchemy' is not defined
```

надо исправить созданный файл миграции (в корне проекта в папке `migrations/version`), а именно добавить в него импорт

```python
import fastapi_users_db_sqlalchemy
```

После чего попробовать снова применить миграцию (не создавать новую, а именно применить)

## Как происходит работа с тестовым окружением

1. Создается ветка `test`
2. В нее пушатся фичи
3. На продакшене надо сделать `pull` из этой ветки и запустить контейнеры
4. Когда тестирование завершено, открываем `pull request` из тестовой ветки в основную
5. На продакшене делаем `pull` из основной ветки и запускаем контейнеры

## Архитектура проекта

```
restapi/
├── src/                    
│   ├── __init__.py
│   ├── main.py             # Главный файл FastAPI-приложения, короче говоря точка входа
│   ├── config/             
│   │   ├── __init__.py
│   │   ├── settings.py     # Основные настройки приложения, читаемые из env-файлов
│   ├── api/                
│   │   ├── __init__.py
│   │   ├── v1/             
│   │   │   ├── __init__.py
│   │   │   ├── schemas     # Pydantic схемы для API
│   │   │   │    ├── __init__.py
│   ├── services/           # Бизнес-логика и сервисы
│   │   ├── __init__.py
│   ├── models/             # Схемы данных БД
│   │   ├── __init__.py
│   │   ├── database.py     # Модели для БД
│   ├── utils/              # Утилиты и вспомогательные функции
│   │   ├── __init__.py
├── celery_app/             # Celery конфигурация и задачи
│   ├── __init__.py
│   ├── tasks/              # Задачи Celery
│   │   ├── __init__.py
├── tests/                  
│   ├── __init__.py
├── .env                    
├── docker-compose.yml      
├── Dockerfile
├── poetry.lock
├── pyproject.toml
└── README.md
```
