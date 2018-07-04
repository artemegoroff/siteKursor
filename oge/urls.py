from django.conf.urls import url
from . import views

app_name = 'oge'

urlpatterns = [
    url(r'^task/(?P<number_task>[0-9]+)$', views.oge_task_detail, name='oge_task_detail'),
    url(r'^var/(?P<variant_number>[0-9]+)$', views.oge_get_var, name='oge_get_var'),
    url(r'^videotask/(?P<id_task>[0-9]+)$', views.oge_videotask_detail, name='oge_videotask_detail'),
    url(r'^task/$', views.oge_task_list, name='oge_list'),
    url(r'^videotask/$', views.oge_videotask_list, name='oge_videotask_list'),
    url(r'^$', views.oge_home_page, name='base_oge'),
]
