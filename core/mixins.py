from rest_framework import status
from rest_framework.response import Response


class SoftDestroyModelMixin:
    """
    Deactivate a model instance.
    """

    def soft_destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_soft_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_soft_destroy(self, instance):
        instance.active = False
        instance.save()
