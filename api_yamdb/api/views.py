"""Application view classes."""

import re

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.settings import SENDER
from reviews.models import Category, Genre, Review, Title
from users.models import User
from .filters import TitleFilter
from .mixins import CreateListDestroyViewSet
from .permissons import (
    AdminOnly,
    AuthorModeratorAdminOrReadOnly,
    IsAdminSuperuserOrReadOnly,
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    TokenSerializer,
    UserCreateSerializer,
    UserSerializer,
)


class CategoryViewSet(CreateListDestroyViewSet):
    """Category viewset"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    permission_classes = [IsAdminSuperuserOrReadOnly]
    lookup_field = "slug"


class GenreViewSet(CreateListDestroyViewSet):
    """Genre viewset"""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    permission_classes = [IsAdminSuperuserOrReadOnly]
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    """Title viewset"""

    queryset = Title.objects.annotate(rating=Avg("reviews__score")).all()
    filter_backends = (DjangoFilterBackend,)
    permission_classes = [IsAdminSuperuserOrReadOnly]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return TitleReadSerializer
        return TitleWriteSerializer


class UserViewSet(viewsets.ModelViewSet):
    """User viewset"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, AdminOnly)
    lookup_field = "username"
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    http_method_names = ["get", "post", "delete", "patch"]

    @action(
        methods=["GET", "PATCH"],
        detail=False, permission_classes=(IsAuthenticated,)
    )
    def me(self, request):

        if request.method == "PATCH":
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role, partial=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    """Review viewset"""

    serializer_class = ReviewSerializer
    permission_classes = [AuthorModeratorAdminOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Comment vieset"""

    serializer_class = CommentSerializer
    permission_classes = [AuthorModeratorAdminOrReadOnly]

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get("review_id"))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get("review_id"))
        serializer.save(author=self.request.user, review=review)


class APIUserCreate(APIView):
    """User creation view function.

    В чате подсказали перенести чать логики по валидации в контроллер.
    Т.к. мы отправляем письмо с подтвердждением из вью класса, а не в
    сериалазайзере, это помогло."""

    serializer_class = UserCreateSerializer
    permission_classes = (AllowAny,)
    http_method_names = ["post"]

    def create_conf_code_send_mail(self, user, data):

        confirmation_code = default_token_generator.make_token(user)
        email = EmailMessage(
            subject=data["subject"],
            body=(f"Ваш код доступа к API: {confirmation_code}"),
            from_email=data["from_email"],
            to=data["to_email"],
        )
        email.send()

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get("username")
        email = serializer.validated_data.get("email")
        if not re.fullmatch((r"^[\w.@+-]+\Z"), username):
            return Response(
                {"username": "Not valid username.",
                 "email": "Not valid email"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if User.objects.filter(username=username, email=email).exists():
            user = User.objects.get(username=username, email=email)
            data = {
                "subject": "Ваш код доступа",
                "from_email": SENDER,
                "to_email": [email],
            }
            self.create_conf_code_send_mail(user, data)
            return Response(
                {"username": username, "email": email},
                status=status.HTTP_200_OK,
            )
        elif User.objects.filter(email=email).exists():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        elif User.objects.filter(username=username).exists():
            if User.objects.get(username=username).email != email:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            user = serializer.save()
            data = {
                "subject": "Ваш код доступа",
                "from_email": SENDER,
                "to_email": [email]
            }
            self.create_conf_code_send_mail(user, data)
            return Response(request.data, status=status.HTTP_200_OK)


class TokenView(generics.CreateAPIView):
    """Token creation view function"""

    permission_classes = [AllowAny]
    serializer_class = TokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get("username")
        user = get_object_or_404(User, username=username)
        conf_code = serializer.validated_data.get("comfirmation_code")
        if default_token_generator.check_token(user, conf_code):
            # генерация токена для конкретного пользователя
            token = AccessToken.for_user(user)
            return Response({"token": str(token)}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
