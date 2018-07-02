from django.db import models

# Create your models here.
class Course(models.Model):
    PYTHON = 'PYT'
    PASCAL = 'PAS'
    CPLUSPLUS = 'CPP'
    LANG_CHOICES = (
        (PYTHON, 'Python'),
        (PASCAL, 'Pascal'),
        (CPLUSPLUS, 'C++'),
    )
    language = models.CharField(verbose_name="Язык",max_length=3,choices=LANG_CHOICES,default=PYTHON)
    theme = models.CharField(verbose_name="Тема",max_length=100)
    number_theme=models.IntegerField(verbose_name="Номер темы",null=True)
    article = models.TextField("Описание темы",blank=True,null=True)
    url_video=models.CharField("Url-видео",max_length=50,blank=True,null=True)
    seo_keywords = models.TextField('Keywords', blank=True, max_length=160)
    def __str__(self):
        return self.get_language_display() + " " + str(self.number_theme) + " " + self.theme

    def seo_description(self):
        return 'Язык программирования "%s". %s'%(self.get_language_display(),self.theme)

    class Meta:
        verbose_name = "Тема курса"
        ordering = ["language","number_theme"]
        verbose_name_plural = "Темы курса"
        unique_together = ("number_theme","language")