from django.db import models

# Create your models here.

class InputOutputData(models.Model):
    input = models.TextField(verbose_name='Входные данные')
    output = models.TextField(verbose_name='Выходные данные')

    def __str__(self):
        return 'in %s out %s'%(self.input.splitlines(),self.output.splitlines())

    def get_rowsInput(self):
        return self.input.splitlines()

    def get_rowsOutput(self):
        return self.output.splitlines()


class ProgrammTask(models.Model):
    name = models.CharField(verbose_name="Название", max_length=50)
    url_ref = models.URLField('Ссылка', blank=True)
    condition = models.TextField(verbose_name="Условие задачи", blank=True)
    difficult = models.IntegerField(verbose_name='Сложность')
    examples = models.ManyToManyField(InputOutputData,blank=True,verbose_name='Примеры')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Задача Практика"
        ordering = ['difficult']
        verbose_name_plural = "Задачи для практики"

class Course(models.Model):
    PYTHON = 'PYT'
    PASCAL = 'PAS'
    CPLUSPLUS = 'CPP'
    TURTLEPython = 'TUR'
    LANG_CHOICES = (
        (PYTHON, 'Python'),
        (PASCAL, 'Pascal'),
        (CPLUSPLUS, 'C++'),
        (TURTLEPython, 'Turtle')
    )
    language = models.CharField(verbose_name="Язык",max_length=3,choices=LANG_CHOICES,default=PYTHON)
    theme = models.CharField(verbose_name="Тема",max_length=100)
    number_theme=models.IntegerField(verbose_name="Номер темы",null=True)
    article = models.TextField("Описание темы",blank=True,null=True)
    url_video =models.CharField("Url-видео",max_length=50,blank=True,null=True)
    seo_keywords = models.TextField('Keywords', blank=True, max_length=160)
    tasks = models.ManyToManyField(ProgrammTask,verbose_name='Задачи',blank=True)

    def __str__(self):
        return self.get_language_display() + " " + str(self.number_theme) + " " + self.theme

    def seo_description(self):
        return 'Язык программирования "%s". %s'%(self.get_language_display(),self.theme)

    class Meta:
        verbose_name = "Тема курса"
        ordering = ["language","number_theme"]
        verbose_name_plural = "Темы курса"
        unique_together = ("number_theme","language")