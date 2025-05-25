from django_rest_passwordreset.models import ResetPasswordToken
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from rest_framework import serializers
from .models import UserProfile, EmailConfirmation
import random
from .utils import send_confirmation_email  # функция для отправки email
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import EmailConfirmation
import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        email = validated_data['email']
        code = str(random.randint(100000, 999999))

        EmailConfirmation.objects.update_or_create(
            email=email,
            defaults={'code': code}
        )

        # Отправка кода на email
        send_mail(
            subject='Ваш код подтверждения',
            message=f'Ваш код подтверждения: {code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return {'email': email}


class ConfirmPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    code = serializers.CharField(write_only=True)

    def validate(self, attrs):
        # проверка кода
        email = attrs.get("email")
        code = attrs.get("code")
        password = attrs.get("password")

        try:
            confirmation = EmailConfirmation.objects.get(email=email, code=code, is_confirmed=False)
        except EmailConfirmation.DoesNotExist:
            raise serializers.ValidationError("Неверный код подтверждения")

        attrs["confirmation"] = confirmation
        return attrs

    def create(self, validated_data):
        confirmation = validated_data["confirmation"]
        email = validated_data["email"]
        password = validated_data["password"]

        # подтверждаем код
        confirmation.is_confirmed = True
        confirmation.save()

        # создаём пользователя
        user, created = User.objects.get_or_create(email=email)
        if created:
            user.set_password(password)
            user.save()

        return user


# login---------------
class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data.get('identifier')
        password = data.get('password')

        user = UserProfile.objects.filter(
            Q(email__iexact=identifier) | Q(phone_number=identifier)
        ).first()

        if user and user.check_password(password):
            if not user.is_active:
                raise serializers.ValidationError("Аккаунт не активен")
            return user

        raise serializers.ValidationError("Неверный логин или пароль")

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'name': instance.name,
                'email': instance.email,
                'phone_number': str(instance.phone_number),
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
# logaut--------------------------
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, data):
        self.token = data['refresh']
        return data

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except Exception as e:
            raise serializers.ValidationError({'detail': 'Недействительный или уже отозванный токен'})


# email password забыл парол 4 значный код -----------------------
class VerifyResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()  # Email пользователя
    reset_code = serializers.IntegerField()  # 4-значный код
    new_password = serializers.CharField(write_only=True)  # Новый пароль

    def validate(self, data):
        email = data.get('email')
        reset_code = data.get('reset_code')

        # Проверяем, существует ли указанный код для email
        try:
            token = ResetPasswordToken.objects.get(user__email=email, key=reset_code)
        except ResetPasswordToken.DoesNotExist:
            raise serializers.ValidationError("Неверный код сброса или email.")

        data['user'] = token.user
        return data

    def save(self):
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']

        # Устанавливаем новый пароль
        user.set_password(new_password)
        user.save()



class QRLoginGenerateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(help_text="ID пользователя, для которого генерируется QR-код")

class QRLoginVerifySerializer(serializers.Serializer):
    qr_token = serializers.CharField(help_text="QR-токен, полученный из изображения")
    password = serializers.CharField(write_only=True, help_text="Пароль пользователя")


