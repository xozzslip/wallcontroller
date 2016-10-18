from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^communities/$', views.communities_list, name="communities_list"),
    url(r'^communities/add$', views.add_community, name="add_community"),
    url(r'^communities/(?P<pk>\d+)/$', views.community, name="community"),
    url(r'^communities/(?P<pk>\d+)/disable$', views.change_disabled_status, name="change_disabled_status"),
]
