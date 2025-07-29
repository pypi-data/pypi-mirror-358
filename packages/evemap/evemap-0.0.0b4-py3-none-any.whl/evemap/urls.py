"""Routes."""

from django.urls import path, re_path

from . import views
from .api import api

app_name = "evemap"

urlpatterns = [
    path("", views.index, name="index"),
    path("api/", api.urls),
    re_path(r"^(?:.*)/?$", views.index, name="catch_all"),
]
