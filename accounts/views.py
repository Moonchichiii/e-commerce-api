from datetime import timedelta

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse

from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView
from rest_framework_simplejwt.tokens import RefreshToken

from mfa.helpers import has_mfa
from .serializers import UserSerializer, RegistrationSerializer
from .throttling import LoginRateThrottle, AdminRateThrottle, RegularUserRateThrottle


# Social login views
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


# MFA login callback view
MFA_TOKEN_EXPIRATION = timedelta(minutes=10)


@login_required
def mfa_login_callback(request, user):
    """
    MFA login callback view.
    """
    if not user:
        return JsonResponse({"detail": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    if not has_mfa(user):
        return HttpResponseRedirect(reverse('mfa_add'))
    return HttpResponseRedirect(reverse('home'))


# Custom login view with rate throttling
class LoginView(APIView):
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        """
        Handle login requests.
        """
        return Response({"detail": "Login successful"}, status=status.HTTP_200_OK)


class CustomLoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        """
        Handle custom login requests.
        """
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            return Response({"detail": "Invalid credentials. Please check your email and password and try again."}, status=status.HTTP_401_UNAUTHORIZED)


class CustomPasswordResetView(PasswordResetView):
    def post(self, request, *args, **kwargs):
        """
        Handle password reset requests.
        """
        user = User.objects.filter(email=request.data.get('email')).first()
        if user is None:
            return Response({"detail": "Invalid login credentials. Please try again or reset your password."}, status=status.HTTP_401_UNAUTHORIZED)
        return super().post(request, *args, **kwargs)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Handle password reset confirmation.
    """
    pass


class CustomRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle user registration.
        """
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@throttle_classes([AdminRateThrottle])
def admin_view(request):
    """
    Admin view with rate throttling.
    """
    return JsonResponse({"detail": "Admin view accessed successfully."})


@throttle_classes([RegularUserRateThrottle])
def regular_user_view(request):
    """
    Regular user view with rate throttling.
    """
    return JsonResponse({"detail": "Regular user view accessed successfully."})


class CustomLogoutView(APIView):
    def post(self, request):
        """
        Handle user logout.
        """
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
