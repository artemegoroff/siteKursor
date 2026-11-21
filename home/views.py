import html
import re

from django.core.paginator import Paginator
from django.db.models import Prefetch, Q
from django.shortcuts import render
from django.urls import reverse
from django.utils.html import strip_tags

from courses.catalogue import course_catalogue, landing_cards
from courses.models import Lesson, LessonBlock


TOPICS = ['Списки', 'Словари', 'Функции', 'zip', 'Декораторы', 'Генераторы', 'Рекурсия', 'ООП']


def get_home_page(request):
    catalogue = course_catalogue(request)
    courses = [course for course in catalogue if course.lessons_count]
    cards = landing_cards(catalogue)
    featured_ids = {card['course'].pk for card in cards if card['course']}
    context = {
        'learning_courses': courses,
        'course_cards': cards,
        'additional_courses': [course for course in courses if course.pk not in featured_ids],
        'lesson_count': sum(course.lessons_count for course in courses),
        'topics': TOPICS,
        'canonical_url': request.build_absolute_uri(reverse('home:main_page')),
    }
    return render(request, 'home/home_page.html', context)


def search(request):
    query = ' '.join(request.GET.get('q', '').split())[:120]
    results = Lesson.objects.none()
    if len(query) >= 2:
        results = (Lesson.objects.select_related('module__course')
            .exclude(slug__isnull=True).exclude(slug='')
            .exclude(module__slug__isnull=True).exclude(module__slug='')
            .exclude(module__course__slug__isnull=True).exclude(module__course__slug=''))
        for term in query.split()[:8]:
            results = results.filter(
                Q(title__icontains=term) | Q(module__title__icontains=term)
                | Q(module__course__title__icontains=term) | Q(blocks__title__icontains=term)
                | Q(blocks__kind=LessonBlock.Kind.TEXT, blocks__content__icontains=term)
            )
        results = results.distinct().order_by('module__course__sort_order', 'module__sort_order', 'sort_order', 'pk')
        results = results.prefetch_related(Prefetch(
            'blocks', queryset=LessonBlock.objects.filter(kind=LessonBlock.Kind.TEXT).only('lesson_id', 'content').order_by('sort_order', 'pk'),
            to_attr='search_blocks',
        ))
    page = Paginator(results, 12).get_page(request.GET.get('page'))
    for lesson in page.object_list:
        text = ' '.join(html.unescape(strip_tags(' '.join(block.content for block in lesson.search_blocks))).split())
        position = next((match.start() for match in re.finditer(re.escape(query.split()[0]), text, flags=re.I)), 0)
        start = max(0, position - 60)
        lesson.search_excerpt = ('…' if start else '') + text[start:start + 230] + ('…' if len(text) > start + 230 else '')
    return render(request, 'home/search.html', {'query': query, 'page_obj': page, 'topics': TOPICS})


def e_handler404(request, exception):
    return render(request, 'error404.html', status=404)


def e_handler500(request):
    # The error page must also work when the database itself is unavailable.
    request._learning_catalogue = []
    return render(request, 'error500.html', status=500)
