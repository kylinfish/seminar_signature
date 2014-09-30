from django.conf.urls import patterns, url

from web_app import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.auth_vertify, name='login'),
    url(r'^list/(?P<unit_id>\d+)$', views.list, name='list'),
    url(r'^signature/(?P<unit_id>\d+)/$', views.signature, name='signature'),
    url(r'^scan_sign', views.scan_sign, name='scan_sign'),
    url(r'^manage', views.manage, name='manage'),
    url(r'^unit_management', views.unit_management, name='unit_management'),
    url(r'^std_search', views.std_search, name='std_search'),
)
