from django.core.management.base import BaseCommand
from django.core.cache import cache
from ip_tracking.models import BlockedIP

class Command(BaseCommand):
    help = "Block an IP address"

    def add_arguments(self, parser):
        parser.add_argument("ip", type=str)
        parser.add_argument("--reason", type=str, default="Manual block")

    def handle(self, *args, **options):
        ip = options["ip"]
        reason = options["reason"]
        obj, created = BlockedIP.objects.get_or_create(ip_address=ip, defaults={"reason": reason})
        cache.set(f"blocked_{ip}", True, 86400)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Blocked {ip}"))
        else:
            self.stdout.write(f"{ip} was already blocked")
