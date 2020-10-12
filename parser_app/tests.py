import datetime
from unittest.mock import patch

from django.test import TestCase, Client
from django.utils import timezone

from .models import Order, Contract, Update


class OrderTest(TestCase):
    def setUp(self) -> None:
        Order.objects.create(
            order_number='1',
            order_subject='Закупка одной херни',
            order_status='Согласование ОЗ',
            prev_order_status='Отложен',
            order_date=datetime.datetime.strptime('01.01.2020', "%d.%m.%Y").date(),
            price=100.00,
            prev_date_changed=timezone.localtime()
        )
        Order.objects.create(
            order_number='2',
            order_subject='Закупка другой херни',
            order_status='Согласование ОЗ',
            prev_order_status='Отложен',
            order_date=datetime.datetime.strptime('01.01.2020', "%d.%m.%Y").date(),
            price=100.00,
            prev_date_changed=timezone.localtime() - datetime.timedelta(days=4)
        )

        Update.objects.update_or_create(name='last', defaults={
            'last_successful_update': timezone.localtime()
        })

        Contract.objects.create(
            contract_number='1м-АВХ',
            contract_date=datetime.datetime.strptime('01.01.2020', "%d.%m.%Y").date(),
            price=100000.00,
            paid=100.00,
            prev_paid=50.00,
            prev_date_changed=timezone.localtime() - datetime.timedelta(days=4)
        )
        Contract.objects.create(
            contract_number='2м-АВХ',
            contract_date=datetime.datetime.strptime('02.01.2020', "%d.%m.%Y").date(),
            price=200000.00,
            paid=200.00,
            prev_paid=20.00,
            prev_date_changed=timezone.localtime() - datetime.timedelta(days=1)
        )

        self.client = Client()

    def testOrderCreated(self):
        order_one = Order.objects.get(order_number='1')
        self.assertEqual(order_one.recent, True)
        self.assertEqual(order_one.order_number, '1')
        order_two = Order.objects.get(order_number='2')
        self.assertEqual(order_two.recent, False)
        self.assertEqual(order_two.order_number, '2')
        contract_one = Contract.objects.get(contract_number='1м-АВХ')
        self.assertEqual(contract_one.paid_recently, False)
        self.assertEqual(contract_one.contract_number, '1м-АВХ')
        contract_two = Contract.objects.get(contract_number='2м-АВХ')
        self.assertEqual(contract_two.paid_recently, True)
        self.assertEqual(contract_two.contract_number, '2м-АВХ')

    def testPageRendering(self):
        # c = Client()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['orders']), 2)
        self.assertEqual(len(response.context['contracts']), 2)
        print(response.content.decode(encoding='utf-8'))
        # orderOne = Order.objects.get(order_number='1')
        # self.assertEqual(orderOne.recent, True)
        # self.assertEqual(orderOne.order_number, '1')
        self.assertContains(response, '<tr class="table-success">', count=2)
        self.assertContains(response,
                            f'''
        <tr class="table-success">
                                
                                    <td>1</td>
                                    <td>Закупка одной херни</td>
                                    <td>
                                        
                                            <span class="tooltippopup" data-html="true" title="Дата изменения: {timezone.localtime().date().strftime('%d/%m/%Y')}<br>
                                                                                      Предыдущий статус: Отложен">Согласование ОЗ</span>
                                        

                                    </td>
                                </tr>
        ''',
                            html=True
                            )


class TestOrderDateChanging(TestCase):
    @patch("django.db.models.signals.ModelSignal.send", autospec=True)
    def setUp(self, mock) -> None:
        order, created = Order.objects.update_or_create(
            order_number='22/Д',
            defaults={
                'order_date': datetime.datetime.strptime('06.07.2020',
                                                         "%d.%m.%Y").date(),
                'order_status': 'Отложен',
                'price': 100.00,
                'order_subject': 'Поставка хрентоваров'
            }
        )

    @patch("django.db.models.signals.ModelSignal.send", autospec=True)
    def testOrderDateChange(self, mock):
        self.assertEqual(Order.objects.get(order_number='22/Д').order_date, datetime.datetime.strptime('06.07.2020',
                                                                                                       "%d.%m.%Y").date())
        order, created = Order.objects.update_or_create(
            order_number='22/Д',
            defaults={
                'order_date': datetime.datetime.strptime('07.07.2020',
                                                         "%d.%m.%Y").date(),
                'order_status': 'Отложен',
                'price': 100.00,
                'order_subject': 'Поставка хрентоваров'
            }
        )
        self.assertEqual(Order.objects.get(order_number='22/Д').order_date, datetime.datetime.strptime('07.07.2020',
                                                                                                       "%d.%m.%Y").date())
        self.assertTrue(mock)
        print(order.order_number)
        print(order.order_date)
        print(order.order_status)
