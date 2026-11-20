from html.parser import HTMLParser
from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import LearningCourse, LearningModule, Lesson


class AddLinkParser(HTMLParser):
    url = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and 'addlink' in attrs.get('class', '').split():
            self.url = attrs['href']


class LessonAdminInitialModuleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            username='lesson-admin', email='admin@example.com', password='test-only',
        )
        course = LearningCourse.objects.create(title='Admin course', slug='admin-course')
        cls.module = LearningModule.objects.create(course=course, title='Selected module', slug='selected')
        cls.other = LearningModule.objects.create(course=course, title='Other module', slug='other')

    def setUp(self):
        self.client.force_login(self.user)
        self.add_url = reverse('admin:courses_lesson_add')

    def test_add_link_from_filtered_list_preselects_module(self):
        response = self.client.get(reverse('admin:courses_lesson_changelist'), {
            'course': self.module.course_id, 'module_custom': self.module.pk,
        })
        self.assertEqual(response.status_code, 200)
        parser = AddLinkParser()
        parser.feed(response.content.decode())
        self.assertIsNotNone(parser.url)
        response = self.client.get(parser.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.context['adminform'].form['module'].value()), self.module.pk)
        self.assertFalse(response.context['adminform'].form['parent'].value())

    def test_unfiltered_add_form_has_no_default_module(self):
        response = self.client.get(self.add_url)
        self.assertIsNone(response.context['adminform'].form['module'].value())

    def test_explicit_module_takes_precedence(self):
        response = self.client.get(self.add_url, {
            'module': self.other.pk,
            '_changelist_filters': urlencode({'module_custom': self.module.pk}),
        })
        self.assertEqual(int(response.context['adminform'].form['module'].value()), self.other.pk)

    def test_stale_and_invalid_filter_values_are_ignored(self):
        for value in ['missing', '-1', '999999999', '9' * 50, '9223372036854775808']:
            with self.subTest(value=value):
                response = self.client.get(self.add_url, {
                    '_changelist_filters': urlencode({'module_custom': value}),
                })
                self.assertEqual(response.status_code, 200)
                self.assertIsNone(response.context['adminform'].form['module'].value())

    def test_posted_module_overrides_initial_filter(self):
        response = self.client.post(
            self.add_url + '?' + urlencode({
                '_changelist_filters': urlencode({'module_custom': self.module.pk}),
            }),
            {'title': '', 'module': self.other.pk},
        )
        self.assertEqual(response.status_code, 200)
        form = response.context['adminform'].form
        self.assertEqual(int(form['module'].value()), self.other.pk)
        self.assertIn('title', form.errors)

    def test_filter_does_not_change_module_of_existing_lesson(self):
        lesson = Lesson.objects.create(module=self.other, title='Existing', slug='existing')
        response = self.client.get(reverse('admin:courses_lesson_change', args=[lesson.pk]), {
            '_changelist_filters': urlencode({'module_custom': self.module.pk}),
        })
        self.assertEqual(int(response.context['adminform'].form['module'].value()), self.other.pk)
