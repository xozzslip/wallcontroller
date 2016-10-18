from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required


from .models import Community
from .forms import AddCommunityForm


@login_required(login_url=reverse_lazy('base:login'))
def communities_list(request):
    template = "wallcontroller/communities_list.html"
    communities = Community.objects.filter(user_owner=request.user)
    return render(request, template, {"communities": communities})


@login_required(login_url=reverse_lazy('base:login'))
def add_community(request):
    template = "wallcontroller/add_community.html"
    if request.method == 'POST':
        form = AddCommunityForm(request.POST)
        if form.is_valid():
            domen_name = form.domen_name_from_url()
            community = Community(domen_name=domen_name, user_owner=request.user)
            community.save()
            return redirect(reverse('wallcontroller:communities_list'))
    else:
        form = AddCommunityForm()

    return render(request, template, {'form': form})


@login_required(login_url=reverse_lazy('base:login'))
def community(request, pk):
    template = "wallcontroller/community.html"
    community = Community.objects.get(pk=pk)
    return render(request, template, {"community": community})


@login_required(login_url=reverse_lazy('base:login'))
def change_disabled_status(request, pk):
    community = Community.objects.get(pk=pk)
    if community.disabled:
        community.disabled = False
    else:
        community.disabled = True
    community.save()
    return redirect(reverse('wallcontroller:community', args=pk))

