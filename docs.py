from rest_framework.documentation import include_docs_urls
from django.urls import path


urlpatterns = [
    path("docs/", include_docs_urls(title="API Documentation")),
]
