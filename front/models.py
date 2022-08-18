from django import forms
from django.contrib.auth.models import User, AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.contrib.postgres.search import SearchVectorField

STATE_NOTPROCESSED = 0
STATE_LATER = 1
STATE_REPROCESSING = 2
STATE_COMPLETE = 3
STATE_INPROGRESS = 4

STATE_CHOICE = (
    (STATE_NOTPROCESSED, "Необработанная"),
    (STATE_LATER, "Ожидание"),
    (STATE_INPROGRESS, "В обработке"),
    (STATE_REPROCESSING, "Повторная обработка"),
    (STATE_COMPLETE, "Оформленна"),
)

SERVICE_A = 1
SERVICE_B = 2

SERVICE_CHOICE = (
    (SERVICE_A, "Интернет"),
    (SERVICE_B, "Телевиденье"),
)

STATUS_NONE = 0
STATUS_WORKS = 1
STATUS_NO_ANSWER = 2
STATUS_THINK = 3
STATUS_INCORRECT = 4
STATUS_COMPLETE = 5

STATUS_CHOICE = (
    (STATUS_NONE, "Отсутствует"),
    (STATUS_WORKS, "В работе"),
    (STATUS_NO_ANSWER, "Нет ответа"),
    (STATUS_THINK, "Подумает"),
    (STATUS_INCORRECT, "Неверная"),
    (STATUS_COMPLETE, "Выполнено")
)

EXODUS_FAIL = 0
EXODUS_SOLVED = 1
EXODUS_CONSULTATION = 2

EXODUS_CHOICE = (
    (EXODUS_FAIL, "Отказ"),
    (EXODUS_SOLVED, "Оформленно"),
    (EXODUS_CONSULTATION, "Консультация"),
)

CONDITIONS_UNKNOWN = 0
CONDITIONS_INDIVIDUAL = 1
CONDITIONS_STOCK_HOME = 2
CONDITIONS_STOCK_PON = 3
CONDITIONS_STOCK_TV = 4

CONDITIONS_CHOICE = (
    (CONDITIONS_INDIVIDUAL, "Индивидуальные"),
    (CONDITIONS_STOCK_HOME, "Акционные (0*3)"),
    (CONDITIONS_STOCK_PON, "10 дней - за 500"),
    (CONDITIONS_STOCK_TV, "Акционные (0*0)")
)
EQUIPMENT_1_IN = 0
EQUIPMENT_2_IN = 1
EQUIPMENT_3_IN = 2
EQUIPMENT_4_IN = 3
EQUIPMENT_5_IN = 4
EQUIPMENT_6_IN = 5
EQUIPMENT_7_IN = 6

EQUIPMENT_CHOICE_IN = (
    (EQUIPMENT_1_IN, "841n - 555"),
    (EQUIPMENT_2_IN, "ArcherC24 - 800"),
    (EQUIPMENT_3_IN, "ArcherC54 - 900"),
    (EQUIPMENT_4_IN, "ArcherC5 - 1399"),
    (EQUIPMENT_5_IN, "ArcherAx10 - 1599"),
    (EQUIPMENT_6_IN, "InextTV5 - 850"),
    (EQUIPMENT_7_IN, "Не требуется"),
)

EQUIPMENT_TV_1 = 0
EQUIPMENT_TV_2 = 1

EQUIPMENT_CHOICE_TV = (
    (EQUIPMENT_TV_1, "Не требуется"),
    (EQUIPMENT_TV_2, "InextTV5 - 850"),
)

CONNECT_TYPE_UNKNOWN = 0
CONNECT_TYPE_Plug = 1
CONNECT_TYPE_Disable = 2
CONNECT_TYPE_Repeated = 3

CONNECT_TYPE_CHOICE = (
    (CONNECT_TYPE_Plug, "Подключение услуг"),
    (CONNECT_TYPE_Disable, "Отключение услуг"),
    (CONNECT_TYPE_Repeated, "Повторная консультация")
)

CONNECT_TYPE_INTERNET_UNKNOWN = 0
CONNECT_TYPE_INTERNET_HOME_TO_CITY = 1
CONNECT_TYPE_INTERNET_GPON_TO_CITY = 2
CONNECT_TYPE_INTERNET_GPON_TO_HOUSE = 3
CONNECT_TYPE_INTERNET_RADIO_TO_HOUSE = 4
CONNECT_TYPE_INTERNET_INDIVIDUAL_TO_ALL = 5

CONNECTION_TYPE_INTERNET_CHOISE = (
    (CONNECT_TYPE_INTERNET_HOME_TO_CITY, "HOME в Многокварт."),
    (CONNECT_TYPE_INTERNET_GPON_TO_CITY, "GPON в Многокварт."),
    (CONNECT_TYPE_INTERNET_GPON_TO_HOUSE, "GPON в Частный"),
    (CONNECT_TYPE_INTERNET_RADIO_TO_HOUSE, "Radio в Частный"),
    (CONNECT_TYPE_INTERNET_INDIVIDUAL_TO_ALL, "Индивидуальное")
)
CONNECT_TYPE_TV_UNKNOWN = 0
CONNECT_TYPE_TV_IPTV = 1
CONNECT_TYPE_TV_ACTV = 2
CONNECT_TYPE_TV_IPTV_TEST = 3

CONNECT_TYPE_TV_CHOISE = (
    (CONNECT_TYPE_TV_UNKNOWN, "Не выбрано"),
    (CONNECT_TYPE_TV_IPTV, "IPTV"),
    (CONNECT_TYPE_TV_ACTV, "Аналоговое Телевиденье"),
    (CONNECT_TYPE_TV_IPTV_TEST, "IPTV в Тест. Режиме")
)


