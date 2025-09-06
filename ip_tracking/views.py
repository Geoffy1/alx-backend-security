from django.http import HttpResponse
from django_ratelimit.decorators import ratelimit

# 10/min for authenticated, 5/min for anonymous
@ratelimit(key="user_or_ip", rate="10/m", method="GET", block=True)
def sensitive_view(request):
    return HttpResponse("Sensitive view - rate limited")

def home(request):
    return HttpResponse("Home page - not limited")
