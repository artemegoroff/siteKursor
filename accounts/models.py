from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from ege.models import QuestionsEGE
from oge.models import QuestionsOge
from hashlib import md5

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    done_ege_tasks = models.ManyToManyField(QuestionsEGE, verbose_name='ЕГЭ сделанные',blank=True, related_name='ege_done')
    fail_ege_tasks = models.ManyToManyField(QuestionsEGE, verbose_name='ЕГЭ провалено',blank=True, related_name='ege_fail')
    done_oge_tasks = models.ManyToManyField(QuestionsOge, verbose_name='ОГЭ сделанные', blank=True, related_name='oge_done')
    fail_oge_tasks = models.ManyToManyField(QuestionsOge, verbose_name='ОГЭ провалено', blank=True, related_name='oge_fail')

    def __str__(self):
        return self.user.username

    def avatar(self):
        digest = md5(self.user.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, 150)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
