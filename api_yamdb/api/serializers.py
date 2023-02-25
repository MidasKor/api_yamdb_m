"""Serializer classes."""

import re

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer."""

    class Meta:
        model = Category
        exclude = ('id',)
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class GenreSerializer(serializers.ModelSerializer):
    """Genre serializer."""

    class Meta:
        model = Genre
        exclude = ('id',)
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class TitleReadSerializer(serializers.ModelSerializer):
    """Title read serializer."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    """Title write serializer."""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title


class UserSerializer(serializers.ModelSerializer):
    """User serializer."""

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role"
        )

    def validate(self, attrs):
        if self.context.get("request").method != "PATCH":
            if not re.fullmatch((r"^[\w.@+-]+\Z"), attrs.get("username")):
                raise serializers.ValidationError("Username is not valid!")
        elif attrs.get("username"):
            if not re.fullmatch((r"^[\w.@+-]+\Z"), attrs.get("username")):
                raise serializers.ValidationError("Username is not valid!")
        return attrs


class ReviewSerializer(serializers.ModelSerializer):
    """Review serializer."""

    title = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True,
    )
    author = serializers.SlugRelatedField(
        slug_field="username",
        default=serializers.CurrentUserDefault(), read_only=True
    )

    def validate(self, data):
        request = self.context["request"]
        author = request.user
        title_id = self.context["view"].kwargs.get("title_id")
        title = get_object_or_404(Title, pk=title_id)
        if request.method == "POST":
            if Review.objects.filter(title=title, author=author).exists():
                raise serializers.ValidationError(
                    "На одно произведение вы можете оставить только один отзыв"
                )
        return data

    class Meta:
        model = Review
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    """Comment serializer."""

    review = serializers.SlugRelatedField(slug_field="text", read_only=True)
    author = serializers.SlugRelatedField(
        slug_field="username", read_only=True)

    class Meta:
        model = Comment
        fields = "__all__"


class UserCreateSerializer(serializers.Serializer):
    """Serializer for a user creation view function."""
    username = serializers.CharField(allow_blank=True)
    email = serializers.CharField()

    class Meta:
        fields = ("username", "email")
        extra_kwargs = {
            "username": {
                "validators": [],
            },
            "email": {
                "validators": [],
            },
        }

    def validate(self, value):

        username = value.get('username')
        if (
            not username
            or username.lower() == "me"
            or not re.fullmatch((r"^[\w.@+-]+\Z"), username)
            or len(username) > 150
        ):
            raise serializers.ValidationError(
                {"username": "Not valid username.",
                 "email": "Not valid email"})
        email = value.get('email')
        if len(email) > 254:
            raise serializers.ValidationError("Not valid email.")
        return value

    def create(self, validated_data):
        return User.objects.create(**validated_data)


class TokenSerializer(serializers.Serializer):
    """Serializer for a token creation view function."""

    confirmation_code = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
