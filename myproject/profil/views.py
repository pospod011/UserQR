from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    RegisterSerializer, LoginSerializer, LogoutSerializer,
    VerifyResetCodeSerializer,
    QRLoginGenerateSerializer, QRLoginVerifySerializer
)
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RegisterSerializer, ConfirmPasswordSerializer
from rest_framework.decorators import api_view
from rest_framework import status, permissions
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import qrcode
import io
import base64
import uuid


User = get_user_model()


class RegisterView(APIView):
    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={200: openapi.Response("email", RegisterSerializer)}
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Код отправлен на email'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmPasswordView(APIView):
    @swagger_auto_schema(
        request_body=ConfirmPasswordSerializer,
        responses={200: openapi.Response("confirm email", ConfirmPasswordSerializer)}
    )
    def post(self, request):
        serializer = ConfirmPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomLoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh токен отсутствует."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Вы вышли из системы."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail": "Ошибка обработки токена."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def verify_reset_code(request):
    serializer = VerifyResetCodeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Пароль успешно сброшен.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class QRLoginGenerateView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=QRLoginGenerateSerializer,
        responses={200: openapi.Response("QR Code", QRLoginGenerateSerializer)}
    )
    def post(self, request):
        serializer = QRLoginGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data.get("user_id")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден"}, status=404)

        qr_token = str(uuid.uuid4())
        user.qr_token = qr_token
        user.save()

        qr = qrcode.make(qr_token)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        return Response({
            "qr_code": f"data:image/png;base64,{qr_base64}",
            "qr_token": qr_token
        }, status=200)

class QRLoginVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=QRLoginVerifySerializer,
        responses={200: "JWT токены и данные пользователя"}
    )
    def post(self, request):
        serializer = QRLoginVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        qr_token = serializer.validated_data['qr_token']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(qr_token=qr_token)
        except User.DoesNotExist:
            return Response({"detail": "Неверный или просроченный QR-код"}, status=404)

        if not user.check_password(password):
            return Response({"detail": "Неверный пароль"}, status=400)

        user.qr_token = None
        user.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "email": user.email,
                "name": user.name,
            }
        }, status=200)
