from django.urls import path, include
from .views import (
    RegisterView,
    CustomLoginView,
    LogoutView,
    verify_reset_code,
    QRLoginGenerateView,
    QRLoginVerifyView,
    ConfirmEmailView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Email confirmation
    path('confirm-email/', ConfirmEmailView.as_view(), name='confirm_email'),

    # Сброс пароля (через стороннее приложение)
    path('password_reset/verify_code/', verify_reset_code, name='verify_reset_code'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),

    # QR логин
    path('qr-login/generate/', QRLoginGenerateView.as_view(), name='qr_login_generate'),
    path('qr-login/verify/', QRLoginVerifyView.as_view(), name='qr_login_verify'),
]
