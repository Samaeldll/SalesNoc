# Generated by Django 3.2.8 on 2022-08-20 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0005_contract_tsv'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='address',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Адрес'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='city',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Город'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='name',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Фио'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Телефон'),
        ),
    ]
