"""Mixin class"""
from rest_framework import mixins, viewsets


class CreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    A viewset that provides `delete`, `create`, and `list` actions.
    """

    pass
