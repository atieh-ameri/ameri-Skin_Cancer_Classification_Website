from django.urls import path
from .views import register, login_user, logout_user, dashboard, result, home, imagecropper, contact_view
from . import views
urlpatterns = [
    path("", home),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("result/", result, name="result"),
    path("dashboard/", dashboard, name="dashboard"),
    path("imagecropper/", imagecropper, name="imagecropper"),
    path('contact/', contact_view, name='contact')
]



