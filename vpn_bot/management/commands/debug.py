from django.core.management.base import BaseCommand, CommandError
import vpn_bot.models as models
from IPython import embed
from decimal import Decimal
import datetime
def create_expiring_service():
    customer = models.Customer.objects.get_or_create(wechat_id='@123456', name='test')
    order = models.Order.objects.create(state=Order.COMPLETED,\
        payment_code='12345',\
        payment_value=Decimal('1.0'),
        transaction_id='a12345678',
        transaction_type=Order.WECHAT,
        customer_id=customer,
        item_type=Order.ONE_WEEK)
    seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7,minutes=1)
    one_min_ago = seven_days_ago + datetime.timedelta(days=7)
    vpn_service = models.VPN_service.create(is_active=1, ip='0.0.0.0',
        port=1234,password='7383',order_id=Order,start_time=seven_days_ago,
        expire_on=one_min_ago)



class Command(BaseCommand):
    help = 'scrape pages'
    def add_arguments(self, parser):
        # parser.add_argument('poll_id', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        embed()
