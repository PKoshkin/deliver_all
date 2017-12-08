from django.views.generic import View
from django.http import JsonResponse


class APIEndpoint(View):
    def post(self, request):
        result = getattr(self, request.POST["method"])(**request.POST)
        return JsonResponse(result)


class OrderListEndpoint(APIEndpoint):
    def get_orders(self, order, **kwargs):
        pass

    def select_route(self, order, index):
        pass
