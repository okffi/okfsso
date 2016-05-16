from django.conf.urls import url, include

from okfsso.core.views import (
    index,
    login,
    logout,
    register,
    change_password,
    apidoc,
    get_info,
    set_info
)

urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^login/$', login, name="login"),
    url(r'^logout/$', logout, name="logout"),
    url(r'^register/$', register, name="register"),
    url(r'^change-password/$', change_password, name="change-password"),
    url(r'^api-doc/$', apidoc, name="apidoc"),
    url(r'^api/get-info/$', get_info, name="get-info"),
    url(r'^api/set-info/$', set_info, name="set-info"),
]
