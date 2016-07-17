from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.start_page_render, name="start_page_render")
]
