"""create app views"""
import re, datetime, openpyxl, os, json
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from .models import *
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from bestoon.settings import BASE_DIR

# TODO: add suggestions part
# TODO: change paragraphs and expressions
now = datetime.datetime.now


def home(request):
    """manage home request."""
    context = {"login_status":request.user.is_authenticated and not request.user.is_superuser}
    return render(request, "web/home.html", context=context)


def income(request):
    """incomes"""
    if request.user.is_authenticated and not request.user.is_superuser:
        if request.method == "POST" and "text" in request.POST:
            text = request.POST.get("text")
            amount = request.POST.get("amount")
            date = request.POST.get("date")
            if not date: date = now()
            Income.objects.create(text=text, amount=amount, date=date, this_user=request.user)
            data_list = list(Income.objects.filter(this_user=request.user))
            context = {"datas": enumerate(data_list), "title":"income", "scroll_tag":"main_table",
                       "scroll_status":"down"}
            return render(request, "web/data.html", context=context)
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
                    os.remove(path)
                    data_list = list(Income.objects.filter(this_user=request.user))
                    context = {"datas": enumerate(data_list), "title": "income",
                               "message": "file haven't requirement titles in first row. (title, amount)",
                               "scroll_tag":"excel_upload", "scroll_status":"down"}
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
                           "message": f"failed rows: {row_failed}",
                           "scroll_tag":"main_table", "scroll_status":"down"}
                return render(request, "web/data.html", context=context)
            else:
                data_list = list(Income.objects.filter(this_user=request.user))
                context = {"datas": enumerate(data_list), "title": "income",
                           "message": "only you can upload excel files!!",
                           "scroll_tag":"excel_upload", "scroll_status":"down"}
                return render(request, "web/data.html", context=context)
        else:
            data_list = list(Income.objects.filter(this_user=request.user))
            context = {"datas":enumerate(data_list), "title":"income",
                       "scroll_tag":request.GET.get("scroll_tag"),
                       "scroll_status":request.GET.get("scroll_status")}
            return render(request, "web/data.html", context=context)
    else:
        return redirect(reverse("account_manager:login"))


def expense(request):
    """expenses"""
    if request.user.is_authenticated and not request.user.is_superuser:
        if request.method == "POST" and "text" in request.POST:
            text = request.POST.get("text")
            amount = request.POST.get("amount")
            date = request.POST.get("date")
            if not date: date = now()
            Expense.objects.create(text=text, amount=amount, date=date, this_user=request.user)
            data_list = list(Expense.objects.filter(this_user=request.user))
            context = {"datas": enumerate(data_list), "title":"expense", "scroll_tag":"main_table",
                       "scroll_status":"down"}
            return render(request, "web/data.html", context=context)
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
                               "message": "file haven't requirement titles in first row. (title, amount)",
                               "scroll_tag": "excel_upload", "scroll_status": "down"}
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
                           "message": f"failed rows: {row_failed}",
                           "scroll_tag": "main_table", "scroll_status": "down"}
                return render(request, "web/data.html", context=context)
            else:
                data_list = list(Expense.objects.filter(this_user=request.user))
                context = {"datas": enumerate(data_list), "title": "expense",
                           "message": "only you can upload excel files!!",
                           "scroll_tag": "excel_upload", "scroll_status": "down"}
                return render(request, "web/data.html", context=context)
        else:
            data_list = Expense.objects.filter(this_user=request.user)
            context = {"datas":enumerate(data_list), "title":"expense",
                       "scroll_tag": request.GET.get("scroll_tag"),
                       "scroll_status": request.GET.get("scroll_status")}
            return render(request, "web/data.html", context=context)
    else:
        return redirect(reverse("account_manager:login"))


