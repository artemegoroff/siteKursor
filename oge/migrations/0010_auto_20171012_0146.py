# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-10-11 22:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oge', '0009_auto_20171012_0038'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='variantoge',
            name='description',
        ),
        migrations.RemoveField(
            model_name='variantoge',
            name='seo_description',
        ),
        migrations.RemoveField(
            model_name='variantoge',
            name='seo_keywords',
        ),
        migrations.RemoveField(
            model_name='variantoge',
            name='seo_title',
        ),
    ]
