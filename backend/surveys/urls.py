from django.urls import path
from django.views.generic import TemplateView

app_name = 'surveys'

urlpatterns = [
  path('', TemplateView.as_view(template_name="surveys/index.html")),
]