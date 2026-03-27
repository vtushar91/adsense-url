from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User,UserProfile
import random

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    referral_code = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = User
        fields = ('username', 'name', 'phone_or_upi', 'password', 'referral_code')

    def generate_referral_code(self, username):
        return f"{username}_{random.randint(1000, 9999)}"

    def create(self, validated_data):
        referral_code_input = validated_data.pop('referral_code', None)

        username = validated_data['username']

        # Generate unique referral code
        referral_code = self.generate_referral_code(username)

        while User.objects.filter(referral_code=referral_code).exists():
            referral_code = self.generate_referral_code(username)

        # Create user
        user = User.objects.create_user(
            username=username,
            password=validated_data['password'],
            name=validated_data['name'],
            phone_or_upi=validated_data['phone_or_upi'],
            referral_code=referral_code
        )

        # Handle referral
        if referral_code_input:
            try:
                ref_user = User.objects.get(referral_code=referral_code_input)
                user.referred_by = ref_user
                user.save(update_fields=["referred_by"])
            except User.DoesNotExist:
                pass  # ignore invalid referral

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data['username'],
            password=data['password']
        )
        if not user:
            raise serializers.ValidationError("Invalid username or password")
        return user
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"
        read_only_fields = ["user"]