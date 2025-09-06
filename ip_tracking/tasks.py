from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from django.db.models import Count
from .models import RequestLog, SuspiciousIP

@shared_task
def detect_anomalies():
    now = timezone.now()
    one_hour_ago = now - timedelta(hours=1)

    # high request rate
    qs = RequestLog.objects.filter(timestamp__gte=one_hour_ago)
    high = qs.values("ip_address").annotate(c=Count("id")).filter(c__gt=100)
    for item in high:
        SuspiciousIP.objects.get_or_create(
            ip_address=item["ip_address"],
            defaults={"reason": f"{item['c']} requests in last hour"},
        )

    # sensitive paths
    sensitive = qs.filter(path__in=["/admin", "/login"]).values("ip_address").distinct()
    for item in sensitive:
        SuspiciousIP.objects.get_or_create(
            ip_address=item["ip_address"],
            defaults={"reason": "Accessed sensitive path"},
        )
    return "done"
