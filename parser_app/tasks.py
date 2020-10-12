import datetime
import hashlib
import json

import requests
from celery import shared_task
from django.utils import timezone

from vz_parser_frontend.settings import TELEGRAM_API_TOKEN
from .models import Contract, Order, Update, MessageRecipient

login = 'АВХ'
password = '123'


def parse_vz_v2(username: str, pwd: str):
    update_status = {
        'contracts': False,
        'orders': False
    }
    orders_date_from = '2020-01-01'
    orders_date_to = '2020-12-31'

    contract_date_from = '2019-12-20'
    contract_date_to = '2020-12-31'

    vz_root_url = 'http://web.volgzakaz.ru:8080/controller'

    disp_status_to_not_fetch_comments = ['7', '10']

    fetch_orders_params = (
        ('actionId', 'handler'),
        ('appObj', 'bft.gz.customrequestdoc'),
        ('method', 'read')
    )
    fetch_orders_dict = {
        'arg': ['["DISPSTATUS_CAPTION","DOC_NUMBER","DOC_DATE","AMOUNT","CUSTOMERCAPTION","PURCHASEMODE_ID",'
                '"PURCHASEMODE_CAPTION","SUBJECT","MARKET_DOCID","MARKET_TYPE","SIGN_CNT","ATT_SIGN_CNT",'
                '"RETENTION_FONT","RETENTION_MSG","ID","DOCUMENT_ID","VERSION","DISPSTATUS_ID",'
                '"DOCUMENTCLASS_ID","PARENT_ID"]',
                f'{{"DATE_FROM": "{orders_date_from}", "DATE_TO": "{orders_date_to}", "DOC_NUMBER_STRICT": "0", '
                f'"PLAN_DEALDATE_FROM": "", '
                '"PLAN_DEALDATE_TO":"","CUSTOMER_INVERT":false,"ORGCHILD":"0","PLAN_INVITATIONDATE_FROM":"",'
                '"PLAN_INVITATIONDATE_TO":"","SUPPLY_DATE_FROM":"","SUPPLY_DATE_TO":"","AMOUNT_FROM":null,'
                '"AMOUNT_TO":null,'
                '"INCOME_DATE_FROM":"","INCOME_DATE_TO":"","ADDRESS_TYPE":null,"WO_CODE5":false,"WO_CODE1":false,'
                '"WO_CODE2":false,"WO_CODE3":false,"WO_CODE4":false,"WO_CODE6":false,"WO_CODE7":false,'
                '"WO_CODE8":false,"WO_CODE10":false,"WO_CODE9":false,"WO_INDUSTRYCODE":false,'
                '"WO_GRANTINVESTMENT":false,"LASTCHAIN":false,"ANNUALITY":"0","WITH_CURYEARAMOUNT":false,'
                '"WITH_YEAR2AMT":false,"WITH_YEAR3AMT":false,"WITH_FUTUREAMT":false,"ROLE_TERM":true,'
                '"SIGN_CNT":null,"ATT_SIGN_CNT":null,"SIGN_VALID":"0","__ctx_fieldValue":"",'
                '"__ctx_fieldName":"ETP_ADDRESS","__ctx_caseSens":false,"__ctx_wholeWord":false}',
                '["DOC_DATE"]',
                'false'
                ]
    }

    fetch_contract_params = (
        ('actionId', 'handler'),
        ('appObj', 'bft.gz.stateContract'),
        ('method', 'read')
    )
    fetch_contracts_dict = {
        'arg': [
            '["DISPSTATUS_CAPTION","DOC_NUMBER","DOC_DATE","AMOUNT","PAYEDAMOUNT","SUPPLIEDAMOUNT",'
            '"CUSTOMERCAPTION","CONNAME","PURCHASEMODE_CAPTION","DEALDATE","SUBJECT","CON_NUMBER",'
            '"SINGLECUSTOMERREASON_NAME","DESCRIPTION","GRNTAMOUNT","ID","DOCUMENT_ID","VERSION","CONTYPE_ID",'
            '"CURRENCY_ID","SIGN_CNT","ATT_SIGN_CNT","RETENTION_FONT","RETENTION_MSG",'
            '"DISPSTATUS_ID","DOCUMENTCLASS_ID","PARENT_ID"]',
            f'{{"DOC_NUMBER_STRICT":"0","DISPSTATUS_ID_LIST":"6","ORGCHILD":false,"DATE_FROM":"{contract_date_from}",'
            f'"DATE_TO":"{contract_date_to}", '
            '"DEALDATE_FROM":"","DEALDATE_TO":"","GROUPCODE_WITH_CHILDREN":false,'
            '"AMOUNT_FROM":null,"AMOUNT_TO":null,"WO_CODE5":false,"WO_CODE1":false,"WO_CODE2":false,'
            '"WO_CODE3":false,"WO_CODE4":false,"WO_CODE6":false,"WO_CODE7":false,"WO_CODE8":false,"WO_CODE10":false,'
            '"WO_CODE9":false,"WO_INDUSTRYCODE":false,"WO_GRANTINVESTMENT":false,'
            '"STARTDATE_FROM":"","STARTDATE_TO":"","FINISHDATE_FROM":"","FINISHDATE_TO":"",'
            '"CON_DATE_FROM":"","CON_DATE_TO":"","COMPLETE_DATE_FROM":null,"COMPLETE_DATE_TO":null,'
            '"DISSOLVE_DATE_FROM":null,"DISSOLVE_DATE_TO":null,"PARENT_MODE":"0","PARENTCLASS_ID_LIST":null,'
            '"SINGLECUSTOMERREASON_INSTEAD":false,"DISSOLVE_OR_COMPLETE":"0","ROLE_TERM":true,"SIGN_CNT":null,'
            '"ATT_SIGN_CNT":null,"__ctx_fieldValue":"","__ctx_fieldName":"SUBJECT","__ctx_caseSens":false,'
            '"__ctx_wholeWord":false,"COMPLETE_DATE":"","DISSOLVE_DATE":""}',
            '["DOC_DATE"]',
            'false'
        ]
    }

    fetch_comments_params = (
        ('actionId', 'handler'),
        ('appObj', 'bft.gz.customrequestdoc'),
        ('method', 'getCommentsList'),
    )
    # "DISPSTATUS_ID_LIST":"6" - contract status filter (6 - Execution)

    password_hash = hashlib.md5(pwd.encode('utf-8')).hexdigest().upper()

    # get auth cookie
    auth_url = 'http://web.volgzakaz.ru:8080/login'
    auth_data = {
        'loginUsername': username,
        'loginPassword': f"ver3:{password_hash}",
        'rememberLogin': 'true'
    }

    with requests.Session() as s:

        s.post(auth_url, auth_data)

        response_orders = s.post(vz_root_url, params=fetch_orders_params, data=fetch_orders_dict)
        response_contract = s.post(vz_root_url, params=fetch_contract_params, data=fetch_contracts_dict)

        # convert responses to dicts
        orders_json = json.loads(response_orders.text)
        contracts_json = json.loads(response_contract.text)

        if orders_json['success'] == 'true' and len(orders_json['data']['data']) == orders_json['data']['totalCount']:
            Update.objects.update_or_create(name='last', defaults={
                'last_orders_update': timezone.localtime()
            })

        if contracts_json['success'] == 'true' and len(contracts_json['data']['data']) == contracts_json['data'][
            'totalCount']:
            Update.objects.update_or_create(name='last', defaults={
                'last_contracts_update': timezone.localtime()
            })

        for contract in contracts_json['data']['data']:
            cont, created = Contract.objects.update_or_create(
                id=int(contract['ID']),
                defaults={
                    'contract_number': contract['DOC_NUMBER'].strip(),
                    'contract_date': datetime.datetime.strptime(contract['DOC_DATE'], "%Y-%m-%d").date(),
                    'paid': float(contract['PAYEDAMOUNT']),
                    'price': float(contract['AMOUNT']),
                }
            )
            cont.save()
        update_status['contracts'] = True

        for order in orders_json['data']['data']:
            comments_text = ''
            # Если заявка - не закупка у ед. поставщика, получить комментарии
            if order['PURCHASEMODE_ID'] != '3':
                fetch_comments_dict = {
                    'arg': order['ID'],
                }
                comments = s.post(vz_root_url, params=fetch_comments_params, data=fetch_comments_dict)
                comments_json = json.loads(comments.text)
                comments_list = [item['user'] + '\n' + item['text'] for item in comments_json['data']]
                comments_text = '\n------\n'.join(comments_list)
            current_order, created = Order.objects.update_or_create(
                id=int(order['ID']),
                defaults={
                    'order_number': order['DOC_NUMBER'].strip(),
                    'order_date': datetime.datetime.strptime(order['DOC_DATE'], "%Y-%m-%d").date(),
                    'order_subject': order['SUBJECT'],
                    'order_status': order['DISPSTATUS_CAPTION'],
                    'price': float(order['AMOUNT']),
                    'order_comments': comments_text
                }
            )
            current_order.save()
        update_status['orders'] = True

        if update_status['orders'] and update_status['contracts']:
            Update.objects.update_or_create(name='last', defaults={
                'last_successful_update': timezone.localtime()
            })


