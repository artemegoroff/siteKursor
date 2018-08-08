# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-08-07 15:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0006_auto_20180804_0301'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='programmtask',
            options={'ordering': ['difficult'], 'verbose_name': 'Задача Практика', 'verbose_name_plural': 'Задачи для практики'},
        ),
        migrations.AlterField(
            model_name='course',
            name='tasks',
            field=models.ManyToManyField(blank=True, to='videos.ProgrammTask', verbose_name='Задачи'),
        ),
    ]
