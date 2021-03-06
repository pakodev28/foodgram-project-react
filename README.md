[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)


## Описание:

Онлайн-сервис Foodgram и API. Сервис предоставляет возможность пользователям публиковать свои рецепты. Есть возможность подписаться на понравившихся авторов рецептов. Добавть рецепт в список покупок и скачать его.


## Как развернуть проект:
1. Склонировать проект, перейти в папку infra, настроить .env файл:
    ```
    git clone git@github.com:pakodev28/foodgram-project-react.git
    ```
    ```
    cd infra
    ```
    ```
    copy .env.example .env
    ```
2. для запуска контейнеров:
    ```
    docker-compose up -d
    ```
3. Далее выполните следующие команды:
    ```
    docker-compose exec web python manage.py migrate --noinput
    ```
    ```
    docker-compose exec web python manage.py collectstatic
    ```
4. Можете загрузить датасет ингредиентов в БД:
    ```
    docker-compose exec web python manage.py load_data
    ```
5. Создайте суперпользователя:
    ```
    docker-compose exec web python manage.py createsuperuser
    ```


### Технологии использованные в проекте
- Python 3.8
- Django 3.2
- DRF
- Gunicorn
- PostgreSQL
- Docker
- Nginx

*backend - https://github.com/pakodev28*

*frontend - https://github.com/yandex-praktikum*
