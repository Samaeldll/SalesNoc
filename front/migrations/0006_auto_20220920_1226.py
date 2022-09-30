# Generated by Django 3.2.8 on 2022-09-20 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0005_alter_contract_tsv'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='call_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='contract',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'Отсутствует'), (1, 'В работе'), (2, 'Нет ответа'), (3, 'Подумает'), (4, 'Неверная'), (5, 'Выполнено'), (6, 'Ожидание Обработки'), (7, 'Ожидание Клиента'), (8, 'Отложено Компанией'), (9, 'Ошибочно Оформленна'), (10, 'Адрес вне зоны покрытия'), (11, 'Заявка Оформленна')], default=0, verbose_name='Статус'),
        ),
    ]