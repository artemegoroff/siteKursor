from .sitemaps import EgeTaskSiteMap, EgeVarSiteMap, EgeStaticSitemap, OgeTaskSiteMap, OgeVarSiteMap
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap

sitemaps = {
    'ege_static': EgeStaticSitemap,
    'ege_task': EgeTaskSiteMap,
    'ege_var': EgeVarSiteMap,
    'oge_task': OgeTaskSiteMap,
    'oge_var': OgeVarSiteMap,
}

urlpatterns = [
    url(r'^$', include('home.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^ege/', include('ege.urls')),
    url(r'^oge/', include('oge.urls')),
    url(r'^course/', include('videos.urls')),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'^robots.txt$', include('robots.urls')),
    url(r'^summernote/', include('django_summernote.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