# celery beat --app=vz_parser_frontend.celery:app --loglevel=INFO
# celery worker --app=vz_parser_frontend.celery:app --loglevel=INFO --pool=solo
# celery purge --app=vz_parser_frontend.celery:app

# https://api.telegram.org/bot<token>/METHOD_NAME

@shared_task
def parse_vz():
    parse_vz_v2(username=login, pwd=password)
    return True


@shared_task
def send_telegram_msg(detect_changes: dict):
    url = f'https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage'
    text = ''
    recipients = list(MessageRecipient.objects.values_list('telegram_id', flat=True))

    if detect_changes['change_type'] == 'order':
        text = f'Изменения по закупке: {detect_changes["order_number"]}: {detect_changes["order_subject"]}'
        text += f"\nСтатус: <s>{detect_changes['prev_status']}</s> {detect_changes['status']}"
    elif detect_changes['change_type'] == 'contract':
        text = f'Изменения по контракту: {detect_changes["contract_number"]} от {detect_changes["contract_date"]}'
        text += f"\nОплачено: <strong>{detect_changes['paid'] - detect_changes['prev_paid']}</strong>"
    elif detect_changes['change_type'] == 'comment':
        order_comments = detect_changes.get('order_comments', '') or ''
        prev_order_comments = detect_changes.get('prev_order_comments', '') or ''
        comment = order_comments.replace(prev_order_comments, '')
        text = f'Новый комментарий к закупке: {detect_changes["order_number"]}: {detect_changes["order_subject"]}'
        text += f"\nКомментарий: <strong>{comment}</strong>"

    for recipient in recipients:
        data = {
            'chat_id': recipient,
            'text': text,
            'parse_mode': 'HTML'
        }
        requests.post(url, data=data)
