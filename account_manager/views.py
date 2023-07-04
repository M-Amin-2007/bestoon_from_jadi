"""manage account views."""
import datetime, string, random, pathlib, os, json, ssl, smtplib, re, pytz
from email.message import EmailMessage
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from account_manager.models import AccountActivatingCodes
from bestoon.settings import BASE_DIR

now = datetime.datetime.now
FORGOT_LINK_TIME = 30
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
        email = request.POST.get("email").lower()
        password = make_password(request.POST.get("password"))
        username = request.POST.get("username").lower().title()
        if User.objects.filter(email=email).exists():
            page_context = {"message": "this email was used before this."}
            return render(request, "account_manager/register.html", context=page_context)
        elif User.objects.filter(username=username).exists():
            page_context = {"message": "this username was used before this."}
            return render(request, "account_manager/register.html", context=page_context)
        else:
            code = random_str(28)
            # send mail
            secret_file = pathlib.Path(os.path.join(BASE_DIR, f"account_manager/static/account_manager/secret.json"))
            sender_info = json.loads(secret_file.read_text())
            sender = sender_info.get("sender_email")
            sender_password = sender_info.get("password")
            prefix = "https://" if request.is_secure() else "http://"
            body = f"""
            please click link to activate your account:
            {prefix}{request.get_host()}/account/register?email={email}&code={code}
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
            AccountActivatingCodes.objects.create(email = email, date = now(), code = code, user_name = username, password= password)

            return render(request, "account_manager/email_send.html")
    elif "code" in request.GET.keys():
        email = request.GET["email"]
        code = request.GET["code"]
        if AccountActivatingCodes.objects.filter(code = code):
            new_temp_user = AccountActivatingCodes.objects.get(code=code)
            new_user = User.objects.create(username=new_temp_user.user_name, password=new_temp_user.password, email=email)
            login(request, new_user)
            AccountActivatingCodes.objects.filter(code=code).delete()
            return redirect(reverse("account_manager:user"))
        else:
            context = {"message": "this activating code is not valid!"}
            return render(request, "account_manager/register.html", context=context)
    else:
        context = {"message":""}
        return render(request, "account_manager/register.html", context=context)


def user_view(request):
    """user panel view."""
    if request.user.is_authenticated:
        return render(request, "account_manager/user.html")
    else:
        return redirect(reverse("account_manager:login"))


@csrf_exempt
def login_view(request):
    """login page view."""
    if request.POST:
        username = request.POST.get("username").lower().title()
        if not User.objects.filter(username=username) or User.objects.get(username=username).is_superuser:
            context = {"message": "this user isn't exist."}
            return render(request, "account_manager/login.html", context=context)
        else:
            this_user = authenticate(username=username, password=request.POST.get("password"))
            if this_user is not None:
                login(request, this_user)
                return redirect(reverse("account_manager:user"))
            else:
                context = {"message": "password is incorrect."}
                return render(request, "account_manager/login.html", context=context)

    else:
        context = {"message":""}
        return render(request, "account_manager/login.html", context=context)


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
                return render(request, "account_manager/change_password.html", context=context)
            elif authenticate(username=this_user.username, password=pass1) != this_user:
                context = {"message": "the old password is incorrect!"}
                return render(request, "account_manager/change_password.html", context=context)
            else:
                this_user.set_password(new_pass)
                this_user.save()
                login(request, this_user)
                return redirect(reverse("account_manager:user"))
        else:
            context={"message":""}
            return render(request, "account_manager/change_password.html", context=context)
    else:
        return redirect(reverse("account_manager:login"))


@csrf_exempt
def change_username(request):
    """change password"""
    if request.method == "GET":
        raise Http404("not found!")
    elif request.user.is_authenticated:
        if "new_username" in request.POST:
            new_username = request.POST.get("new_username").lower().title()
            this_user = request.user
            if User.objects.filter(username=new_username).exists():
                context = {"message": "this username exists. you can't use it."}
                return render(request, "account_manager/change_username.html", context=context)
            else:
                this_user.username = new_username
                this_user.save()
                login(request, this_user)
                return redirect(reverse("account_manager:user"))
        else:
            context={"message":""}
            return render(request, "account_manager/change_username.html", context=context)
    else:
        return redirect(reverse("account_manager:login"))


@csrf_exempt
def change_email(request):
    """change password"""
    if request.user.is_authenticated:
        if request.method == "GET":
            if "code" in request.GET:
                code = request.GET.get("code")
                email = request.GET.get("email").lower()
                code_temp = AccountActivatingCodes.objects.get(code=code)
                this_user = request.user
                if not code_temp.user_name == this_user.username:
                    context = {"message":"this activating code is not valid for this user."}
                    return render(request, "account_manager/change_email.html", context=context)
                else:
                    this_user.email = email
                    this_user.save()
                    login(request, this_user)
                    return redirect(reverse("account_manager:user"))
            else:
                raise Http404("not found!")

        if "new_email" in request.POST:
            new_email = request.POST.get("new_email").lower()
            this_user = request.user
            if User.objects.filter(username=new_email).exists():
                context = {"message": "this email was used before this."}
                return render(request, "account_manager/change_email.html", context=context)
            else:
                code = random_str(30)
                secret_file = pathlib.Path(os.path.join(BASE_DIR, f"account_manager/static/account_manager/secret.json"))
                sender_info = json.loads(secret_file.read_text())
                sender = sender_info.get("sender_email")
                sender_password = sender_info.get("password")
                prefix = "https://" if request.is_secure() else "http://"
                body = f"""
                click on this link to change your email to this email:
                {prefix}{request.get_host()}/account/change_email/?email={new_email}&code={code}
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
                AccountActivatingCodes.objects.create(code=code, user_name=this_user.username, password="",
                                                  date=now(), email=new_email)
                return render(request, "account_manager/email_send.html")
        else:
            context={"message":""}
            return render(request, "account_manager/change_email.html", context=context)
    else:
        return redirect(reverse("account_manager:login"))


