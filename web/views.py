"""create app views"""
import re, datetime, openpyxl, os
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from .models import *
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from bestoon.settings import BASE_DIR

# TODO: add csrf tokens, add js validation to form before submit
# TODO: add suggestions part
# TODO: change paragraphs and expressions
### TODO: add statistics part
# TODO: auto scroll to table or new data with button with script
now = datetime.datetime.now
def home(request):
    """manage home request."""
    context = {"login_status":request.user.is_authenticated and not request.user.is_superuser}
    return render(request, "web/home.html", context=context)


@csrf_exempt
def income(request):
    """incomes"""
    if request.user.is_authenticated and not request.user.is_superuser:
        if request.method == "POST" and "text" in request.POST:
            text = request.POST.get("text")
            amount = request.POST.get("amount")
            date = request.POST.get("date")
            if not date: date = now()
            Income.objects.create(text=text, amount=amount, date=date, this_user=request.user)
            return redirect(reverse("web:income"))
        elif request.method == "POST" and "file" in request.FILES:
            in_memory_file = request.FILES.get("file")
            if re.search(r"\.\w+$", str(in_memory_file)).group(0) == ".xlsx":
                file_storage = default_storage.save(f"./web/excel_files/{str(in_memory_file)}", ContentFile(in_memory_file.read()))
                path = os.path.join(BASE_DIR, file_storage)
                file = openpyxl.load_workbook(path)
                sheet = file.active
                titles_pos = dict()
                for i in range(1, sheet.max_column + 1):
                    cell_value = sheet.cell(row=1, column=i).value
                    if cell_value == "amount":
                        titles_pos["amount"] = i
                    elif cell_value == "text":
                        titles_pos["text"] = i
                    elif cell_value == "date":
                        titles_pos["date"] = i
                if not ("amount" in titles_pos.keys() and "text" in titles_pos.keys()):
                    data_list = list(Income.objects.filter(this_user=request.user))
                    context = {"datas": enumerate(data_list), "title": "income",
                               "message": "file haven't requirement titles in first row. (title, amount)"}
                    return render(request, "web/data.html", context=context)
                row_failed = list()
                for i in range(2, sheet.max_row + 1):
                    new_income_attr = dict()
                    for title, pos in titles_pos.items():
                        new_income_attr.update({title : sheet.cell(row=i, column=pos).value})
                    if not any(new_income_attr.values()): continue
                    text = new_income_attr.get("text")
                    date = new_income_attr.get("date") if type(new_income_attr.get("date")) == datetime.datetime else now()
                    try:amount = int(new_income_attr.get("amount"))
                    except ValueError:
                        row_failed.extend(["amount must be number!", i])
                        continue
                    except TypeError:
                        row_failed.extend(["amount field must have a value!", i])
                        continue
                    else:
                        if text:
                            Income.objects.create(text=text, amount=amount, date=date, this_user=request.user, edit_mod=False)
                        else:
                            row_failed.extend(["text field must have a value!", i])
                os.remove(path)
                data_list = list(Income.objects.filter(this_user=request.user))
                context = {"datas": enumerate(data_list), "title": "income",
                           "message": f"failed rows: {row_failed}"}
                return render(request, "web/data.html", context=context)
            else:
                data_list = list(Income.objects.filter(this_user=request.user))
                context = {"datas": enumerate(data_list), "title": "income", "message": "only you can upload excel files!!"}
                return render(request, "web/data.html", context=context)
        else:
            data_list = list(Income.objects.filter(this_user=request.user))
            context = {"datas":enumerate(data_list), "title":"income"}
            return render(request, "web/data.html", context=context)
    else:
        return redirect(reverse("account_manager:login"))


@csrf_exempt
def expense(request):
    """expenses"""
    if request.user.is_authenticated and not request.user.is_superuser:
        if request.method == "POST" and "text" in request.POST:
            text = request.POST.get("text")
            amount = request.POST.get("amount")
            date = request.POST.get("date")
            if not date: date = now()
            Expense.objects.create(text=text, amount=amount, date=date, this_user=request.user)
            return redirect(reverse("web:expense"))
        elif request.method == "POST" and "file" in request.FILES:
            in_memory_file = request.FILES.get("file")
            if re.search(r"\.\w+$", str(in_memory_file)).group(0) == ".xlsx":
                file_storage = default_storage.save(f"./web/excel_files/{str(in_memory_file)}", ContentFile(in_memory_file.read()))
                path = os.path.join(BASE_DIR, file_storage)
                file = openpyxl.load_workbook(path)
                sheet = file.active
                titles_pos = dict()
                for i in range(1, sheet.max_column + 1):
                    cell_value = sheet.cell(row=1, column=i).value
                    if cell_value == "amount":
                        titles_pos["amount"] = i
                    elif cell_value == "text":
                        titles_pos["text"] = i
                    elif cell_value == "date":
                        titles_pos["date"] = i
                if not ("amount" in titles_pos.keys() and "text" in titles_pos.keys()):
                    data_list = list(Expense.objects.filter(this_user=request.user))
                    context = {"datas": enumerate(data_list), "title": "expense",
                               "message": "file haven't requirement titles in first row. (title, amount)"}
                    return render(request, "web/data.html", context=context)
                row_failed = list()
                for i in range(2, sheet.max_row + 1):
                    new_expense_attr = dict()
                    for title, pos in titles_pos.items():
                        new_expense_attr.update({title : sheet.cell(row=i, column=pos).value})
                    if not any(new_expense_attr.values()): continue
                    text = new_expense_attr.get("text")
                    date = new_expense_attr.get("date") if type(new_expense_attr.get("date")) == datetime.datetime else now()
                    try:amount = int(new_expense_attr.get("amount"))
                    except ValueError:
                        row_failed.extend(["amount must be number!", i])
                        continue
                    except TypeError:
                        row_failed.extend(["amount field must have a value!", i])
                        continue
                    else:
                        if text:
                            Expense.objects.create(text=text, amount=amount, date=date, this_user=request.user, edit_mod=False)
                        else:
                            row_failed.extend(["text field must have a value!", i])
                os.remove(path)
                data_list = list(Expense.objects.filter(this_user=request.user))
                context = {"datas": enumerate(data_list), "title": "expense",
                           "message": f"failed rows: {row_failed}"}
                return render(request, "web/data.html", context=context)
            else:
                data_list = list(Expense.objects.filter(this_user=request.user))
                context = {"datas": enumerate(data_list), "title": "expense", "message": "only you can upload excel files!!"}
                return render(request, "web/data.html", context=context)
        else:
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
