from django.db import models


class CategoryTheory(models.Model):
    name = models.CharField(verbose_name="Название", max_length=60)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Категории теории"
        verbose_name = "Категория вопросов ЕГЭ"

class TheoryVideo(models.Model):
    name = models.CharField("Название",max_length=100)
    category = models.ForeignKey(CategoryTheory, verbose_name="Категория видео")
    url_video = models.CharField("Url-видео", max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Теория"
        verbose_name_plural = "Теория по экзаменам"
