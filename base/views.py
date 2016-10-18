from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login, forms
from django.core.urlresolvers import reverse

from base.forms import RegistrationForm


def start_page_render(request):
    template = "base/start_page.html"
    return render(request, template)


def logout_view(request):
    logout(request)
    return redirect(reverse('base:start_page_render'))


def signup_view(request):
    template = "registration/signup.html"
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            user = authenticate(username=user.username, 
                                password=form.cleaned_data["password1"])
            login(request, user)
            return redirect(reverse('base:start_page_render'))
    else:
        form = RegistrationForm()
    return render(request, template, {"form": form})


def login_view(request):
    template = "registration/login.html"
    if request.method == "POST":
        form = forms.AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data["username"], 
                                password=form.cleaned_data["password"])
            login(request, user)
            return redirect(reverse('wallcontroller:communities_list'))
    else:
        form = RegistrationForm()
    return render(request, template, {"form": form})