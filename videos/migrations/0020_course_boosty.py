# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2020-07-29 15:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0019_course_patreon'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='boosty',
            field=models.URLField(blank=True, default='', verbose_name='Boosty'),
        ),
    ]