def delete_item(request, pk, db):
    """delete an income or expense from database."""
    if db == "income":
        Income.objects.get(pk=pk).delete()
        return redirect(f"{reverse(f'web:{db}')}?scroll_tag=main_table&scroll_status=top")
    elif db == "expense":
        Expense.objects.get(pk=pk).delete()
        return redirect(f"{reverse(f'web:{db}')}?scroll_tag=main_table&scroll_status=top")


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

        return redirect(f"{reverse(f'web:{db}')}?scroll_tag=id_row_{pk}&scroll_status=top")


def multi_delete(request, db):
    """multi delete"""
    if db == "income":
        if "choice" in request.POST:
            print(request.POST)
            items = dict(request.POST).get("choice")
            for pk in items:
                item = Income.objects.get(pk=int(pk))
                item.delete()
            return redirect(f"{reverse(f'web:{db}')}?scroll_tag=main_table&scroll_status=top")
        else:
            data_list = list(Income.objects.filter(this_user=request.user))
            context = {"datas": enumerate(data_list), "title": "income", "multi_delete_mod": True,
                       "scroll_tag":"main_table", "scroll_status":"top"}
            return render(request, "web/data.html", context=context)
    if db == "expense":
        if "choice" in request.POST:
            items = dict(request.POST).get("choice")
            for pk in items:
                item = Expense.objects.get(pk=int(pk))
                item.delete()
            return redirect(f"{reverse(f'web:{db}')}?scroll_tag=main_table&scroll_status=top")
        else:
            data_list = list(Expense.objects.filter(this_user=request.user))
            context = {"datas": enumerate(data_list), "title": "expense", "multi_delete_mod": True,
                       "scroll_tag": "main_table", "scroll_status": "top"}
            return render(request, "web/data.html", context=context)
    else:
        return Http404("not Found!")


def statistics(request):
    """statistic page view"""
    if request.user.is_authenticated and not request.user.is_superuser:
        # income
        month_incomes = dict()
        for income_obj in Income.objects.filter(this_user=request.user):
            month = income_obj.date.month
            if month not in month_incomes.keys():
                month_incomes.update({month: 0})
            month_incomes[month] += income_obj.amount
        income_data = list(month_incomes.values())
        income_label = list(month_incomes.keys())
        # expense
        month_expenses = dict()
        for expense_obj in Expense.objects.filter(this_user=request.user):
            month = expense_obj.date.month
            if month not in month_expenses.keys():
                month_expenses.update({month: 0})
            month_expenses[month] += expense_obj.amount
        expense_data = list(month_expenses.values())
        expense_label = list(month_expenses.keys())
        # label
        label = income_label if len(income_label)>len(expense_label) else expense_label
        for item in label:
            if item == 1:
                label[label.index(item)] =  'Jan'
            elif item == 2:
                label[label.index(item)] =  'Feb'
            elif item == 3:
                label[label.index(item)] =  'Mar'
            elif item == 4:
                label[label.index(item)] =  'Apr'
            elif item == 5:
                label[label.index(item)] = 'May'
            elif item == 6:
                label[label.index(item)] =  'Jun'
            elif item == 7:
                label[label.index(item)] =  'Jul'
            elif item == 8:
                label[label.index(item)] =  'Aug'
            elif item == 9:
                label[label.index(item)] =  'Sep'
            elif item == 10:
                label[label.index(item)] =  'Oct'
            elif item == 11:
                label[label.index(item)] =  'Nov'
            elif item == 12:
                label[label.index(item)] =  'Dec'
        # saving money
        saving_data = list()
        months = month_incomes if len(month_incomes)>len(month_expenses) else month_expenses
        for month in months.keys():
            saving_data.append(month_incomes.get(month, 0)-month_expenses.get(month, 0))
        context = {"expense_data":expense_data, "income_data":income_data,
                   "saving_data":json.dumps(saving_data),
                   "label":json.dumps(label)}
        print(context["label"], type(context["label"]))
        return render(request, "web/statistics.html", context = context)
    else:
        raise Http404("Not Found!")
