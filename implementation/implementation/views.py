from django.views.generic import View
from django.http import JsonResponse
from .models import *
import json


class APIEndpoint(View):
    def post(self, request):
        data = json.loads(request.body)
        method = data["method"]
        del data["method"]
        result = getattr(self, method)(**data)
        return JsonResponse(result, safe=False)


def serialize_connection(conn):
    return {
        "vertex": isinstance(conn, Vertex),
        "name": conn.adress if isinstance(conn, Vertex) else conn.leg_type
    }


class OrderListEndpoint(APIEndpoint):
    def get_orders(self):
        orders = History.get_orders(0)
        json = []
        for order in orders:
            json.append({"id": order.id, "from": order.deliver_from.adress,
                         "to": order.deliver_to.adress, "num": order.product_set.count()})
            if order.follows:
                route = []
                for i, leg in enumerate(order.follows.get_legs()):
                    if i == 0:
                        route.append(serialize_connection(leg.from_vertex))
                    route.append(serialize_connection(leg))
                    route.append(serialize_connection(leg.to_vertex))
                json[-1]["route"] = route
        return json


    def get_routes(self, order):
        routes = []
        for i, route in enumerate(Order.objects.get(id=order).route_set.all()):
            cost = 0
            length = 0
            route_type = None
            for leg in route.get_legs():
                cost += leg.cost
                length += leg.time
                if route_type is None:
                    route_type = leg.leg_type
                elif route_type != leg.leg_type:
                    route_type = False
            routes.append({"index": i, "cost": cost,
                           "length": length, "type": route_type})
        return {"order": order, "routes": routes}

    def select_route(self, order, index):
        index = int(index)
        order = Order.objects.get(id=order)
        order.follows = list(order.route_set.all())[index]
        order.save()
        return {}

    def place_order(self, from_adress, to_adress, products):
        from_vertex, to_vertex = [Navigator.get_vertex(el) for el
                                  in (from_adress, to_adress)]
        order = Order(deliver_from=from_vertex, deliver_to=to_vertex)
        order.save()
        for weight in products:
            Product(cost=0, weight=int(weight), order=order).save()
        Navigator.build_routes(order)
        return {}
