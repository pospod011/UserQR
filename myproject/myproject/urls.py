from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Episyche Technologies API",
        default_version='v1',
        description="""
📌 Регистрация пользователя
POST /register/
Описание: Отправка email и получение 6-значного кода подтверждения.
Request JSON:
{
  "email": "user@example.com"
}
Response JSON:
{
  "detail": "Код отправлен на email"
}

✅ Подтверждение email и установка пароля
POST /confirm_password/
Описание: Подтверждение 6-значного кода и установка пароля. Возвращает access и refresh токены.
Request JSON:
{
  "email": "user@example.com",
  "code": "123456",
  "password": "your_password"
}
Response JSON:
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token"
}

🔐 Логин (email или телефон)
POST /login/
Описание: Логин по email или номеру телефона и паролю. Возвращает access и refresh токены.
Request JSON:
{
  "identifier": "user@example.com",
  "password": "your_password"
}
Response JSON:
{
  "user": {
    "name": "User Name",
    "email": "user@example.com",
    "phone_number": "123456789"
  },
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token"
}

🚪 Логаут
POST /logout/
Описание: Выход из аккаунта, токен добавляется в blacklist.
Request JSON:
{
  "refresh": "jwt_refresh_token"
}
Response JSON:
{
  "detail": "Вы вышли из системы."
}

🔁 Сброс пароля — подтверждение кода
POST /password_reset/verify_code/
Описание: Подтверждение 4-значного кода и установка нового пароля.
Request JSON:
{
  "email": "user@example.com",
  "reset_code": 1234,
  "new_password": "newpassword123"
}
Response JSON:
{
  "message": "Пароль успешно сброшен."
}

🛠 Отправка самого кода сброса
POST /password_reset/
Описание: Отправка 4-значного кода на email (используется django-rest-passwordreset).

📷 Генерация QR-кода для логина
POST /qr-login/generate/
Описание: Генерация QR-кода и токена по ID пользователя.
Request JSON:
{
  "user_id": 1
}
Response JSON:
{
  "qr_code": "data:image/png;base64,...",
  "qr_token": "uuid-string"
}

🔑 Логин по QR и паролю
POST /qr-login/verify/
Описание: Подтверждение QR токена и логин с паролем.
Request JSON:
{
  "qr_token": "uuid-string",
  "password": "your_password"
}
Response JSON:
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "user": {
    "email": "user@example.com",
    "name": "User Name"
  }
}
        """,
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)




urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('profil.urls')),  # все пути из профиля
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
)

