<h1 align="center">CloneTweeter</h1>
Данный сервис является клоном Tweeter

Бэкенд реализован на фреймворке FastApi. База данных PostgreSQL.
Так же в сервисе есть мониторинг работы приложения

## Основой функционал приложения:

1. Регистрация и авторизация пользователя
2. Зарегистрированный пользователь может добавить и удалить твит, добавить картинку к твиту
3. Зарегистрированный пользователь может подписаться на другого пользователя
4. Зарегистрированный пользователь может отписаться от другого пользователя
5. Зарегистрированный пользователь может лайкнуть твит другого пользователя.
6. Пользователь может убрать отметку «Нравится».
7. Пользователь может посмотреть профиль другого пользователя 

### 1. Регистрация и авторизация пользователя
Для регистрации используется email и пароль

<p align="center">
<img  src="./images_md/register.png" width="80%" alt="">
</p>

После регистрации в базе данных появится информация о пользователе и будет возможность зайти на сервис
с почтой и паролем

<p align="center">
<img  src="./images_md/signin.png" width="80%" alt="">
</p>

Основная страница:
<p align="center">
<img  src="./images_md/main.png" width="80%" alt="">
</p>


### 2. Добавление и удаление твита
Твит добавляется на главной станице нажатием кнопки "Твитнуть"
<p align="center">
<img src="./images_md/add-tweet.gif" width="80%" alt="">
</p>

Удаление твита возможно выбором в меню твита, пункта "Удалить"
<p align="center">
<img src="./images_md/delete-tweet.gif" width="80%" alt="">
</p>

Добавление картинки
<p align="center">
<img src="./images_md/upload_media.gif" width="80%" alt="">
</p>

### 3. Добавление подписки на другого пользователя
<p align="center">
<img src="./images_md/follow.gif" width="80%" alt="">
</p>

### 4. Удаление подписки на другого пользователя
<p align="center">
<img src="./images_md/unfollow.gif" width="80%" alt="">
</p>

### 5. Лайк твита
<p align="center">
<img src="./images_md/like.gif" width="80%" alt="">
</p>

### 6. Удаление лайка твита
<p align="center">
<img src="./images_md/unlike.gif" width="80%" alt="">
</p>

### 7. Просмотр профиля другого пользователя 
<p align="center">
<img src="./images_md/profile_other.gif" width="80%" alt="">
</p>

### 8. Просмотр своего профиля 
<p align="center">
<img src="./images_md/profile_owner.gif" width="80%" alt="">
</p>


## Перед первым запуском
Необходимо переименовать .env.template в .env и внести необходимые данные
## Первый запуск сервиса
```
docker compose up --build -d
```
## Повторный запуск
```
docker compose up -d
```
После этого сервис будет доступен по адресу http://127.0.0.1:81/, если запускать локально,
или по адресу http://ip_server:81/, если запускать на сервере

## Остановка сервиса
```
docker compose down
```

Подробная Swagger документация по api сервиса 
доступна по адресу http://127.0.0.1:8000/docs или http://ip_server:8000/docs

Перед выполнением запросов в Swagger нужно сначала зарегистрироваться и использовать полученный ApiKey
<p align="center">
<img src="./images_md/swagger_register.gif" width="80%" alt="">
</p>

Либо войти и получить существующий ApiKey из базы данных
<p align="center">
<img src="./images_md/swagger_signin.gif" width="80%" alt="">
</p>