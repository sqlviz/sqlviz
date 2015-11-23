from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import json
import crawler

@login_required
def index(request):
    c = crawler.Crawler(request)
    r = c.crawl_all()
    return HttpResponse(
        json.dumps(r),
        content_type="application/json"
    )
