from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms      


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required = True)

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        username = self.cleaned_data["email"].split("@")[0]
        user.username = username
        if commit:
            user.save()
        return user


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required = True)

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


