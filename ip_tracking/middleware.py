from ipware import get_client_ip
from .models import RequestLog
from django.http import HttpResponseForbidden
from django.core.cache import cache
from .models import BlockedIP
import requests


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            ip, _ = get_client_ip(request)
            if ip:
                geo = cache.get(f"geo_{ip}")
                if geo is None:
                    try:
                        r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=2)
                        data = r.json()
                        geo = {"country": data.get("country"), "city": data.get("city")}
                    except Exception:
                        geo = {}
                    cache.set(f"geo_{ip}", geo, 86400)

                RequestLog.objects.create(
                    ip_address=ip,
                    path=request.path,
                    country=geo.get("country"),
                    city=geo.get("city"),
                )
        except Exception:
            pass
        return response


class IPBlockerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip, _ = get_client_ip(request)
        if not ip:
            return self.get_response(request)

        blocked = cache.get(f"blocked_{ip}")
        if blocked is None:
            blocked = BlockedIP.objects.filter(ip_address=ip).exists()
            cache.set(f"blocked_{ip}", blocked, 86400)

        if blocked:
            return HttpResponseForbidden("<h1>403 Forbidden</h1><p>Your IP has been blocked.</p>")

        return self.get_response(request)


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            ip, _ = get_client_ip(request)
            if ip:
                RequestLog.objects.create(ip_address=ip, path=request.path)
        except Exception:
            pass
        return response
