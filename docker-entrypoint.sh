#!/bin/sh

echo "Making migrations"
poetry run alembic revision --autogenerate

# Находим последний созданный файл в migrations/versions
LAST_MIGRATION_FILE=$(ls -t migrations/versions | head -n 1)

# Проверяем, существует ли файл, и добавляем строку импорта, если нужно
if [ -n "$LAST_MIGRATION_FILE" ]; then
  echo 'import fastapi_users_db_sqlalchemy' | cat - migrations/versions/"$LAST_MIGRATION_FILE" > temp && mv temp migrations/versions/"$LAST_MIGRATION_FILE"
  echo "Added import statement to $LAST_MIGRATION_FILE"
fi

echo "Upgrading DB by latest migration"
poetry run alembic upgrade head

echo "Running Gunicorn server"
poetry run gunicorn -k uvicorn.workers.UvicornWorker -w 4 --bind 0.0.0.0:8100 --access-logfile - --error-logfile - src.main:app
