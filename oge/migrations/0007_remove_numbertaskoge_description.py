# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-10-11 18:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oge', '0006_auto_20171011_2053'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='numbertaskoge',
            name='description',
        ),
    ]
