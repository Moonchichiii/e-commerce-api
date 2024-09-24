from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import AnonRateThrottle
from allauth.account.models import EmailAddress
from django.core.mail import send_mail
from django.conf import settings

from .serializers import (
    UserSerializer, 
    RegistrationSerializer, 
    EmailVerificationSerializer, 
    PasswordResetSerializer, 
    PasswordResetConfirmSerializer
)
from .throttling import LoginRateThrottle,IPBasedAnonRateThrottle, IPBasedUserRateThrottle
from .models import PasswordResetToken



User = get_user_model()

class CustomLoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle, IPBasedAnonRateThrottle]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            if not user.is_active:
                return Response({"error": "User account is disabled."}, status=status.HTTP_403_FORBIDDEN)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "Invalid credentials",
                "message": "Please check your email and password and try again."
            }, status=status.HTTP_401_UNAUTHORIZED)

class CustomRegistrationView(APIView):
    throttle_classes = [IPBasedAnonRateThrottle]
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data,
                'message': 'Registration successful'
            }, status=status.HTTP_201_CREATED)
        return Response({
            "error": "Registration failed",
            "message": "Please correct the errors and try again.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                email_address = EmailAddress.objects.get(email=email)
                if email_address.verified:
                    return Response({"message": "Email is already verified."}, status=status.HTTP_200_OK)
                email_address.verified = True
                email_address.save()
                return Response({"message": "Email successfully verified."}, status=status.HTTP_200_OK)
            except EmailAddress.DoesNotExist:
                return Response({"error": "Email not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomPasswordResetView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                token = PasswordResetToken.objects.create(user=user)
               
                # Send email with reset token
                reset_url = f"{settings.FRONTEND_URL}/reset-password/{token.token}"
                send_mail(
                    'Password Reset Request',
                    f'Click the following link to reset your password: {reset_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
               
                return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:    
                pass
        return Response({"message": "If an account with this email exists, a password reset link has been sent."}, status=status.HTTP_200_OK)

class CustomPasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = request.data.get('token')
            try:
                reset_token = PasswordResetToken.objects.get(token=token)
                if reset_token.is_valid():
                    user = reset_token.user
                    user.set_password(serializer.validated_data['new_password1'])
                    user.save()
                    reset_token.delete()
                    return Response({"message": "Password successfully reset."}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Token has expired."}, status=status.HTTP_400_BAD_REQUEST)
            except PasswordResetToken.DoesNotExist:
                return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
