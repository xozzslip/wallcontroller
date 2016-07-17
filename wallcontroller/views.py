from django.shortcuts import render


def communities_render(request):
    template = "wallcontroller/communities.html"
    return render(request, template)
