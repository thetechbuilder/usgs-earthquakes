# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-03-16 23:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoevents', '0003_auto_20180316_1913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geoevent',
            name='magnitude',
            field=models.FloatField(default=None, null=True),
        ),
    ]
