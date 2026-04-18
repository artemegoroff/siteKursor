from django.db import migrations
from django.utils.text import slugify


LANGUAGE_TO_COURSE = {
    'PYT': 'Python',
    'PAS': 'Pascal',
    'CPP': 'C++',
    'TUR': 'Turtle',
    'PGA': 'Pygame',
    'OOP': 'OOP Python',
    'TKN': 'Tkinter',
    'DJA': 'Django',
}


def forward(apps, schema_editor):
    OldCourse = apps.get_model('videos', 'Course')
    LearningCourse = apps.get_model('courses', 'LearningCourse')
    LearningModule = apps.get_model('courses', 'LearningModule')
    Lesson = apps.get_model('courses', 'Lesson')

    modules_by_language = {}

    for number, (lang_code, course_title) in enumerate(LANGUAGE_TO_COURSE.items(), start=1):
        course, _ = LearningCourse.objects.get_or_create(
            slug=slugify(course_title),
            defaults={
                'title': course_title,
                'description': 'Автоматически создано миграцией',
            }
        )

        module, _ = LearningModule.objects.get_or_create(
            course=course,
            slug='vvedenie',
            defaults={
                'title': 'Введение',
                'description': 'Автоматически создано миграцией',
            }
        )

        modules_by_language[lang_code] = module

    for old_lesson in OldCourse.objects.all().order_by('language', 'number_theme', 'id'):
        module = modules_by_language.get(old_lesson.language)
        if not module:
            continue

        Lesson.objects.get_or_create(
            module=module,
            slug=old_lesson.slug or f'lesson-{old_lesson.id}',
            defaults={
                'title': old_lesson.theme or f'Урок {old_lesson.id}',
                'sort_order': old_lesson.number_theme,
                'article': old_lesson.article,
                'youtube_id': old_lesson.youtube_id,
                'rutube_id': old_lesson.rutube_id,
                'stepik': old_lesson.stepic,
                'seo_keywords': old_lesson.seo_keywords,
            }
        )


def backward(apps, schema_editor):
    LearningCourse = apps.get_model('courses', 'LearningCourse')

    LearningCourse.objects.filter(
        description='Автоматически создано миграцией',
        title__in=LANGUAGE_TO_COURSE.values()
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0023_remove_course_url_video_course_rutube_id_and_more'),
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]