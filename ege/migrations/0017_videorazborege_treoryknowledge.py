# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-08-02 21:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theory', '0002_auto_20180803_0018'),
        ('ege', '0016_remove_videorazborege_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='videorazborege',
            name='treoryKnowledge',
            field=models.ManyToManyField(to='theory.TheoryVideo', verbose_name='Теория'),
        ),
    ]