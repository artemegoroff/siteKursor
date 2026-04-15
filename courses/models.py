from django.db import models
from django.template.defaultfilters import slugify as django_slugify
from django.urls import reverse

alphabet = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
            'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
            'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ы': 'i', 'э': 'e', 'ю': 'yu',
            'я': 'ya'}


def slugify(s):
    """
    Overriding django slugify that allows to use russian words as well.
    """
    return django_slugify(''.join(alphabet.get(w, w) for w in s.lower()))


# Create your models here.

class LearningCourse(models.Model):
    slug = models.SlugField('Slug', unique=True, null=True, blank=True)
    title = models.CharField('Название курса', max_length=200)
    sort_order = models.PositiveIntegerField('Порядок', default=0, db_index=True)
    description = models.TextField('Описание курса', blank=True, null=True)
    seo_keywords = models.TextField('Keywords', blank=True, max_length=160)
    stepik = models.CharField('Stepik', max_length=200, blank=True, null=True)

    previous_course = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.title)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.sort_order}. {self.title}' if self.sort_order else self.title

    def seo_title(self):
        return f'Курс "{self.title}"'

    def get_absolute_url(self):
        return reverse('courses:course_detail', kwargs={'course_slug': self.slug})

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['sort_order', 'title']


class LearningModule(models.Model):
    course = models.ForeignKey(LearningCourse, on_delete=models.CASCADE, related_name='modules', verbose_name='Курс')
    slug = models.SlugField('Slug', null=True, blank=True)
    title = models.CharField('Название модуля', max_length=200)
    sort_order = models.PositiveIntegerField('Порядок', default=0, db_index=True)
    description = models.TextField('Описание модуля', blank=True, null=True)
    stepik = models.CharField('Stepik', max_length=200, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.title)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.course} / {self.sort_order}. {self.title}' if self.sort_order else f'{self.course} / {self.title}'

    def get_absolute_url(self):
        return reverse(
            'courses:module_detail',
            kwargs={
                'course_slug': self.course.slug,
                'module_slug': self.slug,
            }
        )

    class Meta:
        verbose_name = 'Модуль'
        verbose_name_plural = 'Модули'
        ordering = [ 'sort_order', 'course','title']
        unique_together = ('course', 'slug')


class Lesson(models.Model):
    module = models.ForeignKey(LearningModule, on_delete=models.CASCADE, related_name='lessons', verbose_name='Модуль')
    slug = models.SlugField('Slug', null=True, blank=True)
    title = models.CharField('Название урока', max_length=200)
    sort_order = models.PositiveIntegerField('Порядок', default=0, db_index=True)
    article = models.TextField('Текст урока', blank=True, null=True)
    youtube_id = models.CharField('YouTube ID', max_length=75, blank=True, null=True)
    rutube_id = models.CharField('Rutube ID', max_length=75, blank=True, null=True)
    stepik = models.CharField('Stepik', max_length=200, blank=True, null=True)
    seo_keywords = models.TextField('Keywords', blank=True, max_length=160)

    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.title)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.module} / {self.sort_order}. {self.title}' if self.sort_order else f'{self.module} / {self.title}'

    def seo_title(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'courses:lesson_detail',
            kwargs={
                'course_slug': self.module.course.slug,
                'module_slug': self.module.slug,
                'lesson_slug': self.slug,
            }
        )

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['sort_order', 'module', 'title']
        unique_together = ('module', 'slug')