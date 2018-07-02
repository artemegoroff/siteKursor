from django.contrib import sitemaps
from ege.models import NumberTaskEge, VarEge
from oge.models import NumberTaskOge, VariantOge
from ege.urls import urlpatterns as egeUrls
from django.core.urlresolvers import reverse


class EgeTaskSiteMap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return list(range(1, len(NumberTaskEge.objects.all()) + 1))

    def location(self, item):
        return reverse("ege:ege_task_detail", kwargs={"number_task": item})


class EgeVarSiteMap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return list(range(1, len(VarEge.objects.all()) + 1))

    def location(self, item):
        return reverse("ege:ege_get_var", kwargs={"variant_number": item})


class OgeTaskSiteMap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return list(range(1, len(NumberTaskOge.objects.all()) + 1))

    def location(self, item):
        return reverse("oge:oge_task_detail", kwargs={"number_task": item})


class OgeVarSiteMap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return list(range(1, len(VariantOge.objects.all()) + 1))

    def location(self, item):
        return reverse("oge:oge_get_var", kwargs={"variant_number": item})


class EgeStaticSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['home:main_page', 'ege:base_ege', 'oge:base_oge', 'ege:ege_list', 'oge:oge_list']

    def location(self, item):
        return reverse(item)
