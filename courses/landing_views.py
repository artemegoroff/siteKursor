import json

from django.http import Http404
from django.shortcuts import render
from django.urls import reverse

from .landing_data import LANDING_COURSES


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
        'educationalLevel': 'Beginner', 'isAccessibleForFree': True,
        'provider': {
            '@type': 'Organization', 'name': course['author_name'],
            'url': request.build_absolute_uri(reverse('home:main_page')),
        },
    }
    return render(request, 'courses/landing/python.html', {
        'course': course, 'canonical_url': canonical_url,
        'course_schema_json': json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c'),
    })
