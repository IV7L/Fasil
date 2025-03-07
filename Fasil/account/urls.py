from django.urls import path
from . import views

urlpatterns = [
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("callback", views.callback, name="callback"),
    path("verify_email", views.verify_email, name="verify_email"),
    path("profile/<int:id>/", views.profile, name="profile"),
]