from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'scrape pages'
    def add_arguments(self, parser):
        # parser.add_argument('poll_id', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        import vpn_bot.wxbot.bot_app
        vpn_bot = bot_app.VPN_bot()
        vpn_bot.start()

