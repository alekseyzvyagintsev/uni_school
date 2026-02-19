from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.reverse import reverse


@login_required(login_url="/admin/login/")
def redirect_to_swagger(request):
    return HttpResponseRedirect(reverse("swagger-ui"))


def health(request):
    return HttpResponse("OK")


urlpatterns = [
    path("health/", health),
    path("admin/", admin.site.urls),
    path("admindocs/", include("django.contrib.admindocs.urls")),
    path("", include("materials.urls", namespace="material_urls")),
    path("", include("users.urls", namespace="users_urls")),
    # Маршруты для схемы и документации
    re_path(r"^api/schema(?P<format>\.json|\.yaml)?$", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
