"""create app views"""
from django.http import JsonResponse
from json import JSONEncoder
from django.views.decorators.csrf import csrf_exempt
from .models import *
import datetime
now = datetime.datetime.now
# Create your views here.
@csrf_exempt
def expense_submit(request):
    """make response for expense submit requests."""
    this_token = request.POST["token"]
    this_user = User.objects.get(token__token_m=this_token)
    text = request.POST["text"]
    amount = request.POST["amount"]
    Expense.objects.create(user=this_user, text=text, amount=amount, date=now())
    return  JsonResponse({
        "status":"OK",
    }, encoder=JSONEncoder)


@csrf_exempt
def income_submit(request):
    """make response for income submit requests."""
    this_token = request.POST["token"]
    this_user = User.objects.get(token__token_m=this_token)
    text = request.POST["text"]
    amount = request.POST["amount"]
    Income.objects.create(user=this_user, text=text, amount=amount, date=now())
    return  JsonResponse({
        "status":"OK",
    }, encoder=JSONEncoder)
