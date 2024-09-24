from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from rest_framework import serializers
from allauth.account.models import EmailAddress
from django_countries.serializers import CountryFieldMixin

User = get_user_model()

class UserSerializer(CountryFieldMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'address', 'post_code', 'phone_number', 'country', 'is_mfa_enabled']
        read_only_fields = ['id', 'is_active', 'is_mfa_enabled']

class RegistrationSerializer(CountryFieldMixin, serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    phone_number = serializers.CharField(
        validators=[RegexValidator(
            regex=r'^\+?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    post_code = serializers.CharField(max_length=20)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'first_name', 'last_name', 'phone_number', 'address', 'post_code', 'country']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        return User.objects.create_user(**validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('password', None)
        return representation

class EmailVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailAddress
        fields = ['email', 'verified']

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(max_length=128, style={'input_type': 'password'})
    new_password2 = serializers.CharField(max_length=128, style={'input_type': 'password'})

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({"new_password2": "The two password fields didn't match."})
        return data
    
class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password1 = serializers.CharField(max_length=128, style={'input_type': 'password'})
    new_password2 = serializers.CharField(max_length=128, style={'input_type': 'password'})

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({"new_password2": "The two password fields didn't match."})
        return data