import json
import re

from django.http import Http404
from django.shortcuts import render
from django.urls import reverse

from .landing_data import LANDING_COURSES
from .models import LearningCourse


def theory_destination(course):
    """Resolve an existing course, never invent a URL from its marketing slug."""
    candidates = list(LearningCourse.objects.only('slug', 'title', 'stepik').order_by('pk'))
    candidates = [candidate for candidate in candidates if candidate.slug]
    for candidate in candidates:
        match = re.search(r'/course/(\d+)(?:[/?#]|$)', candidate.stepik or '')
        if match and match.group(1) == course['stepik_id']:
            return candidate.get_absolute_url(), True
    titles = {title.casefold() for title in course['theory_titles']}
    for candidate in candidates:
        if candidate.slug in course['theory_slugs'] or candidate.title.strip().casefold() in titles:
            return candidate.get_absolute_url(), True
    return reverse('courses:courses_home'), False


def detail(request, course_slug):
    course = LANDING_COURSES.get(course_slug)
    if course is None:
        raise Http404('Лендинг курса не найден')
    canonical_url = request.build_absolute_uri(reverse(
        'course_landings:detail', kwargs={'course_slug': course_slug},
    ))
    schema = {
        '@context': 'https://schema.org', '@type': 'Course',
        'name': course['name'], 'description': course['subtitle'],
        'url': canonical_url, 'inLanguage': 'ru',
        'educationalLevel': course['level'],
        'isAccessibleForFree': course['is_free'],
        'provider': {
            '@type': 'Organization', 'name': course['channel_name'],
            'url': request.build_absolute_uri(reverse('home:main_page')),
        },
    }
    theory_url, theory_is_course = theory_destination(course)
    return render(request, course['template'], {
        'theory_url': theory_url, 'theory_is_course': theory_is_course,
        'course': course, 'canonical_url': canonical_url,
        'course_schema_json': json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c'),
    })
