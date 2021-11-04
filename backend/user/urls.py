from django.urls import path
from .views import CustomUserCreate, BlacklistTokenView

app_name = "user"

urlpatterns = [
    # all paths are /api/user/abc
    path("register/", CustomUserCreate.as_view(), name="create_user"),
    path("logout/blacklist/", BlacklistTokenView.as_view(), name="blacklist"),
]
