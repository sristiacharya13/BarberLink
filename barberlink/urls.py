from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenRefreshView 

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", TemplateView.as_view(template_name="barberlink/login.html"), name="login_page"),
    path("register/", TemplateView.as_view(template_name="barberlink/register.html"), name="register_page"),
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("barbers/", include("barbers.urls")),
    path("customers/", include("customers.urls")),
    path('i18n/', include('django.conf.urls.i18n')),
    path('payments/',include('payments.urls')),
]