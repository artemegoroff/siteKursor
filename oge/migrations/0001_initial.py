# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-28 13:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryOge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=60, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Категория вопросов ОГЭ',
                'verbose_name_plural': 'Категории вопросов ОГЭ',
                'ordering': ['number_task'],
            },
        ),
        migrations.CreateModel(
            name='NumberTaskOge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(verbose_name='Номер задания')),
                ('title', models.CharField(max_length=150, verbose_name='Название')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('picture', models.ImageField(blank=True, default='', upload_to='oge/photo')),
                ('type_of_answer', models.CharField(choices=[('Radio', 'RadioButton'), ('Input', 'Input')], default='Input', max_length=5)),
            ],
            options={
                'verbose_name': 'Номер задания ОГЭ',
                'verbose_name_plural': 'Номера заданий ОГЭ',
                'ordering': ['number'],
            },
        ),
        migrations.CreateModel(
            name='QuestionsOge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Вопрос')),
                ('picture', models.ImageField(blank=True, default='', upload_to='oge/photo')),
                ('table_data', models.TextField(blank=True, null=True, verbose_name='Табличные данные')),
                ('code_python', models.TextField(blank=True, null=True, verbose_name='Python')),
                ('code_pascal', models.TextField(blank=True, null=True, verbose_name='Paskal')),
                ('code_c_plus', models.TextField(blank=True, null=True, verbose_name='C++')),
                ('var_of_choice_answer', models.TextField(blank=True, null=True, verbose_name='Варианты ответа')),
                ('answer', models.CharField(max_length=30, verbose_name='Ответ')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='oge.CategoryOge', verbose_name='Категория вопроса')),
                ('number_of_task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='oge.NumberTaskOge', verbose_name='Номер задания')),
            ],
            options={
                'verbose_name': 'Вопрос ОГЭ',
                'verbose_name_plural': 'Вопросы ОГЭ',
            },
        ),
        migrations.CreateModel(
            name='VariantOge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_var', models.IntegerField(verbose_name='Номер задания')),
                ('description', models.TextField(verbose_name='Описание')),
            ],
            options={
                'verbose_name': 'Вариант ОГЭ',
                'verbose_name_plural': 'Варианты ОГЭ',
            },
        ),
        migrations.AddField(
            model_name='questionsoge',
            name='number_of_variant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='oge.VariantOge', verbose_name='Номер варианта'),
        ),
        migrations.AddField(
            model_name='categoryoge',
            name='number_task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='oge.NumberTaskOge', verbose_name='Номер задания'),
        ),
    ]
