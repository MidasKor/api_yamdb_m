from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    APIUserCreate,
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    TokenView,
    UserViewSet,
)

router = DefaultRouter()

app_name = "api"

router.register(r"titles", TitleViewSet, basename="titles")
router.register(r"genres", GenreViewSet)
router.register(r"categories", CategoryViewSet)
router.register(r"users", UserViewSet)
router.register(r"titles/(?P<title_id>\d+)/reviews",
                ReviewViewSet, basename="reviews")
router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="comments",
)

urlpatterns = [
    path("v1/", include(router.urls)),
    path("v1/auth/signup/", APIUserCreate.as_view(), name='signup'),
    path("v1/auth/token/", TokenView.as_view(), name="get_token"),
]
