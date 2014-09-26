from django.conf.urls import patterns, url

from web_app import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^list/(?P<unit_id>\d+)$', views.list, name='list'),
    url(r'^signature/(?P<unit_id>\d+)/$', views.signature, name='signature'),
    url(r'^scan_sign', views.scan_sign, name='scan_sign'),
    url(r'^manage', views.manage, name='manage'),
)