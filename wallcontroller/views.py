from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required


from .models import Community
from .forms import AddCommunityForm, ChangeCommunityForm


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
            url = form.cleaned_data["url"]
            community = Community(url=url, domen_name=domen_name,
                                  user_owner=request.user)
            community.save()
            return redirect(reverse('wallcontroller:community', args=(community.pk,)))
    else:
        form = AddCommunityForm()

    return render(request, template, {'form': form})


@login_required(login_url=reverse_lazy('base:login'))
def community(request, pk):
    template = "wallcontroller/community.html"
    community = Community.objects.get(pk=pk)
    if request.method == 'POST':
        form = ChangeCommunityForm(request.POST, instance=community)
        if form.is_valid():
            form.save()
    else:
        form = ChangeCommunityForm(instance=community)

    return render(request, template, {"community": community, "form": form})


@login_required(login_url=reverse_lazy('base:login'))
def change_disabled_status(request, pk):
    community = Community.objects.get(pk=pk)
    community.change_disabled_status()
    community.save()
    return redirect(reverse('wallcontroller:community', args=(pk,)))
