from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import slugify as django_slugify
from django.urls import reverse


alphabet = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
    'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
    'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
    'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
    'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
    'ш': 'sh', 'щ': 'shch', 'ы': 'y', 'э': 'e', 'ю': 'yu',
    'я': 'ya',
}


def slugify(value):
    return django_slugify(
        ''.join(alphabet.get(char, char) for char in value.lower())
    )


class LearningCourse(models.Model):
    slug = models.SlugField(
        'Slug', unique=True, null=True, blank=True,
    )
    title = models.CharField('Название курса', max_length=200)
    sort_order = models.PositiveIntegerField(
        'Порядок', default=0, db_index=True,
    )
    description = models.TextField(
        'Описание курса', blank=True, null=True,
    )
    seo_keywords = models.TextField(
        'Keywords', blank=True, max_length=160,
    )
    stepik = models.CharField(
        'Stepik', max_length=200, blank=True, null=True,
    )
    previous_course = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.title)
        return super().save(*args, **kwargs)

    def __str__(self):
        if self.sort_order:
            return f'{self.sort_order}. {self.title}'
        return self.title

    def seo_title(self):
        return f'Курс "{self.title}"'

    def get_absolute_url(self):
        return reverse(
            'courses:course_detail',
            kwargs={'course_slug': self.slug},
        )

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['sort_order', 'title']


class LearningModule(models.Model):
    course = models.ForeignKey(
        LearningCourse,
        on_delete=models.CASCADE,
        related_name='modules',
        verbose_name='Курс',
    )
    slug = models.SlugField('Slug', null=True, blank=True)
    title = models.CharField('Название модуля', max_length=200)
    sort_order = models.PositiveIntegerField(
        'Порядок', default=0, db_index=True,
    )
    description = models.TextField(
        'Описание модуля', blank=True, null=True,
    )
    stepik = models.CharField(
        'Stepik', max_length=200, blank=True, null=True,
    )

    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.title)
        return super().save(*args, **kwargs)

    def __str__(self):
        if self.sort_order:
            return f'{self.course} / {self.sort_order}. {self.title}'
        return f'{self.course} / {self.title}'

    def get_absolute_url(self):
        return reverse(
            'courses:module_detail',
            kwargs={
                'course_slug': self.course.slug,
                'module_slug': self.slug,
            },
        )

    class Meta:
        verbose_name = 'Модуль'
        verbose_name_plural = 'Модули'
        ordering = ['sort_order', 'course', 'title']
        unique_together = ('course', 'slug')


class Lesson(models.Model):
    module = models.ForeignKey(
        LearningModule,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Модуль',
    )
    parent = models.ForeignKey(
        'self',
        verbose_name='Родительский урок',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='children',
    )
    slug = models.SlugField('Slug', null=True, blank=True)
    title = models.CharField('Название урока', max_length=200)
    sort_order = models.PositiveIntegerField(
        'Порядок', default=0, db_index=True,
    )
    seo_keywords = models.TextField(
        'Keywords', blank=True, max_length=160,
    )

    def clean(self):
        super().clean()

        if self.pk and self.children.exclude(
            module_id=self.module_id,
        ).exists():
            raise ValidationError({
                'module': (
                    'Нельзя изменить модуль отдельно от подуроков.'
                ),
            })

        if self.parent_id is None:
            return

        if self.pk and self.parent_id == self.pk:
            raise ValidationError({
                'parent': (
                    'Урок не может быть родителем самому себе.'
                ),
            })

        visited = {self.pk} if self.pk else set()
        ancestor = self.parent

        while ancestor is not None:
            if ancestor.pk in visited:
                raise ValidationError({
                    'parent': 'В иерархии уроков обнаружен цикл.',
                })

            visited.add(ancestor.pk)

            if ancestor.module_id != self.module_id:
                raise ValidationError({
                    'parent': (
                        'Родительский урок должен быть '
                        'в том же модуле.'
                    ),
                })

            ancestor = ancestor.parent

    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.title)
        return super().save(*args, **kwargs)

    def __str__(self):
        if self.sort_order:
            return f'{self.module} / {self.sort_order}. {self.title}'
        return f'{self.module} / {self.title}'

    def seo_title(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'courses:lesson_detail',
            kwargs={
                'course_slug': self.module.course.slug,
                'module_slug': self.module.slug,
                'lesson_slug': self.slug,
            },
        )

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['sort_order', 'module', 'title']
        unique_together = ('module', 'slug')


class LessonBlock(models.Model):
    class Kind(models.TextChoices):
        TEXT = 'text', 'Текст'
        VIDEO = 'video', 'Видео'
        PRACTICE = 'practice', 'Практика'

    lesson = models.ForeignKey(
        Lesson,
        verbose_name='Урок',
        related_name='blocks',
        on_delete=models.CASCADE,
    )
    kind = models.CharField(
        'Тип блока',
        max_length=20,
        choices=Kind.choices,
    )
    title = models.CharField(
        'Заголовок', max_length=200, blank=True,
    )
    sort_order = models.PositiveIntegerField(
        'Порядок', default=0, db_index=True,
    )
    content = models.TextField('Текст', blank=True)
    youtube_id = models.CharField(
        'YouTube ID', max_length=75, blank=True,
    )
    rutube_id = models.CharField(
        'Rutube ID', max_length=75, blank=True,
    )
    practice_url = models.URLField(
        'Ссылка на практику', max_length=500, blank=True,
    )

    def __str__(self):
        return (
            f'{self.lesson.title} / '
            f'{self.sort_order}. '
            f'{self.title or self.get_kind_display()}'
        )

    class Meta:
        verbose_name = 'Блок урока'
        verbose_name_plural = 'Блоки урока'
        ordering = ['sort_order', 'id']


class LegacyCourseRedirect(models.Model):
    old_path = models.CharField('Старый путь', max_length=500, unique=True)
    course = models.ForeignKey(
        LearningCourse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='legacy_redirects',
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='legacy_redirects',
    )

    def get_absolute_url(self):
        if self.lesson_id:
            return self.lesson.get_absolute_url()
        if self.course_id:
            return self.course.get_absolute_url()
        return reverse('courses:courses_home')

    class Meta:
        verbose_name = 'Перенаправление старого курса'
        verbose_name_plural = 'Перенаправления старых курсов'
