from django.conf.urls import url
from . import views
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

app_name = 'videos'

urlpatterns = [
                  url(r'^python/(?P<number>[0-9]+)$', views.videos_python_theme, name='videos_python_theme'),
                  url(r'^python/$', views.videos_python_all, name='videos_python_all'),

                  url(r'^turtle/(?P<number>[0-9]+)$', views.videos_turtle_theme, name='videos_turtle_theme'),
                  url(r'^turtle/$', views.videos_turtle_all, name='videos_turtle_all'),
                  # url(r'^test/$', views.videos_test, name='videos_test'),
                  url(r'^$', views.videos_home, name='videos_home'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
