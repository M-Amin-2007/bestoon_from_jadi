"""manage admin panel"""
from django.contrib import admin
from .models import *

# Register your models here.
reg = admin.site.register
reg(Expense)
reg(Income)
