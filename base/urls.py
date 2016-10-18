from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.start_page_render, name="start_page_render"),
    url(r'^logout$', views.logout_view, name="logout"),
    url(r'^login$', views.login_view, name="login"),
    url(r'^signup$', views.signup_view, name="signup"),
]
