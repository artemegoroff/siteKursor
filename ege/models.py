from django.db import models
from theory.models import TheoryVideo
from django.contrib.auth.models import User

class VarEge(models.Model):
    number_var = models.IntegerField(verbose_name="Номер варианта", unique=True)

    def __str__(self):
        return str(self.number_var) + " Вариант ЕГЭ"

    def seo_title(self):
        return 'Тренировачный вариант ' + str(self.number_var) + ' ЕГЭ по информатике'

    def seo_description(self):
        return "Испытайте Ваши знания! Решите пробный вариант № " + str(self.number_var) + """ по ЕГЭ Информатика
    В данном варианте собраны все актуальные задачи, аналогичные тем, что присутствуют в демо варианте ФИПИ или были
    на последнем реальном экзамене"""

    def seo_keywords(self):
        return "ЕГЭ Информатика, Информатика 2018, Варианты информатика, тесты ЕГЭ информатика, Тесты онлайн Информатика"

    class Meta:
        verbose_name = "Вариант ЕГЭ"
        verbose_name_plural = "Варианты ЕГЭ"


class NumberTaskEge(models.Model):
    number = models.IntegerField(verbose_name="Номер задания", primary_key=True)
    title = models.CharField("Название", max_length=150)
    picture = models.ImageField(upload_to='ege/photo', blank=True, default='')
    types = (
        ('ManyT', 'ManyText'),
        ('Input', 'Input'),
        ('NoInp', 'NoInput'),
    )
    type_of_answer = models.CharField(
        max_length=5,
        choices=types,
        default='Input',
    )
    seo_description = models.TextField('SEO Description', blank=True, max_length=160)
    seo_keywords = models.TextField('SEO Keywords', blank=True, max_length=160)

    def __str__(self):
        return str(self.number) + '. ' + self.title

    def seo_title(self):
        return "ЕГЭ Информатика " + "Тест задание " + str(self.number) + " " + self.title

    def count_questions(self):
        return len(QuestionsEGE.objects.filter(number_of_task=self.number))

    def count_videoRazbors(self):
        return len(VideoRazborEGE.objects.filter(number_of_task=self.number))

    class Meta:
        verbose_name = "Номер задания ЕГЭ"
        verbose_name_plural = "Номера заданий ЕГЭ"
        ordering = ["number"]


class CategoryEge(models.Model):
    number_task = models.ForeignKey(NumberTaskEge, verbose_name="Номер задания")
    text = models.CharField(verbose_name="Название", max_length=60)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name_plural = "Категории вопросов ЕГЭ"
        verbose_name = "Категория вопросов ЕГЭ"
        ordering = ["number_task"]


class VideoRazborEGE(models.Model):
    url_video = models.CharField("Url-видео", max_length=50, blank=True, null=True)
    number_of_task = models.ForeignKey(NumberTaskEge, verbose_name="Номер задания")
    data_add = models.DateField(verbose_name="Дата добавления", auto_now_add=True)
    seo_description = models.TextField('SEO Description', blank=True, max_length=160)
    seo_keywords = models.TextField('SEO Keywords', blank=True, max_length=160)
    treoryKnowledge = models.ManyToManyField(TheoryVideo, verbose_name="Теория", blank=True)

    def __str__(self):
        return str(self.id) + ' ' + self.url_video

    def TITLE(self):
        return "Видеоразборы задач ЕГЭ по информатике"

    def SEO_DESCRIP_ALL(self):
        return "Видеоразборы актуальных задач из ЕГЭ по информатике. Видеоуроки по подготовке к ЕГЭ по информатике"

    def SEO_KEYWORDS_ALL(self):
        return 'информатика,ЕГЭ информатика,решение егэ информатика,видеоразборы информатика егэ,видеоуроки информатика егэ,егэ фипи решение,поляков решение задач,егэ по информатике,ЕГЭ информатика и ИКТ,как решать егэ информатика,информатика как решать егэ'

    def get_category_of_question(self):
        return QuestionsEGE.objects.get(q_url_video=self).category

    class Meta:
        verbose_name = "Разбор задач ЕГЭ"
        verbose_name_plural = "Разборы ЕГЭ"


class QuestionsEGE(models.Model):
    text = models.TextField("Вопрос")
    number_of_task = models.ForeignKey(NumberTaskEge, verbose_name="Номер задания")
    category = models.ForeignKey(CategoryEge, verbose_name="Категория вопроса", blank=True, null=True)
    number_of_variant = models.ForeignKey(VarEge, verbose_name="Номер варианта", blank=True, null=True)
    picture = models.ImageField(upload_to='ege/photo', blank=True, default='')
    table_data = models.TextField("Табличные данные", blank=True, null=True)
    code_python = models.TextField("Python", blank=True, null=True)
    code_pascal = models.TextField("Paskal", blank=True, null=True)
    code_c_plus = models.TextField("C++", blank=True, null=True)
    q_url_video = models.OneToOneField(VideoRazborEGE, verbose_name="Url-видео", on_delete=models.CASCADE, blank=True,
                                       null=True)
    failed = models.IntegerField("Неверные попытки",default=0)
    passed = models.IntegerField("Правильные попытки", default=0)
    answer = models.CharField(verbose_name="Ответ", max_length=30)

    def __str__(self):
        return "%s %s" % (self.number_of_task, self.text)

    def get_part_question_1(self):
        return self.text.split('---')[0].split('===')

    def get_part_question_2(self):
        if len(self.text.split('---')) > 1:
            return self.text.split('---')[1].split('===') or ''

    def get_var_answers(self):
        return self.var_of_choice_answer.split('\n')

    def table_in_row(self):
        s = self.table_data.split('#####')
        for i in range(len(s)):
            s[i] = s[i].replace('\r', '')
        for i in range(len(s)):
            s[i] = s[i].strip()
        for i in range(len(s)):
            s[i] = s[i].split('\n')
        for i in range(len(s)):
            for j in range(len(s[i])):
                s[i][j] = s[i][j].split('\t')
        return s

    def table_style(self):
        if len(self.table_in_row()) > 1:
            return 'twoTable'
        elif self.number_of_task_id == 2:
            return 'oneTable oneTableLastChild'
        elif self.number_of_task_id == 4:
            return 'oneTable oneTableWithout'
        elif self.number_of_task_id in [17, 19]:
            return 'oneTable oneTableHeader'
        elif len(self.table_in_row()) == 1:
            return 'oneTable oneTableFirstChild'
        return ''

    def table_setka(self):
        if len(self.table_in_row()) > 1:
            return 'col-md-6 col-lg-6'
        elif len(self.table_in_row()) == 1 and self.picture:
            return 'col-12 col-sm-8 col-md-8 col-lg-7'
        elif len(self.table_in_row()) == 1:
            return 'col-md-10 col-lg-8'
        return ''

    class Meta:
        verbose_name = "Вопрос ЕГЭ"
        verbose_name_plural = "Вопросы ЕГЭ"


class CommentEge(models.Model):
    task_ege = models.ForeignKey(QuestionsEGE,verbose_name='Задание')
    user = models.ForeignKey(User)
    reply = models.ForeignKey('self',null=True,related_name='replies')
    content = models.TextField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}-{}'.format(self.task_ege.number_of_task,self.user)
