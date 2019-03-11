from django.core.management.base import BaseCommand, CommandError
import vpn_bot.models as models
from vpn_bot.shadowsocks.api import open_port

class Command(BaseCommand):
    def add_arguments(self, parser):
        # parser.add_argument('poll_id', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        active_services = models.VPN_service.objects.filter(is_active=1)
        for a in active_services:
            open_port(a.port, a.password)
