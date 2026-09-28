import django
from django.conf.urls import include
from django.contrib import admin

if django.VERSION >= (3, 1):
    from django.urls import re_path as url
else:
    from django.conf.urls import url


if django.VERSION < (1, 9):
    admin_urls = include(admin.site.urls)
else:
    admin_urls = admin.site.urls

urlpatterns = [
    url(r'^admin/', admin_urls),
]
