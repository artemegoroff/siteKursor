"""Current course links shared by the home page and navigation."""
import re

from django.db.models import Count
from django.urls import reverse

from .landing_data import LANDING_COURSES
from .models import LearningCourse


LANDING_ALIASES = {
    'python-oop': {'oop-python', 'python-oop', 'oop python', 'ооп на python', 'объектно-ориентированное программирование на python'},
    'basic-python': {'python', 'basic-python', 'инди-курс программирования на python', 'инди-курс python с нуля'},
    'functional-python': {'functional-python', 'функциональное программирование', 'функциональное программирование на python'},
    'python-modules-files': {'python-modules-files', 'модули и файлы в python', 'сохрани меня, если сможешь: модули и файлы в python'},
}



def count_label(number, forms):
    if 11 <= number % 100 <= 14:
        word = forms[2]
    elif number % 10 == 1:
        word = forms[0]
    elif 2 <= number % 10 <= 4:
        word = forms[1]
    else:
        word = forms[2]
    return f'{number} {word}'


def course_catalogue(request):
    if not hasattr(request, '_learning_catalogue'):
        request._learning_catalogue = list(
            LearningCourse.objects.exclude(slug__isnull=True).exclude(slug='')
            .annotate(lessons_count=Count('modules__lessons', distinct=True), modules_count=Count('modules', distinct=True))
            .order_by('sort_order', 'title', 'pk')
        )
        for course in request._learning_catalogue:
            course.lesson_summary = count_label(course.lessons_count, ('урок', 'урока', 'уроков'))
            course.module_summary = count_label(course.modules_count, ('модуль', 'модуля', 'модулей'))
    return request._learning_catalogue


def landing_cards(courses):
    cards = []
    for slug, data in LANDING_COURSES.items():
        identifier = re.search(r'/course/(\d+)', data['stepik_url']).group(1)
        linked = next((course for course in courses if course.pk == data.get('learning_course_pk')), None)
        if linked is None:
            linked = next((course for course in courses if re.search(r'/course/' + identifier + r'(?:[/?#]|$)', course.stepik or '')), None)
        if linked is None:
            aliases = LANDING_ALIASES.get(slug, set())
            linked = next((course for course in courses if course.slug in aliases or course.title.strip().casefold() in aliases), None)
        cards.append({
            'slug': slug, 'name': data['name'], 'description': data['subtitle'],
            'url': reverse('course_landings:detail', kwargs={'course_slug': slug}),
            'theory_url': linked.get_absolute_url() if linked else reverse('courses:courses_home'),
            'theory_available': linked is not None,
            'level': data.get('display_level', 'С нуля' if data['level'] == 'Beginner' else 'После основ'),
            'order': data.get('catalogue_order', 10 if slug == 'basic-python' else 20),
            'theme': data.get('card_theme', 'basic' if slug == 'basic-python' else 'functional'),
            'card_description': data.get('card_description', data['subtitle']),
            'card_code': data.get('card_code', 'print("Привет, Python!")' if slug == 'basic-python' else 'def next_level():\n    yield "Python"'),
            'card_symbol': data.get('card_symbol', 'Py' if slug == 'basic-python' else 'ƒ(x)'),
            'card_tags': data.get('card_tags', ['Первые программы', 'Основы языка'] if slug == 'basic-python' else ['Декораторы', 'Генераторы']),
            'course': linked,
        })
    # Show the introductory course first regardless of registry insertion order.
    return sorted(cards, key=lambda card: card['order'])
