from html.parser import HTMLParser
from urllib.parse import urlsplit

from django.db import connection
from django.test import TestCase, RequestFactory
from django.test.utils import CaptureQueriesContext
from django.urls import resolve, reverse

from courses.models import LearningCourse, LearningModule, Lesson, LessonBlock


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []

    def handle_starttag(self, tag, attrs):
        href = dict(attrs).get('href', '')
        if tag == 'a' and href.startswith('/'):
            self.paths.append(urlsplit(href).path)


class HomeAndSearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.course = LearningCourse.objects.create(title='Теория функций', slug='actual-functions', stepik='https://stepik.org/course/195619/promo')
        cls.module = LearningModule.objects.create(course=cls.course, title='Итераторы', slug='iterators')
        cls.lesson = Lesson.objects.create(module=cls.module, title='Использование zip', slug='zip')
        cls.child = Lesson.objects.create(module=cls.module, parent=cls.lesson, title='Распаковка', slug='unpacking')
        LessonBlock.objects.create(lesson=cls.lesson, kind='text', content='<p>Объединяем последовательности в кортежи.</p>')
        LessonBlock.objects.create(lesson=cls.lesson, kind='text', content='<p>zip соединяет последовательности.</p>')
        LessonBlock.objects.create(lesson=cls.child, kind='text', title='Работа с парами', content='<p>Распаковка кортежей.</p>')

    def test_home_uses_current_courses_and_actual_theory_links(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.get_absolute_url())
        self.assertContains(response, '/learn/basic-python/')
        self.assertContains(response, '/learn/functional-python/')
        self.assertContains(response, 'Вся теория')
        self.assertNotContains(response, '/old_course/')
        self.assertNotContains(response, 'Автоматически создано миграцией')
        current = next(course for course in response.context['learning_courses'] if course.pk == self.course.pk)
        self.assertEqual(current.lessons_count, 2)
        card = next(card for card in response.context['course_cards'] if card['slug'] == 'functional-python')
        self.assertEqual(card['theory_url'], self.course.get_absolute_url())
        links = Links()
        links.feed(response.content.decode())
        for path in links.paths:
            resolve(path)

    def test_titles_blocks_and_hierarchy_are_searchable_without_duplicates(self):
        for query, expected in [('zip', self.lesson), ('последовательности', self.lesson), ('Работа с парами', self.child)]:
            with self.subTest(query=query):
                response = self.client.get(reverse('home:search'), {'q': query})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(list(response.context['page_obj'].object_list), [expected])
                self.assertContains(response, expected.get_absolute_url())
                self.assertContains(response, self.course.title)
                self.assertContains(response, self.module.title)
                self.assertContains(response, 'noindex,follow')

    def test_empty_search_missing_results_and_html_input(self):
        for query in ['', 'z', 'nothing-unfindable', '<script>alert(1)</script>']:
            response = self.client.get(reverse('home:search'), {'q': query, 'page': 'wrong'})
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertContains(self.client.get(reverse('home:search'), {'q': 'nothing-unfindable'}), 'Пока ничего не нашли.')

    def test_search_pagination_keeps_query_and_excludes_missing_slugs(self):
        for number in range(15):
            Lesson.objects.create(module=self.module, title=f'Pageable {number}', slug=f'page-{number}')
        Lesson.objects.filter(pk=self.child.pk).update(slug=None)
        response = self.client.get(reverse('home:search'), {'q': 'Pageable', 'page': 2})
        self.assertEqual(len(response.context['page_obj'].object_list), 3)
        self.assertContains(response, 'q=Pageable')
        self.assertNotContains(self.client.get(reverse('home:search'), {'q': 'Распаковка'}), '/None/')

    def test_query_count_is_independent_of_number_of_courses(self):
        with CaptureQueriesContext(connection) as queries:
            self.client.get('/')
        first = len(queries)
        for number in range(6):
            LearningCourse.objects.create(title=f'New {number}', slug=f'new-{number}')
        with CaptureQueriesContext(connection) as queries:
            self.client.get('/')
        self.assertEqual(first, len(queries))
        self.assertLessEqual(first, 3)

    def test_server_error_page_does_not_query_the_database(self):
        from .views import e_handler500
        with self.assertNumQueries(0):
            response = e_handler500(RequestFactory().get('/'))
        self.assertEqual(response.status_code, 500)
