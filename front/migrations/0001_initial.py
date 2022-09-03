# Generated by Django 3.2.8 on 2022-08-24 19:12

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.contrib.postgres.search
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='FrontUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('done_count', models.IntegerField(default=0)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='CommentRow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('changes', models.TextField(blank=True)),
                ('text', models.TextField(blank=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'ordering': ['-create_date'],
            },
        ),
        migrations.CreateModel(
            name='Statistic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.IntegerField(choices=[(1, 'Не назначен пользователь после создания')], default=0)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Фио')),
                ('city', models.CharField(max_length=50, verbose_name='Город')),
                ('address', models.CharField(max_length=100, verbose_name='Адрес')),
                ('phone', models.CharField(max_length=50, verbose_name='Телефон')),
                ('request_number', models.CharField(blank=True, max_length=20, null=True)),
                ('contract_condition', models.TextField(blank=True, null=True)),
                ('tsv', django.contrib.postgres.search.SearchVectorField(null=True)),
                ('state', models.SmallIntegerField(choices=[(0, 'Необработанная'), (1, 'Ожидание'), (4, 'В обработке'), (2, 'Повторная обработка'), (3, 'Оформленна')], default=0, verbose_name='Состояние')),
                ('service_first', models.CharField(default='Интернет', max_length=50, verbose_name='Услуга')),
                ('service_two', models.CharField(default='Телевиденье', max_length=50, verbose_name='Услуга')),
                ('conditions_first', models.SmallIntegerField(choices=[(1, 'Индивидуальные'), (2, 'Акционные (0*3)'), (3, '10 дней - за 500'), (4, 'Акционные (0*0)')], default=2, verbose_name='Условия интернет')),
                ('conditions_two', models.SmallIntegerField(choices=[(1, 'Индивидуальные'), (2, 'Акционные (0*3)'), (3, '10 дней - за 500'), (4, 'Акционные (0*0)')], default=4, verbose_name='Условия телевиденье')),
                ('equipment_first', models.SmallIntegerField(choices=[(0, '841n - 555'), (1, 'ArcherC24 - 800'), (2, 'ArcherC54 - 900'), (3, 'ArcherC5 - 1399'), (4, 'ArcherAx10 - 1599'), (5, 'InextTV5 - 850'), (6, 'Не требуется')], default=6, verbose_name='Оборудование интернет')),
                ('equipment_two', models.SmallIntegerField(choices=[(0, 'Не требуется'), (1, 'InextTV5 - 850')], default=0, verbose_name='Оборудование телевиденье')),
                ('type_first', models.SmallIntegerField(choices=[(0, 'Не выбрано'), (1, 'HOME в Многокварт.'), (2, 'GPON в Многокварт.'), (3, 'GPON в Частный'), (4, 'Radio в Частный'), (5, 'Индивидуальное')], default=0, verbose_name='Тип подключения интернет')),
                ('type_two', models.SmallIntegerField(choices=[(0, 'Не выбрано'), (1, 'IPTV'), (2, 'Аналоговое Телевиденье'), (3, 'IPTV в Тест. Режиме')], default=0, verbose_name='Тип подключения телевиденье')),
                ('exodus_in', models.SmallIntegerField(choices=[(0, 'Отказ'), (1, 'Оформленно'), (2, 'Консультация')], default=1, verbose_name='Исход интернет')),
                ('exodus_tv', models.SmallIntegerField(choices=[(0, 'Отказ'), (1, 'Оформленно'), (2, 'Консультация')], default=1, verbose_name='Исход телевиденье')),
                ('status', models.SmallIntegerField(choices=[(0, 'Отсутствует'), (1, 'В работе'), (2, 'Нет ответа'), (3, 'Подумает'), (4, 'Неверная'), (5, 'Выполнено')], default=0, verbose_name='Статус')),
                ('from_office', models.BooleanField(default=False, verbose_name='Офисное обращение')),
                ('priority_service', models.CharField(choices=[('SERVICE_A', 'Интернет'), ('SERVICE_B', 'Телевиденье')], default='SERVICE_A', max_length=15, verbose_name='Приоритетная Услуга')),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('call_date', models.DateTimeField(null=True)),
                ('plain_later', models.DateTimeField(null=True)),
                ('infinity_plain', models.BooleanField(default=False)),
                ('comments', models.ManyToManyField(to='front.CommentRow')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_by', to=settings.AUTH_USER_MODEL, verbose_name='Создатель')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('contract_assign', 'Может назначить пользователя на выполнение заявки'), ('contract_browse', 'Может просматривать заявки'), ('contract_create', 'Может создавать заявки'), ('contract_edit', 'Может редактировать заявки'), ('contract_comment', 'Может добавлять комментарий к заявке'), ('contract_close', 'Может закрывать заявку'), ('contract_time', 'Может отложить заявку'), ('contract_take', 'Может брать заявку')],
            },
        ),
    ]
