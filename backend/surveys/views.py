from django.shortcuts import render
from rest_framework import generics

# from .models import Form

from rest_framework.permissions import (
    SAFE_METHODS,
    BasePermission,
    IsAdminUser,
    DjangoModelPermissionsOrAnonReadOnly,
)


class SurveyDetail(generics.RetrieveUpdateDestroyAPIView):
    pass
