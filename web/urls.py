"""manage app urls"""
from django.urls import path
from . import views

app_name = "web"

urlpatterns = [
    path("submit/expense/", views.expense_submit, name="expense_submit"),
    path("submit/income/", views.income_submit, name="income_submit"),
    path("register/", views.register, name="register"),
]
