from django.urls import path
from .views import WebHook

urlpatterns = [
    path("", WebHook.as_view())
]
