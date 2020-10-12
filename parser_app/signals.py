from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Order, Contract
from .tasks import send_telegram_msg


@receiver(pre_save, sender=Order)
def order_signal(sender, instance: Order, **kwargs):
    try:
        changed_order = Order.objects.get(id=instance.id)

        if instance.order_status != changed_order.order_status:
            detect_changes = {
                'change_type': 'order',
                'status': instance.order_status,
                'prev_status': changed_order.order_status,
                'order_number': instance.order_number,
                'order_subject': instance.order_subject
            }
            instance.prev_order_status = changed_order.order_status
            instance.prev_date_changed = changed_order.date_changed
            send_telegram_msg.delay(detect_changes)

        if instance.order_comments != changed_order.order_comments:
            detect_changes = {
                'change_type': 'comment',
                'order_number': instance.order_number,
                'order_subject': instance.order_subject,
                'order_comments': instance.order_comments,
                'prev_order_comments': instance.prev_order_comments
            }
            instance.prev_order_comments = changed_order.order_comments
            instance.prev_date_changed = changed_order.date_changed
            send_telegram_msg.delay(detect_changes)

    except Order.DoesNotExist:
        pass


@receiver(pre_save, sender=Contract)
def contract_signal(sender, instance: Contract, **kwargs):
    try:
        changed_contract = Contract.objects.get(id=instance.id)
        if instance.paid != changed_contract.paid:
            detect_changes = {
                'change_type': 'contract',
                'contract_number': instance.contract_number,
                'contract_date': instance.contract_date.strftime('%d.%m.%Y'),
                'paid': instance.paid,
                'prev_paid': changed_contract.paid
            }
            instance.prev_paid = changed_contract.paid
            instance.prev_date_changed = changed_contract.date_changed
            send_telegram_msg.delay(detect_changes)
    except Contract.DoesNotExist:
        pass
