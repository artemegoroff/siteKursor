from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'oge'

urlpatterns = [
    url(r'^task/(?P<number_task>[0-9]+)$', views.oge_task_detail, name='oge_task_detail'),
    url(r'^var/(?P<variant_number>[0-9]+)$', views.oge_get_var, name='oge_get_var'),

    url(r'^videotask/(?P<id_theme>[0-9]+)/(?P<id_task>[0-9]+)$', views.oge_videotask_detail,
        name='oge_videotask_detail'),
    url(r'^videotask/(?P<id_theme>[0-9]+)$', views.oge_videotask_ONEtheme,
        name='oge_videotask_ONEtheme'),
    url(r'^videotask/$', views.oge_videotask_AllTask, name='oge_videotask_AllTask'),

    url(r'^$', views.oge_home_page, name='base_oge'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
