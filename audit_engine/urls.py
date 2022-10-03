from django.urls import path, include

urlpatterns = [
    path("api/", include("audit_engine.api.urls")),
]
