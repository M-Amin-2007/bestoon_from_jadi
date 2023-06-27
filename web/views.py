"""create app views"""
import ssl, smtplib, json, os, pathlib, string, random
from email.message import EmailMessage
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from bestoon.settings import BASE_DIR
from .models import *
import datetime
from django.templatetags.static import static

# TODO: add csrf tokens, add js validation to form before submit, add multiple delete for tables
# TODO: add edit button to tables
# TODO: user panel: 1-logout 2-change password, name, email , change the form of user button when it wasn't login
# TODO: move register button under sign in form, change "register" to "sign up"
url = static("web/secret.json")
now = datetime.datetime.now
def random_str(n):
    """returns a random str that not exit before this"""
    characters = string.ascii_lowercase + string.ascii_uppercase + string.digits + ["$", "%", "&", "^", "?"]
    random_string = ""
    for _ in range(n):
        random_string += random.choice(characters)
    return random_string



@csrf_exempt
def register(request):
    """register user."""
    if request.POST:
        if User.objects.filter(email=request.POST["email"]).exists():
            page_context = {"message": "this email was used before this.", "status":True}
            return render(request, "web/register.html", context=page_context)
        elif User.objects.filter(username=request.POST["username"]).exists():
            page_context = {"message": "this username was used before this.", "status":True}
            return render(request, "web/register.html", context=page_context)
        else:
            code = random_str(28)
            email = request.POST["email"]
            password = make_password(request.POST["password"])
            username = request.POST["username"]
            # send mail
            sender = 'bestoon2023@gmail.com'
            subject = "verify Bestoon account"
            prefix = "https://" if request.is_secure() else "http://"
            body = f"""
            please click link to activate your account:
            {prefix}{request.get_host()}/register?email={email}&code={code}
            """
            secret_file = pathlib.Path(os.path.join(BASE_DIR, f"web/{url}"))
            sender_host_password = json.loads(secret_file.read_text())
            em =EmailMessage()
            em["From"] = sender
            em["To"] = email
            em["Subject"] = subject
            em.set_content(body)
            ssl_context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl_context) as server:
                server.login(sender, sender_host_password)
                server.sendmail(sender, email, em.as_string())
            PasswordResetCodes.objects.create(email = email, date = now(), code = code, user_name = username, password= password)

            page_context = {"message": "click on link send to your email. it can be in spam part", "status":False}
            return render(request, "web/register.html", context=page_context)
    elif "code" in request.GET.keys():
        email = request.GET["email"]
        code = request.GET["code"]
        if PasswordResetCodes.objects.filter(code = code):
            new_temp_user = PasswordResetCodes.objects.get(code=code)
            new_user = User.objects.create(username=new_temp_user.user_name, password=new_temp_user.password, email=email)
            login(request, new_user)
            PasswordResetCodes.objects.filter(code=code).delete()
            return redirect(reverse("web:user"))
        else:
            context = {"message": "this activating code is not valid!", "status":True}
            return render(request, "web/register.html", context=context)
    else:
        context = {"message":"", "status":True}
        return render(request, "web/register.html", context=context)

def home(request):
    """manage home request."""
    return render(request, "web/home.html")


def user(request):
    """user panel view."""
    if request.user.is_authenticated:
        return render(request, "web/user.html")
    else:
        return redirect(reverse("web:login"))

@csrf_exempt
def login_view(request):
    """login page view."""
    if request.POST:
        this_user = authenticate(username=request.POST["username"], password=request.POST["password"])
        if this_user:
            login(request, this_user)
            return redirect(reverse("web:user"))
        else:
            context = {"message": "this user isn't exist or password is incorrect."}
            return render(request, "web/login.html", context=context)

    else:
        context = {"message":""}
        return render(request, "web/login.html" ,context=context)

@csrf_exempt
def income(request):
    """incomes"""
    if request.user.is_authenticated:
        if request.method == "POST":
            text = request.POST["text"]
            amount = request.POST["amount"]
            date = request.POST.get("date")
            if not date: date = now()
            Income.objects.create(text=text, amount=amount, date=date, this_user=request.user)
        data_list = list(Income.objects.filter(this_user=request.user))
        context = {"datas":enumerate(data_list), "title":"income"}
        return render(request, "web/data.html", context=context)
    else:
        return redirect(reverse("web:login"))

@csrf_exempt
def expense(request):
    """expenses"""
    if request.user.is_authenticated:
        if request.method == "POST":
            text = request.POST["text"]
            amount = request.POST["amount"]
            date = request.POST.get("date")
            if not date: date = now()
            Expense.objects.create(text=text, amount=amount, date=date, this_user=request.user)
        data_list = Expense.objects.filter(this_user=request.user)
        context = {"datas":enumerate(data_list), "title":"expense"}
        return render(request, "web/data.html", context=context)
    else:
        return redirect(reverse("web:login"))

@csrf_exempt
def delete_item(request, pk, db):
    """delete an income or expense from database."""
    if db == "income":
        Income.objects.get(pk=pk).delete()
        return redirect(reverse("web:income"))
    elif db == "expense":
        Expense.objects.get(pk=pk).delete()
        return redirect(reverse("web:expense"))
