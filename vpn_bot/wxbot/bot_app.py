#!/usr/bin/env python
# coding: utf-8
import wxpy
import logging
from decimal import Decimal
import sys
import random
import socket
import datetime
sys.path.append("..") 
from vpn_bot.models import Order, Customer, VPN_service
import vpn_bot.shadowsocks.api as api
from vpn_bot.wxbot.api import Bot_server

logging.basicConfig(level=logging.INFO)
ch = logging.StreamHandler(sys.stdout)

NEW_CUSTOMER_ONE_WEEK_DISCOUNT = 'new customer one week discount'

IP = '35.236.145.194'

def find_pending_order(payment_code):
    orders = Order.objects.filter(state=Order.PENDING, payment_code=payment_code)
    if len(orders) > 1:
        logging.warn('For payment_code {}, found more than 1 order.'\
            '\n Order ids: {}'
            .format(payment_code,','.join([str(o.id) for o in orders])))
    if len(orders) == 0:
        return None
    return orders[0]

def match_item_type_by_value(value):
    if value == Decimal('3.00'):
        return Order.ONE_WEEK
    elif value == Decimal('10.00'):
        return Order.ONE_MONTH
    elif value == Decimal('30.00'):
        return Order.THREE_MONTH
    return None

def complete_order(order, payment_value, item_type, msg):
    logging.info('Completing item order of {}, amount paid: {}'\
        .format(item_type, payment_value))
    port, password = api.open_services()
    today = datetime.datetime.now()
    days = 0
    if item_type == Order.ONE_WEEK:
        days = 7
    elif item_type == Order.ONE_MONTH:
        days=30
    elif item_type == Order.THREE_MONTH:
        days=90
    if order.comment == NEW_CUSTOMER_ONE_WEEK_DISCOUNT:
        days += 7
    expire_on = today + datetime.timedelta(days=days)
    vpn_service = VPN_service.objects.create(order_id=order,\
        start_time=today, expire_on=expire_on, ip=IP,\
        port=port, password=password, is_active=1)
    logging.info('Created service at {}:{}, pass: {}; expiring_on: {}'\
        .format(ip, port, password, expire_on))
    order.state = Order.COMPLETED
    order.transaction_id = str(msg.id)
    order.transaction_type = Order.WECHAT
    order.item_type = item_type
    order.payment_value = payment_value
    order.save()
    return vpn_service

def generate_pending_order(customer):
    payment_code = ''.join([str(random.randint(0,9)) for _ in range(6)])
    new_customer = Order.objects.filter(state=Order.COMPLETED,\
        customer_id=customer).count() == 0
    comment = NEW_CUSTOMER_ONE_WEEK_DISCOUNT if new_customer else None
    order = Order.objects.create(state=Order.PENDING,\
        customer_id=customer, payment_code=payment_code,\
        comment=comment)
    return order

def reply_with_service_info(customer, bot, vpn_service):
    ip,port,password,expire_on = \
        vpn_service.ip,vpn_service.port,vpn_service.password,\
        vpn_service.expire_on
    expire_on = expire_on.strftime('%Y-%m-%d %H:%M %p')
    receiver = wxpy.ensure_one(bot.friends()\
        .search(user_name=customer.wechat_id))
    receiver.send(u'台湾服务器:{ip},端口:{port},密码:{password};'\
        '到期时间:{expire_on}'
        .format(ip=ip,port=port,password=password,expire_on=expire_on))

def send_purchase_info(msg):
    msg.reply(u'你好我是VPN小助手，台服VPN，3块钱一个星期，'\
        '10块钱一个月，第一次买的话有一个星期免费，请问需要购买吗？回复【购买】')

def send_order_info_and_payment_code(msg, payment_code):
    msg.reply(u'上面是收款码，请在五分钟之内付款哦，'\
        '付款的时候填写备注{}，要不然系统不知道这是你付的'\
        .format(payment_code))

def send_order_still_pending(msg, order):
    msg.reply(u'你的支付码{}还可以继续使用哦，请扫二维码完成支付'\
        .format(order.payment_code))


