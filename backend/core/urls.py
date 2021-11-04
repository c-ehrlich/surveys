from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # JWT auth
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Website / Frontend
    path("", include("surveys.urls", namespace="surveys")),

    # REST API
    path("api/", include("surveys_api.urls", namespace="surveys_api")),
    path("api/user/", include("user.urls", namespace="user")),

    # ADMIN CP
    path('admin/', admin.site.urls),
]
