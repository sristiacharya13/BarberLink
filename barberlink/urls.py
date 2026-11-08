from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenRefreshView 
from django.views.i18n import JavaScriptCatalog
from django.contrib.auth import views as auth_views
urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", TemplateView.as_view(template_name="barberlink/login.html"), name="login_page"),
    path("register/", TemplateView.as_view(template_name="barberlink/register.html"), name="register_page"),
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/", include("bookings.urls")),
    path("barbers/", include("barbers.urls")),
    path("forgot_password/",auth_views.PasswordResetView.as_view(
        template_name="barberlink/forgot_password.html",
        email_template_name="barberlink/password_reset_email.html",
        subject_template_name="barberlink/password_reset_subject.txt",
        success_url="/forgot_password/done/",
        ),
        name="forgot_password_page",
    ),
    path("forgot_password/done/",auth_views.PasswordResetDoneView.as_view(template_name="barberlink/password_reset_done.html"),name="password_reset_done"),
    path("reset/<uidb64>/<token>/",auth_views.PasswordResetConfirmView.as_view(template_name="barberlink/password_reset_confirm.html"),name="password_reset_confirm"),
    path("reset/done/",auth_views.PasswordResetCompleteView.as_view(template_name="barberlink/password_reset_complete.html"),name="password_reset_complete",),
    path("",TemplateView.as_view(template_name="barberlink/home.html"),name="home",),
    path("customers/", include("customers.urls")),
    path('i18n/', include('django.conf.urls.i18n')),
    path('payments/',include('payments.urls')),
    path("jsi18n/",JavaScriptCatalog.as_view(),name="javascript-catalog",),
]