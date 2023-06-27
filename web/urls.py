"""manage app urls"""
from django.urls import path
from . import views

app_name = "web"

urlpatterns = [
    path("expense/", views.expense, name="expense"),
    path("income/", views.income, name="income"),
    path("delete/<pk>/<db>/", views.delete_item, name="delete_method"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("user/", views.user, name="user"),
    path("", views.home, name="home"),
]
