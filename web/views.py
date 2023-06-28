"""create app views"""
import ssl, smtplib, json, os, pathlib, string, random
from email.message import EmailMessage
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from bestoon.settings import BASE_DIR
from .models import *
import datetime
from django.templatetags.static import static

# TODO: add csrf tokens, add js validation to form before submit, add multiple delete for tables
# TODO: add edit button to tables
# TODO: move register button under sign in form, change name of "register" to "sign up"
# TODO: add suggestions part, make navbar constant, unable user to login when user is authenticated
# TODO: change Home page figure when user login, correct login page title
# TODO: change paragraphs and expressions, move user account (making, changing, login) parts to another app
# TODO: move sender email to secret.json
# TODO: make lower email and make capital usernames before saving

url = static("web/secret.json")
now = datetime.datetime.now
def random_str(n):
    """returns a random str that not exit before this"""
    characters = string.ascii_lowercase + string.ascii_uppercase + string.digits
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
            secret_file = pathlib.Path(os.path.join(BASE_DIR, f"web/{url}"))
            sender_info = json.loads(secret_file.read_text())
            sender = sender_info.get("sender_email")
            sender_password = sender_info.get("password")
            prefix = "https://" if request.is_secure() else "http://"
            body = f"""
            please click link to activate your account:
            {prefix}{request.get_host()}/register?email={email}&code={code}
            """
            em =EmailMessage()
            em["From"] = sender
            em["To"] = email
            em["Subject"] = "Bestoon"
            em.set_content(body)
            ssl_context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl_context) as server:
                server.login(sender, sender_password)
                server.sendmail(sender, email, em.as_string())
            PasswordResetCodes.objects.create(email = email, date = now(), code = code, user_name = username, password= password)

            return render(request, "web/email_send.html")
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


def user_view(request):
    """user panel view."""
    if request.user.is_authenticated:
        return render(request, "web/user.html")
    else:
        return redirect(reverse("web:login"))

@csrf_exempt
def login_view(request):
    """login page view."""
    if request.POST:
        if not User.objects.filter(username=request.POST["username"]):
            context = {"message": "this user isn't exist."}
            return render(request, "web/login.html", context=context)
        else:
            this_user = authenticate(username=request.POST["username"], password=request.POST["password"])
            if this_user is not None:
                login(request, this_user)
                return redirect(reverse("web:user"))
            else:
                context = {"message": "password is incorrect."}
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

@csrf_exempt
def change_password(request):
    """change password"""
    if request.method == "GET":
        raise Http404("not found!")
    elif request.user.is_authenticated:
        if "pass1" in request.POST:
            pass1 = request.POST.get("pass1")
            new_pass_repeat = request.POST.get("pass2")
            new_pass = request.POST.get("new_pass")
            this_user = request.user
            if new_pass != new_pass_repeat:
                context = {"message": "your repeat field isn't correct!"}
                return render(request, "web/change_password.html", context=context)
            elif authenticate(username=this_user.username, password=pass1) != this_user:
                context = {"message": "the old password is incorrect!"}
                return render(request, "web/change_password.html", context=context)
            else:
                this_user.set_password(new_pass)
                this_user.save()
                login(request, this_user)
                return redirect(reverse("web:user"))
        else:
            context={"message":""}
            return render(request, "web/change_password.html", context=context)
    else:
        return redirect(reverse("web:login"))

@csrf_exempt
def change_username(request):
    """change password"""
    if request.method == "GET":
        raise Http404("not found!")
    elif request.user.is_authenticated:
        if "new_username" in request.POST:
            new_username = request.POST.get("new_username")
            this_user = request.user
            if User.objects.filter(username=new_username).exists():
                context = {"message": "this username exists. you can't use it."}
                return render(request, "web/change_username.html", context=context)
            else:
                this_user.username = new_username
                this_user.save()
                login(request, this_user)
                return redirect(reverse("web:user"))
        else:
            context={"message":""}
            return render(request, "web/change_username.html", context=context)
    else:
        return redirect(reverse("web:login"))

@csrf_exempt
def change_email(request):
    """change password"""
    if request.user.is_authenticated:
        if request.method == "GET":
            if "code" in request.GET:
                code = request.GET.get("code")
                email = request.GET.get("email")
                code_temp = PasswordResetCodes.objects.get(code=code)
                this_user = request.user
                if not code_temp.user_name == this_user.username:
                    context = {"message":"this activating code is not valid for this user."}
                    return render(request, "web/change_email.html", context=context)
                else:
                    this_user.email = email
                    this_user.save()
                    login(request, this_user)
                    return redirect(reverse("web:user"))
            else:
                raise Http404("not found!")

        if "new_email" in request.POST:
            new_email = request.POST.get("new_email")
            this_user = request.user
            if User.objects.filter(username=new_email).exists():
                context = {"message": "this email was used before this."}
                return render(request, "web/change_email.html", context=context)
            else:
                code = random_str(30)
                secret_file = pathlib.Path(os.path.join(BASE_DIR, f"web/{url}"))
                sender_info = json.loads(secret_file.read_text())
                sender = sender_info.get("sender_email")
                sender_password = sender_info.get("password")
                prefix = "https://" if request.is_secure() else "http://"
                body = f"""
                click on this link to change your email to this email:
                {prefix}{request.get_host()}/change_email/?email={new_email}&code={code}
                """
                message = EmailMessage()
                message["Subject"] = "Bestoon"
                message["From"] = sender
                message["To"] = new_email
                message.set_content(body)
                ssl_context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl_context) as server:
                    server.login(sender, sender_password)
                    server.sendmail(sender, new_email, message.as_string())
                PasswordResetCodes.objects.create(code=code, user_name=this_user.username, password="",\
                                                  date=now(), email=new_email)
                return render(request, "web/email_send.html")
        else:
            context={"message":""}
            return render(request, "web/change_email.html", context=context)
    else:
        return redirect(reverse("web:login"))

@csrf_exempt
def logout_view(request):
    """log out user"""
    if request.method == "GET":
        raise Http404("not found!")
    else:
        logout(request)
        return redirect(reverse("web:user"))