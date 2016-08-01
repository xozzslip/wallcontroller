from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^communities/$', views.CommunitiesList.as_view(), name="communities_list"),
    url(r'^communities/(?P<pk>\d+)/', views.CommunitySingle.as_view(), name="single_community")
]
