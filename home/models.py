from django.db import models


class Review(models.Model):
    client = models.CharField("Клиент",max_length=70)
    text = models.TextField("Отзыв",max_length=500)
    date = models.DateField("Дата отзыва",auto_now=False,auto_now_add=False)
    mark = models.IntegerField("Оценка",default=5)
    picture = models.ImageField(upload_to='home/reviews', blank=True, default='')

    def __str__(self):
        return self.client + '  ' + self.text[:20]

    def get_review(self):
            # return self.text[:190]+'...'
            return self.text
    class Meta:
        verbose_name = "Отзыв клиента"
        verbose_name_plural = "Отзывы клиентов"
        ordering = ["date"]