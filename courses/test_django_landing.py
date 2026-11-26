import json
import re

from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse

from Kursor.sitemaps import CourseLandingSiteMap
from .models import LearningCourse


class DjangoLandingTests(TestCase):
    def test_landing_has_own_design_prerequisites_and_paid_metadata(self):
        response = self.client.get('/learn/django/?utm_source=test')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/landing/django.html')
        self.assertContains(response, 'Django, потанцуем?')
        self.assertContains(response, '/learn/basic-python/')
        self.assertContains(response, '/learn/python-oop/')
        self.assertContains(response, 'HTML, CSS и JavaScript')
        self.assertContains(response, 'Вся теория курса')
        self.assertContains(response, 'https://stepik.org/course/114288/promo')
        self.assertContains(response, 'data-dj-lab')
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', response.content.decode(), re.S).group(1))
        self.assertEqual(schema['url'], 'http://testserver/learn/django/')
        self.assertFalse(schema['isAccessibleForFree'])
        self.assertIn('django', CourseLandingSiteMap().items())
        for asset in ['base_static/css/landing/django.css', 'base_static/js/landing/django.js']:
            self.assertIsNotNone(finders.find(asset))

    def test_stepik_match_uses_real_course_address_in_landing_home_and_menu(self):
        course = LearningCourse.objects.create(title='Материалы Django', slug='my-web-theory', stepik='https://stepik.org/course/114288/promo?utm_source=test')
        response = self.client.get('/learn/django/')
        self.assertEqual(response.context['theory_url'], course.get_absolute_url())
        self.assertTrue(response.context['theory_is_course'])
        home = self.client.get('/')
        card = next(card for card in home.context['course_cards'] if card['slug'] == 'django')
        self.assertEqual(card['theory_url'], course.get_absolute_url())
        self.assertEqual(card['theme'], 'django')
        self.assertContains(home, '/learn/django/')
        self.assertEqual(home.context['course_cards'][-1]['slug'], 'django')
        nav = next(card for card in home.context['navigation_landings'] if card['slug'] == 'django')
        self.assertEqual(nav['url'], '/learn/django/')

    def test_alias_match_and_missing_theory_fallback(self):
        LearningCourse.objects.all().delete()
        response = self.client.get('/learn/django/')
        self.assertEqual(response.context['theory_url'], reverse('courses:courses_home'))
        self.assertFalse(response.context['theory_is_course'])
        self.assertContains(response, 'Откроется библиотека')
        course = LearningCourse.objects.create(title='Django', slug='django')
        response = self.client.get('/learn/django/')
        self.assertEqual(response.context['theory_url'], course.get_absolute_url())
        self.assertTrue(response.context['theory_is_course'])
