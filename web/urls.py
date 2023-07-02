"""manage app urls"""
from django.urls import path
from . import views

app_name = "web"

urlpatterns = [
    path("expense/", views.expense, name="expense"),
    path("income/", views.income, name="income"),
    path("delete/<pk>/<db>/", views.delete_item, name="delete_method"),
    path("edit/<pk>/<db>/", views.edit_item, name="edit_method"),
    path("multi_delete/<db>/", views.multi_delete, name="multi_delete"),
    path("", views.home, name="home"),
]
