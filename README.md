# ТЕСТОВОЕ ЗАДАНИЕ МАГНИТ #

# миграции(если необходимо)
flask db init
flask db migrate -m "users table"
flask db upgrade

# celery
celery -A app.tasks worker -l info --pool=prefork
celery -A app.tasks beat -l info

# настройки
Необходимо создать файл .env c настройками в корне приложения, образец в .env_form

# docker
docker-compose -f dev-docker-compose up -d --build

# test
pytest app/tests.py
