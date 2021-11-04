from django.shortcuts import render
from rest_framework import generics

# from forms.models import Form
from rest_framework.permissions import (
    SAFE_METHODS,
    BasePermission,
    IsAdminUser,
    DjangoModelPermissionsOrAnonReadOnly,
)


class FormUserWritePermission(BasePermission):
    """Forms can only be edited or deleted by their author"""

    message = "Editing forms is restricted to the author only."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:  # GET, OPTIONS, HEAD
            return True

        return obj.author == request.user


class FormDetail(generics.RetrieveUpdateDestroyAPIView):
    pass
