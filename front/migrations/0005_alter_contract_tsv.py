# Generated by Django 3.2.8 on 2022-09-17 10:00

import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0004_frontuser_workmail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='tsv',
            field=django.contrib.postgres.search.SearchVectorField(blank=True, null=True),
        ),
    ]