import simplejson

from django.http import HttpResponse
from django.views import View


class TradeOrders(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse(headers={'Content-Type': "application/json"}, content=simplejson.dumps({'test': 'response'}))

