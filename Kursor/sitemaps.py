from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from courses.models import LearningCourse, LearningModule, Lesson
from ege.models import NumberTaskEge, VarEge, VideoRazborEGE
from oge.models import NumberTaskOge, VariantOge, VideoRazborOGE


class LearningCourseSiteMap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return LearningCourse.objects.exclude(slug__isnull=True).exclude(slug='').order_by('pk')


class LearningModuleSiteMap(Sitemap):
    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return (
            LearningModule.objects.select_related('course')
            .exclude(slug__isnull=True).exclude(slug='')
            .exclude(course__slug__isnull=True).exclude(course__slug='')
            .order_by('pk')
        )


class LessonSiteMap(Sitemap):
    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return (
            Lesson.objects.select_related('module__course')
            .exclude(slug__isnull=True).exclude(slug='')
            .exclude(module__slug__isnull=True).exclude(module__slug='')
            .exclude(module__course__slug__isnull=True)
            .exclude(module__course__slug='').order_by('pk')
        )


class EgeTaskSiteMap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return NumberTaskEge.objects.order_by('number')

    def location(self, item):
        return reverse('ege:ege_task_detail', kwargs={'number_task': item.number})


class EgeVarSiteMap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return VarEge.objects.order_by('number_var')

    def location(self, item):
        return reverse('ege:ege_get_var', kwargs={'variant_number': item.number_var})


class EgeVideoSiteMap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return VideoRazborEGE.objects.order_by('pk')

    def location(self, item):
        return reverse('ege:ege_videotask_detail', kwargs={
            'id_theme': item.number_of_task_id,
            'id_task': item.pk,
        })


class OgeTaskSiteMap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return NumberTaskOge.objects.order_by('number')

    def location(self, item):
        return reverse('oge:oge_task_detail', kwargs={'number_task': item.number})


class OgeVarSiteMap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return VariantOge.objects.order_by('number_var')

    def location(self, item):
        return reverse('oge:oge_get_var', kwargs={'variant_number': item.number_var})


class OgeVideoSiteMap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return VideoRazborOGE.objects.order_by('pk')

    def location(self, item):
        return reverse('oge:oge_videotask_detail', kwargs={
            'id_theme': item.number_of_task_id,
            'id_task': item.pk,
        })


class EgeStaticSiteMap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return ['ege:base_ege', 'ege:ege_videotask_AllTask']

    def location(self, item):
        return reverse(item)


class OgeStaticSiteMap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return ['oge:base_oge', 'oge:oge_videotask_AllTask']

    def location(self, item):
        return reverse(item)


class AllLastSiteMap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return ['home:main_page', 'courses:courses_home']

    def location(self, item):
        return reverse(item)
