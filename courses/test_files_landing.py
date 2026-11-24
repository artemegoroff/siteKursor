import json
import re

from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse

from .models import LearningCourse


class ModulesFilesLandingTests(TestCase):
    def test_independent_landing_has_prerequisites_programme_and_paid_metadata(self):
        response = self.client.get('/learn/python-modules-files/?utm_source=test')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/landing/python_modules_files.html')
        self.assertContains(response, '/learn/basic-python/')
        self.assertContains(response, '/learn/functional-python/')
        self.assertContains(response, 'Нужны знания двух предыдущих курсов.')
        self.assertContains(response, 'class="fm-topic"', count=8)
        self.assertContains(response, 'Вся теория')
        self.assertContains(response, 'https://stepik.org/course/230401/promo')
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', response.content.decode(), re.S).group(1))
        self.assertFalse(schema['isAccessibleForFree'])
        self.assertEqual(schema['url'], 'http://testserver/learn/python-modules-files/')
        for asset in ['base_static/css/landing/python-modules-files.css', 'base_static/js/landing/python-modules-files.js']:
            self.assertIsNotNone(finders.find(asset))

    def test_custom_course_slug_links_correctly_in_landing_home_and_menu(self):
        course = LearningCourse.objects.create(
            title='Материалы про файлы', slug='custom-files-theory',
            stepik='https://stepik.org/course/230401/promo?utm_source=test',
        )
        response = self.client.get('/learn/python-modules-files/')
        self.assertEqual(response.context['theory_url'], course.get_absolute_url())
        self.assertTrue(response.context['theory_is_course'])
        home = self.client.get('/')
        self.assertContains(home, '/learn/python-modules-files/')
        self.assertContains(home, course.get_absolute_url())
        card = next(card for card in home.context['course_cards'] if card['slug'] == 'python-modules-files')
        self.assertEqual(card['level'], 'После двух курсов')
        self.assertEqual(card['theme'], 'files')
        self.assertEqual(card['theory_url'], course.get_absolute_url())
        nav = next(card for card in home.context['navigation_landings'] if card['slug'] == 'python-modules-files')
        self.assertEqual(nav['url'], reverse('course_landings:detail', kwargs={'course_slug': 'python-modules-files'}))

    def test_missing_theory_course_uses_catalogue_instead_of_a_broken_url(self):
        response = self.client.get('/learn/python-modules-files/')
        self.assertEqual(response.context['theory_url'], reverse('courses:courses_home'))
        self.assertFalse(response.context['theory_is_course'])
        self.assertContains(response, 'Откроется библиотека')