@csrf_exempt
def logout_view(request):
    """log out user"""
    if request.method == "GET":
        raise Http404("not found!")
    else:
        logout(request)
        return redirect(reverse("account_manager:user"))


@csrf_exempt
def delete_account_view(request):
    """delete_account_view"""
    if request.method == "GET":
        raise Http404("not found!")
    else:
        user = request.user
        user.delete()
        return redirect(reverse("account_manager:login"))


@csrf_exempt
def forgot_password_view(request):
    """forgot pass word view"""
    if "password1" in request.POST.keys():
        this_user = request.user
        new_pass_repeat = request.POST.get("password2")
        new_pass = request.POST.get("password1")
        if new_pass != new_pass_repeat:
            context = {"message": "your repeat field isn't correct!"}
            return render(request, "account_manager/change_password.html", context=context)
        else:
            this_user.set_password(new_pass)
            this_user.save()
            login(request, this_user)
            return redirect(reverse("account_manager:user"))
    elif request.POST:
        username = request.POST.get("username").lower().title()
        email = request.POST.get("email").lower()
        try:
            this_user = User.objects.get(username=username)
        except AccountActivatingCodes.DoesNotExist:
            context = {"message": "username not found!"}
            return render(request, "account_manager/forgot_password.html", context=context)
        else:
            if re.sub(r"\s\w+@", "@", this_user.email) == email:
                code = random_str(28)
                # send mail
                secret_file = pathlib.Path(
                    os.path.join(BASE_DIR, f"account_manager/static/account_manager/secret.json"))
                sender_info = json.loads(secret_file.read_text())
                sender = sender_info.get("sender_email")
                sender_password = sender_info.get("password")
                prefix = "https://" if request.is_secure() else "http://"
                body = f"""
                please click link to activate your account:
                {prefix}{request.get_host()}/account/forgot_password/?email={email}&code={code}&username={username}
                this activating code is valid for {FORGOT_LINK_TIME} minutes
                """
                em = EmailMessage()
                em["From"] = sender
                em["To"] = email
                em["Subject"] = "Bestoon forgot password"
                em.set_content(body)
                ssl_context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl_context) as server:
                    server.login(sender, sender_password)
                    server.sendmail(sender, email, em.as_string())
                AccountActivatingCodes.objects.create(email=email, date=now(), code=code, user_name=username,
                                                      password="")
                return render(request, "account_manager/email_send.html")
            else:
                context = {"message": "this email isn't for this user."}
                return render(request, "account_manager/forgot_password.html", context=context)
    elif "code" in request.GET.keys():
        username = request.GET.get("username")
        email = request.GET.get("email")
        code = request.GET.get("code")
        try: temp_code = AccountActivatingCodes.objects.get(user_name=username, code=code, email=email)
        except AccountActivatingCodes.DoesNotExist:
            context = {"message": "forgot password code is not valid. create new one with this form!"}
            return render(request, "account_manager/forgot_password.html", context=context)
        else:
            time_difference = pytz.utc.localize(now())-temp_code.date
            if time_difference.seconds > FORGOT_LINK_TIME * 60:
                context = {"message": "forgot password code time is over. create new one with this form!"}
                return render(request, "account_manager/forgot_password.html", context=context)
            else:
                this_user = User.objects.get(username=username)
                login(request, this_user)
                context={"change_password":True}
                return render(request, "account_manager/forgot_password.html", context=context)
        return redirect(reverse("web:home"))
    else:
        return render(request, "account_manager/forgot_password.html")
