from django.contrib import sitemaps
from ege.models import NumberTaskEge, VarEge, VideoRazborEGE
from oge.models import NumberTaskOge, VariantOge, VideoRazborOGE
from videos.models import Course
from ege.urls import urlpatterns as egeUrls
from django.shortcuts import reverse


class CoursePythonSiteMap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return list(range(1, len(Course.objects.all().filter(language=Course.PYTHON)) + 1))

    def location(self, item):
        return reverse("videos:videos_python_theme", kwargs={"number": item})


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


class EgeVideoSiteMap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        razbors = VideoRazborEGE.objects.all()
        return sorted(list(razbors.values_list('id', flat=True).distinct()))

    def location(self, item):
        return reverse("ege:ege_videotask_detail", kwargs={"id_task": item})


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


class OgeVideoSiteMap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        razbors = VideoRazborOGE.objects.all()
        return list(razbors.values_list('id', flat=True).distinct())

    def location(self, item):
        return reverse("oge:oge_videotask_detail", kwargs={"id_task": item})


class EgeStaticSiteMap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['ege:base_ege', 'ege:ege_list', 'ege:ege_videotask_list']

    def location(self, item):
        return reverse(item)


class OgeStaticSiteMap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['oge:base_oge', 'oge:oge_list', 'oge:oge_videotask_list']

    def location(self, item):
        return reverse(item)


class AllLastSiteMap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['home:main_page', 'videos:videos_python_all']

    def location(self, item):
        return reverse(item)
