from django.contrib.auth import get_user_model
from rest_framework import serializers

from user.models import Post


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "is_staff",
        )
        read_only_fields = ("id", "is_staff")
        extra_kwargs = {"password": {"write_only": True, "min_length": 8}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class UserListSerializer(UserSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
        )


class UserDetailSerializer(UserSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "bio",
        )


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "text", "user")


class PostListSerializer(PostSerializer):
    user_username = serializers.CharField(
        source="user.username", read_only=True
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "user_username",
            "text",
            # "media_image",
            "created_at",
        )


class PostDetailSerializer(PostListSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "user_username",
            "text",
            # "media_image",
            # "likes_count",
            # "unlikes_count",
        )