class VPN_bot(object):
    def __init__(self):
        print('Please log in by scanning QR code')
        self.bot = wxpy.Bot(cache_path=True,console_qr=True)
        self.bot.enable_puid()
        self.payment_mp = wxpy.ensure_one(self.bot.mps().search(u'微信支付'))
        self.developer = self.bot.friends().search('Han Chen')[0]
        logging.info('setting developer to: {}, with wechat id: {}'\
            .format(self.developer.name, self.developer.user_name))
        self._register_wechat_listeners()
        logging.debug('registered wechat listeners')
        self._start_bot_server()
        logging.debug('started bot server')


    def start(self):
        self.bot.join()

    def notify_developer(self, payment_id=None, additional_info=None):
        import datetime
        self.developer.send('At {time}, there is an issue: {info}'\
                .format(time=str(datetime.datetime.now()), info=additional_info))

    def _start_bot_server(self):
        '''
        handles request from other processes
        '''
        self.bot_server = Bot_server()

        def handle_msg_send(wechat_id, msg):
            user = wxpy.ensure_one(self.bot.friends().search(user_name=wechat_id))
            user.send(msg)

        self.bot_server.register_msg_handler(handle_msg_send)
        self.bot_server.start_listening()

    def _register_wechat_listeners(self):
        @self.bot.register()
        def print_others(msg):
            print(str(msg))
            print(msg.sender)
            if type(msg.sender) != wxpy.Friend:
                return
            customer = None
            wechat_id = msg.sender.user_name
            is_new_customer = False
            try:
                customer = Customer.objects.get(wechat_id=wechat_id)
            except(Customer.DoesNotExist) as e:
                # adding new customer
                customer = Customer.objects.create(wechat_id=wechat_id)
                is_new_customer = True
            if is_new_customer:
                send_purchase_info(msg)
                return
            pending_orders = Order.objects.filter(
                state=Order.PENDING, customer_id=customer)
            print(pending_orders)
            if len(pending_orders) > 1:
                logging.warn(customer, \
                    'Customer with {} and wechat_id {} had more than one pending order'\
                    .format(customer.id, customer.wechat_id))
            pending_order_exists = len(pending_orders) > 0
            if msg.text == '购买' and not pending_order_exists:
                order = generate_pending_order(customer)
                payment_code = order.payment_code
                send_order_info_and_payment_code(msg, payment_code)
                return
            elif msg.text == '购买' and pending_order_exists:
                order = pending_orders[0]
                send_order_still_pending(msg, order)
                return
            elif pending_order_exists:
                msg.reply(u'请问付款的时候是不是出问题了，'\
                    '可以回复【客服】联系客服，会尽快回复你的')
            elif msg.text == '客服':
                self.notify_developer()
                msg.reply(u'已经在联系客服了，请你稍等哦')
                return
            return

        @self.bot.register(chats=self.payment_mp, msg_types=wxpy.SHARING)
        def on_receive_pay_msg(self, msg):
            def find_payment_code(txt):
                import re
                matching = re.search('<!\[CDATA\[收款金额：￥.+\n付款方备注：(\d{4,6})',txt)
                if matching:
                    return matching.group(1)
                return None
            def find_payment_val(txt):
                import re
                matching = re.search('<!\[CDATA\[收款金额：￥(\d+.\d+)',txt)
                if matching:
                    return matching.group(1)
                return None
            content = msg.raw['Content']
            logging.info('Received new payment info: {}'.format(msg.text))
            payment_code = find_payment_code(content)
            value_raw = find_payment_val(content)
            logging.info('Found payment_code {}, value {}'.format(payment_code, value_raw))
            if not value_raw:
                # not a payment message
                return
            order = find_pending_order(payment_code)
            value = Decimal(value_raw)
            item_type = match_item_type_by_value(value)
            if value_raw and (not order or (not item_type)):
                # payment without code or with wrong code, might be a customer error
                additional_info = 'For payment of value {},'.format(value_raw)
                if not order:
                    additional_info += ' order not found for this; '
                elif not item_type:
                    additional_info += ' cannot match an item based on this value; '
                additional_info += 'additional information: ' + str(msg.raw)
                self.notify_developer(additional_info=additional_info)
                return
            # now proceed with transaction
            vpn_service = complete_order(order, value, item_type, msg)
            reply_with_service_info(order.customer_id, self.bot, vpn_service)

