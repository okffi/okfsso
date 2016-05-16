from django import forms
from django.utils.translation import ugettext_lazy as _, string_concat
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import (
    validate_password, password_validators_help_text_html
)
from django.contrib.auth.models import User

class RegisterForm(forms.Form):
    email = forms.EmailField(
        label=_("Email address"),
        widget=forms.TextInput(
            attrs={
                "placeholder": _("user@example.com"),
            }
        ),
    )
    username = forms.CharField(
        label=_("Display name"),
        widget=forms.TextInput(attrs={
            "autocomplete": "username"
        }),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "autocomplete": "new-password"
        }),
        label=_("Password")
    )
    password_again = forms.CharField(
        widget=forms.PasswordInput(),
        label=_("Password again"),
        help_text=string_concat(
            _("Your password must meet these requirements:"),
            password_validators_help_text_html())
    )
    next = forms.CharField(widget=forms.HiddenInput, required=False)

    def clean(self):
        if ("password" in self.cleaned_data
            and "password_again" in self.cleaned_data):
            if self.cleaned_data["password"] != self.cleaned_data["password_again"]:
                self.add_error("password",
                               forms.ValidationError(_("Passwords don't match")))
                self.add_error("password_again",
                               forms.ValidationError(_("Passwords don't match")))

        if "email" in self.cleaned_data:
            self.cleaned_data["username"] = self.get_username()

        if "username" in self.cleaned_data:
            username_exists = User.objects.filter(
                username=self.cleaned_data["username"]).count()
            if username_exists:
                self.add_error("username", forms.ValidationError(
                    _("Please choose another display name")))

        if "email" in self.cleaned_data:
            email_exists = User.objects.filter(
                email=self.cleaned_data["email"]).count()
            if email_exists:
                self.add_error("email", forms.ValidationError(
                    _("Please choose another email address")))

        if "password" in self.cleaned_data:
            validate_password(self.cleaned_data["password"])

        return self.cleaned_data

    def get_username(self):
        if self.cleaned_data.get("username"):
            return self.cleaned_data["username"]
        return self.cleaned_data["email"].split("@", 1)[0]

class LoginForm(forms.Form):
    user = None

    username = forms.CharField(
        label=_("User name"),
        widget=forms.TextInput(attrs={
            "autocomplete": "username"
        }),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "autocomplete": "current-password"
        }),
        label=_("Password")
    )
    next = forms.CharField(widget=forms.HiddenInput, required=False)

    def clean(self):
        self.user = authenticate(username=self.cleaned_data["username"],
                                 password=self.cleaned_data["password"])
        if not self.user:
            raise forms.ValidationError(_("Email or password did not match. Please try again."))
        return self.cleaned_data

class ChangePasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label=_("Old password"),
    )

    new_password = forms.CharField(
        widget=forms.PasswordInput,
        label=_("New password"),
    )
    new_password_again = forms.CharField(
        widget=forms.PasswordInput,
        label=_("New password again"),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        if "password" in self.cleaned_data:
            authenticated_user = authenticate(username=self.user.username,
                                              password=self.cleaned_data["password"])
            if not authenticated_user:
                self.add_error("password",
                               forms.ValidationError(_("Please provide the current password")))

        if ("new_password" in self.cleaned_data
            and "new_password_again" in self.cleaned_data):
            if self.cleaned_data["new_password"] != self.cleaned_data["new_password_again"]:
                self.add_error("new_password",
                               forms.ValidationError(_("Passwords don't match")))
                self.add_error("new_password_again",
                               forms.ValidationError(_("Passwords don't match")))

        return self.cleaned_data
