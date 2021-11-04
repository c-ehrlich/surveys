from django.urls import path
from .views import FormDetail

app_name = "surveys_api"

urlpatterns = [
    path('form/<int:pk>/', FormDetail.as_view(), name="formdetail"),
]