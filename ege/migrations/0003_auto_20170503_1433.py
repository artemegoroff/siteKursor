# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-03 11:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ege', '0002_auto_20170503_1432'),
    ]

    operations = [
        migrations.CreateModel(
            name='VarEge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_var', models.IntegerField(unique=True, verbose_name='Номер варианта')),
                ('description', models.TextField(verbose_name='Описание')),
            ],
            options={
                'verbose_name': 'Вариант ЕГЭ',
                'verbose_name_plural': 'Варианты ЕГЭ',
            },
        ),
        migrations.AddField(
            model_name='questionsege',
            name='number_of_variant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ege.VarEge', verbose_name='Номер варианта'),
        ),
    ]
