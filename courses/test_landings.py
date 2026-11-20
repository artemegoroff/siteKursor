import json
import re

from django.contrib.staticfiles import finders
from django.test import TestCase, RequestFactory
from django.http import Http404
from courses.landing_views import detail
from courses.models import LearningCourse
from django.urls import reverse

from Kursor.sitemaps import CourseLandingSiteMap


class LandingTests(TestCase):
    def test_landing_and_canonical_metadata(self):
        response = self.client.get('/learn/basic-python/?utm_source=test')
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))
        self.assertEqual(schema['@type'], 'Course')
        self.assertTrue(schema['isAccessibleForFree'])
        self.assertEqual(schema['url'], 'http://testserver/learn/basic-python/')
        self.assertContains(response, 'https://stepik.org/course/63085/promo')
        self.assertContains(response, 'data-demo-form')

    def test_unknown_course(self):
        with self.assertRaises(Http404):
            detail(RequestFactory().get('/learn/missing/'), 'missing')

    def test_sitemap_and_assets(self):
        sitemap = CourseLandingSiteMap()
        self.assertCountEqual(sitemap.items(), ['basic-python', 'functional-python'])
        self.assertEqual(sitemap.location('basic-python'), reverse('course_landings:detail', kwargs={'course_slug': 'basic-python'}))
        for asset in ['base_static/css/landing/python.css', 'base_static/js/landing/python.js']:
            self.assertIsNotNone(finders.find(asset))

    def test_old_address_redirects_and_preserves_campaign(self):
        response = self.client.get('/learn/python/?utm_source=old')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], '/learn/basic-python/?utm_source=old')

    def test_author_portrait_is_available(self):
        self.assertIsNotNone(finders.find('base_static/img/landing/artem-egorov.webp'))
        response = self.client.get('/learn/basic-python/')
        self.assertContains(response, 'Артём Егоров')
        self.assertContains(response, 'Инди-курс<br>')
        self.assertContains(response, 'Профессиональный разработчик')

    def test_functional_course_uses_own_design_and_paid_metadata(self):
        response = self.client.get('/learn/functional-python/?utm_source=test')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/landing/functional_python.html')
        self.assertTemplateNotUsed(response, 'courses/landing/python.html')
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', response.content.decode(), re.S).group(1))
        self.assertFalse(schema['isAccessibleForFree'])
        self.assertEqual(schema['educationalLevel'], 'Intermediate')
        self.assertEqual(schema['url'], 'http://testserver/learn/functional-python/')
        self.assertContains(response, 'https://stepik.org/course/195619/promo')
        self.assertContains(response, 'data-fp-lab')
        self.assertContains(response, 'class="module"', count=9)
        for asset in ['base_static/css/landing/functional-python.css', 'base_static/js/landing/functional-python.js']:
            self.assertIsNotNone(finders.find(asset))

    def test_both_landings_explain_complete_theory_and_link_to_existing_courses(self):
        for landing_slug, title, stepik_id in [
            ('basic-python', 'Теория Python', '63085'),
            ('functional-python', 'Теория функций', '195619'),
        ]:
            with self.subTest(course=landing_slug):
                course = LearningCourse.objects.create(
                    title=title, slug='theory-' + landing_slug,
                    stepik='https://stepik.org/course/' + stepik_id + '/promo?test=1',
                )
                response = self.client.get('/learn/' + landing_slug + '/')
                self.assertEqual(response.context['theory_url'], course.get_absolute_url())
                self.assertTrue(response.context['theory_is_course'])
                self.assertContains(response, 'Читать теорию')
                self.assertContains(response, 'Пройти курс на Stepik')
                self.assertContains(response, '«Уроки»')
                self.assertContains(response, 'data-theory-link')
                self.assertEqual(self.client.get(course.get_absolute_url()).status_code, 200)

    def test_theory_destination_handles_existing_slug_and_missing_course(self):
        course, _ = LearningCourse.objects.get_or_create(title='Python', slug='python')
        response = self.client.get('/learn/basic-python/')
        self.assertEqual(response.context['theory_url'], course.get_absolute_url())
        response = self.client.get('/learn/functional-python/')
        self.assertEqual(response.context['theory_url'], reverse('courses:courses_home'))
        self.assertFalse(response.context['theory_is_course'])
        self.assertContains(response, 'В разделе «Уроки» выбери функциональное программирование.')

    def test_stepik_id_match_is_exact_and_precedes_alias(self):
        LearningCourse.objects.get_or_create(title='Python', slug='python')
        correct = LearningCourse.objects.create(
            title='Теория основ', slug='custom-python', stepik='https://stepik.org/course/63085',
        )
        LearningCourse.objects.create(
            title='Другой курс', slug='unrelated', stepik='https://stepik.org/course/1956190/promo',
        )
        response = self.client.get('/learn/basic-python/')
        self.assertEqual(response.context['theory_url'], correct.get_absolute_url())
        response = self.client.get('/learn/functional-python/')
        self.assertFalse(response.context['theory_is_course'])
