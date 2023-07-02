"""create app views"""
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from .models import *
import datetime

# TODO: add csrf tokens, add js validation to form before submit
# TODO: move register button under sign in form, change name of "register" to "sign up"
# TODO: add suggestions part, make navbar constant, unable user to login when user is authenticated
# TODO: change Home page figure when user login, correct login page title
# TODO: change paragraphs and expressions
# TODO: make exel files readable, add statistics part
# TODO: super users shouldn't be able to use normal panels.
# TODO: delete account ability for user

now = datetime.datetime.now
def edit_mod_maker(db_obj):
    """DB"""
    db_obj.edit_mod = False
    return db_obj


def home(request):
    """manage home request."""
    return render(request, "web/home.html")


@csrf_exempt
def income(request):
    """incomes"""
    if request.user.is_authenticated:
        if request.method == "POST":
            text = request.POST.get("text")
            amount = request.POST.get("amount")
            date = request.POST.get("date")
            if not date: date = now()
            Income.objects.create(text=text, amount=amount, date=date, this_user=request.user)
        data_list = list(Income.objects.filter(this_user=request.user))
        context = {"datas":enumerate(data_list), "title":"income"}
        return render(request, "web/data.html", context=context)
    else:
        return redirect(reverse("account_manager:login"))


@csrf_exempt
def expense(request):
    """expenses"""
    if request.user.is_authenticated:
        if request.method == "POST":
            text = request.POST.get("text")
            amount = request.POST.get("amount")
            date = request.POST.get("date")
            if not date: date = now()
            Expense.objects.create(text=text, amount=amount, date=date, this_user=request.user)
        data_list = Expense.objects.filter(this_user=request.user)
        context = {"datas":enumerate(data_list), "title":"expense"}
        return render(request, "web/data.html", context=context)
    else:
        return redirect(reverse("account_manager:login"))


@csrf_exempt
def delete_item(request, pk, db):
    """delete an income or expense from database."""
    if db == "income":
        Income.objects.get(pk=pk).delete()
        return redirect(reverse("web:income"))
    elif db == "expense":
        Expense.objects.get(pk=pk).delete()
        return redirect(reverse("web:expense"))


@csrf_exempt
def edit_item(request, pk, db):
    """edit table methods"""
    if request.method == "GET":
        raise Http404("not found!")
    else:
        if "text" in request.POST:
            text = request.POST.get("text")
            amount = request.POST.get("amount")
            date = request.POST.get("date")
            if db == "income":
                data_object = Income.objects.get(pk=pk)
                data_object.edit_mod = False
                data_object.text = text
                data_object.amount = amount
                data_object.date = date if date else data_object.date
                data_object.save()
            else:
                data_object = Expense.objects.get(pk=pk)
                data_object.edit_mod = False
                data_object.text = text
                data_object.amount = amount
                data_object.date = date if date else data_object.date
                data_object.save()
        else:
            if db == "income":
                data_object = Income.objects.get(pk=pk)
                data_object.edit_mod = True
                data_object.save()
            else:
                data_object = Expense.objects.get(pk=pk)
                data_object.edit_mod = True
                data_object.save()

        return redirect(reverse(f"web:{db}"))


@csrf_exempt
def multi_delete(request, db):
    """multi delete"""
    if db == "income":
        if request.POST:
            items = dict(request.POST).get("choice")
            for pk in items:
                item = Income.objects.get(pk=int(pk))
                item.delete()
            return redirect(reverse("web:income"))
        else:
            data_list = list(Income.objects.filter(this_user=request.user))
            context = {"datas": enumerate(data_list), "title": "income", "multi_delete_mod": True}
            return render(request, "web/data.html", context=context)
    if db == "expense":
        if request.POST:
            items = dict(request.POST).get("choice")
            for pk in items:
                item = Expense.objects.get(pk=int(pk))
                item.delete()
            return redirect(reverse("web:expense"))
        else:
            data_list = list(Expense.objects.filter(this_user=request.user))
            context = {"datas": enumerate(data_list), "title": "expense", "multi_delete_mod": True}
            return render(request, "web/data.html", context=context)
    else:
        return Http404("not Found!")
