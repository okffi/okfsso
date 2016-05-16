import json
import functools

from django.shortcuts import render, redirect
from django.http import (
    JsonResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden
)
from django.contrib.auth import (
    logout as auth_logout,
    login as auth_login,
    authenticate
)
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.http import is_safe_url
from django.views.decorators.csrf import csrf_exempt

from oauth2_provider.decorators import (
    protected_resource,
    rw_protected_resource
)

from okfsso.core.forms import LoginForm, RegisterForm, ChangePasswordForm

class JsonResponseBadRequest(JsonResponse, HttpResponseBadRequest):
    pass

class JsonResponseForbidden(JsonResponse, HttpResponseForbidden):
    pass


def index(request):
    if request.user.is_authenticated():
        return render(request, "account/dashboard.html")
    return render(request, "index.html")

def login(request):
    redirect_to = request.POST.get("next",
                                   request.GET.get("next", ''))

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            if form.user is not None:
                if form.user.is_active:
                    auth_login(request, form.user)
                    messages.add_message(
                        request, messages.SUCCESS,
                        _("Logged in successfully"))
                    if not is_safe_url(url=redirect_to,
                                       host=request.get_host()):
                        return redirect("index")

                    return redirect(redirect_to)
                else:
                    messages.add_message(
                        request, messages.ERROR,
                        _("Your account is disabled. Please contact webmaster."))
    else:
        form = LoginForm(initial={"next": redirect_to})

    return render(request, "account/login.html", {
        "form": form,
        "next": redirect_to,
    })

def register(request):
    redirect_to = request.POST.get("next",
                                   request.GET.get("next", ''))

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"]
            )
            user.set_password(form.cleaned_data["password"])
            user.save()

            authenticated_user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"]
            )
            auth_login(request, authenticated_user)

            messages.add_message(
                request, messages.SUCCESS,
                _("Registered successfully. Welcome aboard."))

            if not is_safe_url(url=redirect_to,
                               host=request.get_host()):
                return redirect("index")
            return redirect(redirect_to)
    else:
        form = RegisterForm(initial={"next": redirect_to})

    return render(request, "account/register.html", {
        "form": form,
        "next": redirect_to,
    })

@login_required
def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            request.user.set_password(form.cleaned_data["new_password"])
            request.user.save()
            messages.add_message(request, messages.SUCCESS, _("You have changed your password successfully."))
            return redirect("index")
    else:
        form = ChangePasswordForm(user=request.user)

    return render(request, "account/change_password.html", {"form": form})

@login_required
def logout(request):
    auth_logout(request)
    return redirect("index")

def apidoc(request):
    return render(request, "apidoc.html")

def token_required(scopes=None):
    scopes = scopes or []
    def decorator(f):
        @functools.wraps(f)
        def validator(request, *args, **kwargs):
            from oauth2_provider.oauth2_validators import OAuth2Validator
            from oauth2_provider.oauth2_backends import OAuthLibCore
            from oauthlib.oauth2 import Server

            core = OAuthLibCore(Server(OAuth2Validator()))
            valid, oauthlib_req = core.verify_request(request, scopes=scopes)
            if valid:
                request.token = oauthlib_req.access_token
                return f(request, *args, **kwargs)
            return JsonResponseForbidden({"error": "invalid token", "code": "INVALID_TOKEN"})
        return validator
    return decorator

@token_required()
def get_info(request):
    "Get all useful information for the token owner"
    apps = {}
    for info in request.token.user.appinfo_set.all():
        apps[info.app.client_id] = {
            "name": info.app.name,
            "info": json.loads(info.info)
        }

    user = {
        "username": request.user.username,
        "email": request.user.email,
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "is_staff": request.user.is_staff,
        "is_superuser": request.user.is_superuser,
        "date_joined": request.user.date_joined.isoformat(),
    }

    return JsonResponse({
        "content": {
            "user": user,
            "apps": apps,
        }
    })

@csrf_exempt
@token_required(["read", "write"])
def set_info(request):
    "Set given info json for the token client's app info"
    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponseBadRequest({
            "error": "request body is not valid JSON",
            "code": "NOT_JSON"
         })

    info, created = request.token.user.appinfo_set.get_or_create(
        app=request.token.application
    )
    info.info = json.dumps(data)
    info.save()

    return JsonResponse({"content": "ok"})
