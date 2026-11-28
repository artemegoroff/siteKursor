import json
from urllib.parse import urlencode

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse

from .models import LearningCourse, LearningModule, Lesson
from .admin_lesson_table import SESSION_KEY


class LessonTableSettingsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.first = User.objects.create_superuser('table-first', 'first@example.com', 'test-only')
        cls.second = User.objects.create_superuser('table-second', 'second@example.com', 'test-only')
        cls.reader = User.objects.create_user('table-reader', is_staff=True)
        cls.reader.user_permissions.add(Permission.objects.get(codename='view_lesson', content_type__app_label='courses'))
        course = LearningCourse.objects.create(title='Table course', slug='table-course')
        cls.module = LearningModule.objects.create(course=course, title='Module', slug='module')
        cls.other = LearningModule.objects.create(course=course, title='Other', slug='other')
        cls.a = Lesson.objects.create(module=cls.module, title='First', slug='first', sort_order=1)
        cls.b = Lesson.objects.create(module=cls.module, title='Second', slug='second', sort_order=2)

    def setUp(self):
        self.client.force_login(self.first)
        self.list_url = reverse('admin:courses_lesson_changelist')
        self.settings_url = reverse('admin:courses_lesson_table_settings')

    def configure(self, visible=None, editable=None, **extra):
        return self.client.post(self.settings_url, {
            'visible_fields': visible or ['title', 'module', 'parent', 'sort_order', 'slug', 'seo_keywords'],
            'editable_fields': editable or [], **extra,
        })

    def payload(self, slugs=('first-new', 'second-new')):
        data = {'form-TOTAL_FORMS': 2, 'form-INITIAL_FORMS': 2, 'form-MIN_NUM_FORMS': 0, 'form-MAX_NUM_FORMS': 1000, '_save': 'Сохранить'}
        for index, lesson in enumerate([self.a, self.b]):
            data.update({f'form-{index}-id': lesson.pk, f'form-{index}-title': lesson.title + ' edited', f'form-{index}-slug': slugs[index], f'form-{index}-seo_keywords': 'Python'})
        return data

    def test_default_table_and_personal_persistence_without_admin_mutation(self):
        default = self.client.get(self.list_url).context['cl']
        self.assertIn('_reorder_', default.list_display)
        self.assertFalse(default.list_editable)
        self.configure(visible=['slug', 'seo_keywords'], editable=['title', 'slug'])
        response = self.client.get(self.list_url)
        cl = response.context['cl']
        self.assertIn('title', cl.list_display)
        self.assertIn('open_lesson', cl.list_display)
        self.assertNotIn('module', cl.list_display)
        self.assertNotIn('_reorder_', cl.list_display)
        self.assertEqual(cl.list_editable, ('title', 'slug'))
        self.assertContains(response, f'/admin/courses/lesson/{self.a.pk}/change/')
        self.assertIn('title', cl.formset.forms[0].fields)
        self.assertIsNot(cl.model_admin, admin.site._registry[Lesson])
        self.assertEqual(admin.site._registry[Lesson].list_editable, ())
        other_client = Client()
        other_client.force_login(self.second)
        other = other_client.get(self.list_url).context['cl']
        self.assertIn('module', other.list_display)
        self.assertFalse(other.list_editable)
        self.client.force_login(self.first)
        self.assertEqual(self.client.get(self.list_url).context['cl'].list_editable, ('title', 'slug'))

    def test_bulk_edit_saves_allowed_fields_and_ignores_injected_relations(self):
        self.configure(editable=['title', 'slug', 'seo_keywords'])
        data = self.payload()
        data.update({'form-0-module': self.other.pk, 'form-0-parent': self.b.pk, 'form-0-sort_order': 999})
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, 302)
        self.a.refresh_from_db()
        self.assertEqual(self.a.title, 'First edited')
        self.assertEqual(self.a.slug, 'first-new')
        self.assertEqual(self.a.seo_keywords, 'Python')
        self.assertEqual(self.a.module_id, self.module.pk)
        self.assertIsNone(self.a.parent_id)
        self.assertEqual(self.a.sort_order, 1)

    def test_conflicting_slugs_do_not_save_any_row(self):
        self.configure(editable=['title', 'slug', 'seo_keywords'])
        for slugs in [('same-new', 'same-new'), ('second', 'second-new')]:
            with self.subTest(slugs=slugs):
                response = self.client.post(self.list_url, self.payload(slugs))
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context['cl'].formset.errors or response.context['cl'].formset.non_form_errors())
                self.a.refresh_from_db()
                self.assertEqual(self.a.title, 'First')
                self.assertEqual(self.a.slug, 'first')

    def test_settings_preserve_filters_and_reset_index_based_ordering(self):
        query = urlencode({'course': self.module.course_id, 'module_custom': self.module.pk, 'q': 'First', 'o': '2.1'})
        response = self.configure(visible=['title', 'slug'], return_query=query)
        self.assertEqual(response.status_code, 302)
        self.assertIn('module_custom=', response['Location'])
        self.assertIn('q=First', response['Location'])
        self.assertNotIn('o=', response['Location'])
        response = self.client.get(response['Location'])
        self.assertEqual(response.context['cl'].result_count, 1)

    def test_reset_only_affects_current_session(self):
        self.configure(editable=['slug'])
        other = Client()
        other.force_login(self.first)
        other.post(self.settings_url, {'visible_fields': ['title'], 'editable_fields': ['title']})
        self.client.post(self.settings_url, {'reset': '1'})
        self.assertNotIn(SESSION_KEY, self.client.session)
        self.assertEqual(other.session[SESSION_KEY]['editable_fields'], ['title'])
        self.assertFalse(self.client.get(self.list_url).context['cl'].list_editable)

    def test_logout_discards_session_settings(self):
        self.configure(editable=['slug'])
        self.client.logout()
        self.client.force_login(self.first)
        self.assertNotIn(SESSION_KEY, self.client.session)
        self.assertFalse(self.client.get(self.list_url).context['cl'].list_editable)

    def test_illegal_editable_fields_are_rejected_and_hidden_fields_not_editable(self):
        self.configure(editable=['slug'])
        for field in ['module', 'parent', 'sort_order', 'password']:
            self.configure(editable=[field])
            self.assertEqual(self.client.session[SESSION_KEY]['editable_fields'], ['slug'])
        self.configure(visible=['title'], editable=['slug'])
        self.assertFalse(self.client.session[SESSION_KEY]['editable_fields'])

    def test_read_only_user_cannot_enable_editing(self):
        self.client.force_login(self.reader)
        self.configure(editable=['title'])
        self.assertFalse(self.client.session[SESSION_KEY]['editable_fields'])
        cl = self.client.get(self.list_url).context['cl']
        self.assertFalse(cl.list_editable)
        self.assertNotIn('_reorder_', cl.list_display)
        self.assertEqual(self.client.post(self.list_url, self.payload()).status_code, 403)

    def test_settings_require_permission_post_and_csrf(self):
        self.assertEqual(self.client.get(self.settings_url).status_code, 405)
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.first)
        self.assertEqual(client.post(self.settings_url, {'reset': '1'}).status_code, 403)
        user = get_user_model().objects.create_user('table-no-access', is_staff=True)
        self.client.force_login(user)
        self.assertEqual(self.client.post(self.settings_url, {'reset': '1'}).status_code, 403)

    def test_sorting_handle_still_updates_order(self):
        self.configure(editable=['slug'])
        self.assertIn('_reorder_', self.client.get(self.list_url).context['cl'].list_display)
        response = self.client.post(reverse('admin:courses_lesson_sortable_update'), data=json.dumps({'updatedItems': [[self.a.pk, 2], [self.b.pk, 1]]}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.a.refresh_from_db()
        self.assertEqual(self.a.sort_order, 2)

    def test_null_slugs_are_allowed_until_changed_rows_generate_them(self):
        Lesson.objects.filter(pk__in=[self.a.pk, self.b.pk]).update(slug=None, title='Same title')
        self.configure(editable=['seo_keywords'])
        data = self.payload()
        data['form-0-seo_keywords'] = ''
        data['form-1-seo_keywords'] = ''
        self.assertEqual(self.client.post(self.list_url, data).status_code, 302)
        data['form-0-seo_keywords'] = 'Python'
        data['form-1-seo_keywords'] = 'Python'
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['cl'].formset.non_form_errors())
        self.assertEqual(Lesson.objects.filter(pk__in=[self.a.pk, self.b.pk], slug__isnull=True).count(), 2)
