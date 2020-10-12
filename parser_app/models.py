import datetime

from django.db import models
from django.utils import timezone


class Contract(models.Model):
    id = models.IntegerField(primary_key=True)
    contract_number = models.CharField(max_length=200, verbose_name='Номер контракта')
    contract_date = models.DateField(verbose_name='Дата заключения контракта')
    price = models.FloatField(blank=True, null=True, verbose_name='Сумма контракта')
    paid = models.FloatField(blank=True, null=True, verbose_name='Оплачено')
    prev_paid = models.FloatField(blank=True, null=True)
    prev_date_changed = models.DateTimeField(blank=True, null=True)
    date_changed = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Контракт "{self.contract_number}"'

    @property
    def paid_recently(self):
        if self.prev_date_changed:
            return self.prev_date_changed > (timezone.localtime() - datetime.timedelta(days=3))
        return False


class Order(models.Model):
    id = models.IntegerField(primary_key=True)
    order_number = models.CharField(max_length=200, verbose_name='Номер заявки')
    order_date = models.DateField(verbose_name='Дата заявки', blank=True, null=True)
    order_subject = models.CharField(blank=True, null=True, max_length=1000, verbose_name='Предмет заявки')
    order_status = models.CharField(blank=True, null=True, max_length=200, verbose_name='Статус заявки')
    prev_order_status = models.CharField(max_length=200, verbose_name='Предыдущий статус заявки', null=True, blank=True)
    price = models.FloatField(blank=True, null=True, verbose_name='НМЦК')
    prev_date_changed = models.DateTimeField(blank=True, null=True)
    date_changed = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)
    order_comments = models.CharField(blank=True, null=True, max_length=20000, verbose_name='Комментарии к заявке')
    prev_order_comments = models.CharField(blank=True, null=True, max_length=20000,
                                           verbose_name='Предыдущие комментарии к заявке')

    def __str__(self):
        return f'Заявка "{self.order_subject}"'

    @property
    def recent(self):
        if self.prev_date_changed:
            return self.prev_date_changed > (timezone.localtime() - datetime.timedelta(days=3))
        return False


class Update(models.Model):
    name = models.CharField(max_length=20)
    last_successful_update = models.DateTimeField(blank=True, null=True)
    last_orders_update = models.DateTimeField(blank=True, null=True)
    last_contracts_update = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.last_successful_update.strftime('%d.%m.%Y %H-%M')


class MessageRecipient(models.Model):
    telegram_id = models.BigIntegerField(verbose_name='Telegram ID')
    name = models.CharField(max_length=200, verbose_name='Имя получателя сообщения')

    def __str__(self):
        return f'{self.name} Telegram ID: {self.telegram_id}'
