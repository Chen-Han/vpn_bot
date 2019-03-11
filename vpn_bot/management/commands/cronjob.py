# coding: utf-8
from django.core.management.base import BaseCommand
from vpn_bot.models import Order, VPN_service
from vpn_bot.shadowsocks.api import ping, close_port
from vpn_bot.wxbot.api import Bot_api
import datetime
import logging

def notify_customer(bot_api, customer):
    msg = u'你好，你的服务刚刚过期，需要续费的话可以回复【购买】哦'
    bot_api.send_msg(customer.wechat_id,msg)

def expire_pending_orders():
    ten_min_ago = datetime.datetime.now() - datetime.timedelta(minutes=10)
    expired_orders = Order.objects.filter(state=Order.PENDING, \
        payment_code_issued_at__lte=ten_min_ago)
    for o in expired_orders:
        o.state = Order.EXPIRED
        o.save()

def expire_vpn_services(bot_api):
    now = datetime.datetime.now()
    expired_vpn_services = list(VPN_service.objects.filter(expire_on__lte=now, is_active=1))
    for expired_service in expired_vpn_services:
        customer_name = expired_service.order_id.customer_id.name
        customer_id = expired_service.order_id.customer_id.wechat_id
        logging.info('Found expired service with id {}, for customer {}, '\
            'with name {}, closing vpn service at port {}'.format(
                expired_service.id,
                customer_name,
                customer_id,
                expired_service.port))
        close_port(expired_service.port)
        logging.info('port {} closed successfully, notifying customer'\
            .format(expired_service.port))
        expired_service.is_active = 0
        expired_service.save()
        customer = expired_service.order_id.customer_id
        notify_customer(bot_api, customer)
        logging.info('Notified customer {}'.format(customer_name))

class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        bot_api = Bot_api()
        ping()
        expire_pending_orders()
        expire_vpn_services(bot_api)

