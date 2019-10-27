from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'services'

urlpatterns = [
                  # url(r'^videotask/$', views.ege_videotask_AllTask, name='ege_videotask_AllTask'),

                  url(r'^$', views.services_home_page, name='services_home'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
