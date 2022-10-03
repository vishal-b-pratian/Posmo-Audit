from django.urls import path, include

urlpatterns = [
    path("api/", include("content_management.api.urls")),
]
