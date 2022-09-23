from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

schema_view = get_schema_view(
    openapi.Info(
        title="Habbit API",
        default_version="v1",
        description="Habbit app backend api",
        terms_of_service="",
        contact=openapi.Contact(email="contact@habbit.gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    authentication_classes=(JWTAuthentication,),
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("admin/", admin.site.urls),
    #  API VERSION 1
    path("api/v1/", include("account.api.v1.urls")),
    path("api/v1/", include("thread.api.v1.urls")),
]

urlpatterns += [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
]
