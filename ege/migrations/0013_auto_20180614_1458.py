# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-06-14 11:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ege', '0012_auto_20180524_0021'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoRazborEGE',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_video', models.CharField(blank=True, max_length=50, null=True, verbose_name='Url-видео')),
                ('description', models.CharField(max_length=150, verbose_name='Описание')),
                ('data_add', models.DateField(auto_now_add=True, verbose_name='Дата добавления')),
            ],
        ),
        migrations.AlterField(
            model_name='numbertaskege',
            name='seo_description',
            field=models.TextField(blank=True, max_length=160, verbose_name='SEO Description'),
        ),
        migrations.AlterField(
            model_name='numbertaskege',
            name='seo_keywords',
            field=models.TextField(blank=True, max_length=160, verbose_name='SEO Keywords'),
        ),
        migrations.AlterField(
            model_name='numbertaskege',
            name='type_of_answer',
            field=models.CharField(choices=[('ManyT', 'ManyText'), ('Input', 'Input'), ('NoInp', 'NoInput')], default='Input', max_length=5),
        ),
        migrations.AddField(
            model_name='videorazborege',
            name='number_of_task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ege.NumberTaskEge', verbose_name='Номер задания'),
        ),
    ]
