from .sitemaps import EgeTaskSiteMap, EgeVarSiteMap, EgeVideoSiteMap, EgeStaticSiteMap
from .sitemaps import OgeTaskSiteMap, OgeVarSiteMap, OgeVideoSiteMap, OgeStaticSiteMap
import home.views as home_view

from .sitemaps import CoursePythonSiteMap, AllLastSiteMap
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.views.static import serve

sitemaps = {
    'egeStatic': EgeStaticSiteMap,
    'egeTask': EgeTaskSiteMap,
    'egeVar': EgeVarSiteMap,
    'egeRazbor': EgeVideoSiteMap,
    'ogeStatic': OgeStaticSiteMap,
    'ogeTask': OgeTaskSiteMap,
    'ogeVar': OgeVarSiteMap,
    'ogeRazbor': OgeVideoSiteMap,
    'coursePython': CoursePythonSiteMap,
    'allLast': AllLastSiteMap,
}

handler404 = home_view.e_handler404
handler500 = home_view.e_handler500

urlpatterns = [
    url(r'^$', include('home.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'sponsorship/', include('sponsorship.urls')),
    url(r'accounts/', include('accounts.urls')),
    url(r'^ege/', include('ege.urls')),
    url(r'^oge/', include('oge.urls')),
    url(r'^services/', include('services.urls')),
    url(r'^course/', include('videos.urls')),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'^robots.txt$', include('robots.urls')),
    url(r'^summernote/', include('django_summernote.urls')),
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
