from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^communities/', views.communities_render, name="communities_render")
]
