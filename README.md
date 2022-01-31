## Описание:

Онлайн-сервис Foodgram и API. Сервис предоставляет возможность пользователям публиковать свои рецепты. Есть возможность подписаться на понравившихся авторов рецептов. Добавть рецепт в список покупок и скачать его.


### Адрес http://51.250.20.252/

### Данные для входа на сайт login: guest@qq.com password: guest12345qq


## Как пазвернуть проект:
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
- PostgreSQL
- Docker
- Nginx

*backend - pakodev28*

*frontend - студенты факультета web-разработки Я.Практикума*
