"""create app views"""
import ssl, smtplib, json, os, pathlib, string, random
from email.message import EmailMessage
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from django.http import JsonResponse
from json import JSONEncoder
from django.views.decorators.csrf import csrf_exempt
from bestoon.settings import BASE_DIR
from .models import *
import datetime
from django.templatetags.static import static

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
            body = f"""
            please click link to activate your account:
            http://{request.get_host()}/register?email={email}&code={code}
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
        if PasswordResetCodes.objects.filter(code = code).exists():
            new_temp_user = PasswordResetCodes.objects.get(code=code)
            new_user = User.objects.create(username=new_temp_user.user_name, password=new_temp_user.password, email=email)
            this_token = random_str(48)
            Token.objects.create(token_m=this_token, user=new_user)
            PasswordResetCodes.objects.filter(code=code).delete()
            context = {"message":f"your account activated. now you can login. remember this token to register data. token:{this_token}"}
            return render(request, "web/login.html", context=context)
        else:
            context = {"message": "this activating code is not valid!", "status":True}
            return render(request, "web/register.html", context=context)
    else:
        context = {"message":"", "status":True}
        return render(request, "web/register.html", context=context)


