from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'ege'

urlpatterns = [
                  url(r'^task/(?P<number_task>[1-9]|[1][\d]|2[0-7])$', views.ege_task_detail, name='ege_task_detail'),
                  url(r'^var/(?P<variant_number>[0-9]+)$', views.ege_get_var, name='ege_get_var'),
                  url(r'^videotask/$', views.ege_videotask_AllTask, name='ege_videotask_AllTask'),
                  url(r'^videotask/(?P<id_theme>[0-9]+)/(?P<id_task>[0-9]+)$', views.ege_videotask_detail,
                      name='ege_videotask_detail'),
                  url(r'^videotask/(?P<id_theme>[0-9]+)$', views.ege_videotask_ONEtheme,
                      name='ege_videotask_ONEtheme'),

                  url(r'^$', views.ege_home_page, name='base_ege'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
