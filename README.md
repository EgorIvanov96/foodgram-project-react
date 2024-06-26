# Foodgram Project - "Продуктовый помощник"

## Foodgram - это сеть для обмена рецептами.


## Основные возможности:
 - создавать аккаунты
 - создавать рецепты
 - подписываться на любимых пользователей
 - добавлять в избранное понравившиеся рецепты 
 - скачивать список продуктов, рецептов, которые вы хотите приготовить


## Данные для входа администратора:

```bash
логин: Admin@gmail.com 

пароль: admin
```

## Технологии

Проект "Foodgram" использует следующие технологии:

- Python
- Django
- Django REST framework
- HTML/CSS
- JavaScript


## Установка

1. Склонируйте репозиторий с помощью команды:

```bash
git clone git@github.com:EgorIvanov96/foodgram-project-react .git
```

2. Установите Docker

2. Перейдите в папку с проектом:

```bash
cd foodgram-project-react
```

3. Создайте файл .env в корне проекта:

```bash
POSTGRES_USER=Имя пользователя для подключения к базе данных.
```

```bash
POSTGRES_PASSWORD=Пароль для подключения к базе данных PostgreSQL.
```

```bash
POSTGRES_DB=Имя базы данных PostgreSQL, с которой вы хотите подключиться.
```

```bash
DB_HOST=Хост базы данных PostgreSQL. В данном случае, значение должно быть 'db'.
```

```bash
DB_PORT=Порт, на котором работает база данных PostgreSQL. В данном случае, значение должно быть '5432'
```

```bash
SECRET_KEY= Секретный ключ, используемый для аутентификации и безопасности вашего приложения.
```

```bash
ALLOWED_HOSTS=Список хостов, которые можно разрешить для доступа к вашему приложению. Вы можете указать конкретные имена хостов, разделяя их запятыми.
```

```bash
DEBUG=Определите значение как 'True', если вы хотите включить режим отладки для вашего приложения.
```

4. Запустите файл docker-compose.production.yml:

```bash
docker compose -f docker-compose.production.yml up
```


## Автор

- Egor Ivanov - [@EgorIvanov96](https://github.com/EgorIvanov96)

