# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-08-02 21:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ege', '0017_videorazborege_treoryknowledge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videorazborege',
            name='treoryKnowledge',
            field=models.ManyToManyField(blank=True, to='theory.TheoryVideo', verbose_name='Теория'),
        ),
    ]