class FrontUser(AbstractUser):
    done_count = models.IntegerField(default=0)


class CommentRow(models.Model):
    class Meta:
        ordering = ['-create_date']

    user = models.ForeignKey(
        FrontUser,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    changes = models.TextField(blank=True)
    text = models.TextField(blank=True)


class ChoiceArrayField(ArrayField):
    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.MultipleChoiceField,
            'choices':    self.base_field.choices,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)


STATISTIC_UNKNOWN = 0
STATISTIC_NO_AUTO_ASSIGN = 1

STATISTIC_CHOICE = (
    (STATISTIC_NO_AUTO_ASSIGN, "Не назначен пользователь после создания"),
)

class Statistic(models.Model):
    name = models.IntegerField(choices=STATISTIC_CHOICE, default=STATISTIC_UNKNOWN)
    date = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def log(action):
        return Statistic.objects.create(name=action)


class Contract(models.Model):
    class Meta:
        permissions = [
            ("contract_assign", "Может назначить пользователя на выполнение заявки"),
            ("contract_browse", "Может просматривать заявки"),
            ("contract_create", "Может создавать заявки"),
            ("contract_edit", "Может редактировать заявки"),
            ("contract_comment", "Может добавлять комментарий к заявке"),
            ("contract_close", "Может закрывать заявку"),
            ("contract_time", "Может отложить заявку"),
            ("contract_take", "Может брать заявку"),
        ]

    name = models.CharField("Фио", max_length=50, blank=True)
    city = models.CharField("Город", max_length=50, blank=True)
    address = models.CharField("Адрес", max_length=100, blank=True)
    phone = models.CharField("Телефон", max_length=20, blank=True)

    created_by = models.ForeignKey(
        FrontUser, verbose_name="Создатель", on_delete=models.SET_NULL, null=True,
        related_name="created_by")

    user = models.ForeignKey(FrontUser, on_delete=models.SET_NULL, null=True)
    request_number = models.CharField(max_length=20, null=True, blank=True)
    contract_condition = models.TextField(null=True, blank=True)
    #tsv = SearchVectorField(null=True)
    state = models.SmallIntegerField(
        "Состояние",
        choices=STATE_CHOICE,
        default=STATE_NOTPROCESSED,
        blank=True)  # состояние
    service_first = models.CharField(
        "Услуга",
        max_length=50,
        default="Интернет",
        blank=True,
        null=True)  # Услуга №1
    service_two = models.CharField(
        "Услуга",
        max_length=50,
        default="Телевиденье",
        blank=True,
        null=True)  # Услуга №2
    conditions_first = models.SmallIntegerField(
        "Условия интернет",
        choices=CONDITIONS_CHOICE,
        default=CONDITIONS_STOCK_HOME,
        null=True,
        blank = True)
    conditions_two = models.SmallIntegerField(
        "Условия телевиденье",
        choices=CONDITIONS_CHOICE,
        default=CONDITIONS_STOCK_TV,
        null=True,
        blank = True)
    equipment_first = models.SmallIntegerField(
        "Оборудование интернет",
        choices=EQUIPMENT_CHOICE_IN,
        default=EQUIPMENT_7_IN,
        null=True,
        blank = True)  # Оборудование №2
    equipment_two = models.SmallIntegerField(
        "Оборудование телевиденье",
        choices=EQUIPMENT_CHOICE_TV,
        default=EQUIPMENT_TV_1,
        null=True,
        blank = True)  # Оборудование №2
    type_first = models.SmallIntegerField(
        "Тип подключения интернет",
        choices=CONNECTION_TYPE_INTERNET_CHOISE,
        null=True,
        blank = True)  # Тип подключение №1
    type_two = models.SmallIntegerField(
        "Тип подключения телевиденье",
        choices=CONNECT_TYPE_TV_CHOISE,
        null=True,
        blank = True)  # Тип подключение №2
    exodus_in = models.SmallIntegerField(
        "Исход интернет",
        choices=EXODUS_CHOICE,
        blank=True,
        null=True,
        default=EXODUS_SOLVED)  # Исход
    exodus_tv = models.SmallIntegerField(
        "Исход телевиденье",
        choices=EXODUS_CHOICE,
        blank=True,
        null=True,
        default=EXODUS_SOLVED)  # Исход
    status = models.SmallIntegerField(
        "Статус",
        choices=STATUS_CHOICE,
        blank = True,
        null = True,
        default=STATUS_NONE)  # Статус
    from_office = models.BooleanField("Офисное обращение", default=False)
    priority_service = models.CharField(
        "Приоритетная Услуга",
        max_length=15,
        choices=SERVICE_CHOICE,
        default='SERVICE_A',
        blank=True)

    create_date = models.DateTimeField(auto_now_add=True)
    # closed_time = models.DateTimeField(auto_now_add=True)
    call_date = models.DateTimeField(null=True)

    comments = models.ManyToManyField(CommentRow)

    plain_later = models.DateTimeField(null=True)
    infinity_plain = models.BooleanField(default=False)

    def history_add(self, user, changes):
        comment = CommentRow(user=user)
        if changes:
            comment.changes = changes
        comment.save()
        self.comments.add(comment)

    def comment_add(self, user, text):
        comment = CommentRow(user=user)
        if text:
            comment.text = text
        comment.save()
        self.comments.add(comment)


