from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from rest_framework import serializers
from allauth.account.models import EmailAddress


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active']


class RegistrationSerializer(serializers.ModelSerializer):
    phone_number_validator = RegexValidator(
        regex=r'^\+?\d{9,15}$', 
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'phone_number']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        return user


class EmailVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailAddress
        fields = ['email', 'verified']
