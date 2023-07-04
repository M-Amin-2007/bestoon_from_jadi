"""manage urls send to this app"""
from django.urls import path
from . import views

app_name = "account_manager"

urlpatterns = [
    path("change_password/", views.change_password, name="change_password"),
    path("change_username/", views.change_username, name="change_username"),
    path("change_email/", views.change_email, name="change_email"),
    path("logout_view/", views.logout_view, name="logout_view"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("delete_account/", views.delete_account_view, name="delete_account"),
    path("user/", views.user_view, name="user"),
    path("forgot_password/", views.forgot_password_view, name="forgot_password"),
]