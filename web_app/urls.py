from django.conf.urls import patterns, url

from web_app import views,view_processing

urlpatterns = patterns('',
	
	#page render
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.user_login, name='login'),
    url(r'^list/(?P<unit_id>\d+)$', views.page_sign_list, name='page_sign_list'),
    url(r'^signature/(?P<unit_id>\d+)/$', views.page_signature, name='page_signature'),
    url(r'^manage', views.page_manage_menu, name='page_manage_menu'),
    url(r'^std_search', views.page_std_search, name='page_std_search'),
    url(r'^dblist', views.page_db_list, name='page_db_list'),
    url(r'^updateCard', views.page_fix_cardNumber, name='page_fix_cardNumber'),
    url(r'^visualize', views.page_visualize_record, name='page_visualize_record'),
    
    #operate method
    url(r'^unit_management', views.view_processing.op_manage_unit, name='op_manage_unit'),
    url(r'^scan_sign', view_processing.op_scan_sign, name='op_scan_sign'),
    url(r'^op_update_card', view_processing.op_update_card, name='op_update_card'),
    url(r'^op_particple_records', view_processing.op_particple_records, name='op_particple_records'),
    url(r'^op_std_profile', view_processing.op_std_profile, name='op_std_profile'),
    url(r'^op_bacth', view_processing.op_bacth, name='op_bacth'),
    url(r'^/(?P<unit_id>\d+)$', views.index, name='index'),
    
    # url(r'^remove_unit', views.remove_unit, name='remove_unit'),

)
