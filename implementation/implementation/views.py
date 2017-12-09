from django.views.generic import View
from django.http import JsonResponse
import json


class APIEndpoint(View):
    def post(self, request):
        data = json.loads(request.body)
        result = getattr(self, data["method"])(**data)
        return JsonResponse(result, safe=False)


class OrderListEndpoint(APIEndpoint):
    def get_orders(self, **kwargs):
        return []

    def get_routes(self, order, **kwargs):
        return {}

    def select_route(self, order, index, **kwargs):
        return {}
