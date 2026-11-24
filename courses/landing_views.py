import json

from django.http import Http404
from django.shortcuts import render
from django.urls import reverse

from .landing_data import LANDING_COURSES
from .catalogue import course_catalogue, landing_cards


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
    card = next(card for card in landing_cards(course_catalogue(request)) if card['slug'] == course_slug)
    return render(request, course['template'], {
        'theory_url': card['theory_url'], 'theory_is_course': card['theory_available'],
        'course': course, 'canonical_url': canonical_url,
        'course_schema_json': json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c'),
    })
