from django.urls import path

from .ninja_api import api as ninja_api

app_name = "api"

urlpatterns = [
    path('', ninja_api.urls)
]

