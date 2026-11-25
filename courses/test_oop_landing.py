import json
import re

from django.contrib.staticfiles import finders
from django.test import TestCase

from .models import LearningCourse


class OopLandingTests(TestCase):
    def test_landing_explains_prerequisites_and_has_own_design(self):
        response = self.client.get('/learn/python-oop/?utm_source=test')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/landing/python_oop.html')
        for text in ('/learn/basic-python/', '/learn/functional-python/',
                     '/learn/python-modules-files/', 'Желательно, но не обязательно',
                     'Вся теория', 'https://stepik.org/course/114354/promo'):
            self.assertContains(response, text)
        self.assertContains(response, 'class="oo-module"', count=10)
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', response.content.decode(), re.S).group(1))
        self.assertEqual(schema['url'], 'http://testserver/learn/python-oop/')
        self.assertFalse(schema['isAccessibleForFree'])
        self.assertEqual(schema['educationalLevel'], 'Intermediate')
        for asset in ('base_static/css/landing/python-oop.css', 'base_static/js/landing/python-oop.js'):
            self.assertIsNotNone(finders.find(asset))

    def test_explicit_course_binding_survives_a_renamed_course(self):
        course, _ = LearningCourse.objects.update_or_create(
            pk=6, defaults={'title': 'Мой курс объектов', 'slug': 'custom-object-theory', 'stepik': ''},
        )
        LearningCourse.objects.create(title='Другой курс', slug='another-oop', stepik='https://stepik.org/course/114354/promo')
        response = self.client.get('/learn/python-oop/')
        self.assertEqual(response.context['theory_url'], course.get_absolute_url())
        self.assertTrue(response.context['theory_is_course'])
        home = self.client.get('/')
        card = next(item for item in home.context['course_cards'] if item['slug'] == 'python-oop')
        self.assertEqual(card['theme'], 'oop')
        self.assertEqual(card['theory_url'], course.get_absolute_url())
        self.assertContains(home, '/learn/python-oop/')
        nav = next(item for item in home.context['navigation_landings'] if item['slug'] == 'python-oop')
        self.assertEqual(nav['url'], '/learn/python-oop/')

    def test_theory_fallback_with_no_linked_course(self):
        LearningCourse.objects.all().delete()
        response = self.client.get('/learn/python-oop/')
        self.assertFalse(response.context['theory_is_course'])
        self.assertContains(response, 'Откроется библиотека курсов')
