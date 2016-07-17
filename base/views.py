from django.shortcuts import render


def start_page_render(request):
    template = "base/start_page/.html"
    return render(request, template)
