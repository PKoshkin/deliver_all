from django.db import models
import re
from heapq import heappush, heappop


class DomainObject(models.Model):
    class Meta:
        abstract = True


class Vertex(DomainObject):
    postcodes = models.TextField()
    adress = models.TextField()


class Leg(DomainObject):
    max_weight = models.IntegerField()
    time = models.IntegerField()
    cost = models.IntegerField()
    leg_type = models.TextField()
    from_vertex = models.ForeignKey(Vertex, on_delete=models.CASCADE,
                                    related_name="+")
    to_vertex = models.ForeignKey(Vertex, on_delete=models.CASCADE,
                                  related_name="+")
    ends = [from_vertex, to_vertex]


class Route(DomainObject):
    location = models.IntegerField(default=0)
    legs = models.ManyToManyField(Leg, through="Index")
    order = models.ForeignKey("Order", on_delete=models.CASCADE)

    def get_legs(self):
        return [el.leg for el
                in Index.objects.filter(route=self).order_by("index")]

    def set_legs(self, legs):
        Index.objects.filter(route=self).delete()
        for index, leg in enumerate(legs):
            Index(route=self, leg=leg, index=index).save()


class Index(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    leg = models.ForeignKey(Leg, on_delete=models.CASCADE)
    index = models.IntegerField()


class Product(DomainObject):
    weight = models.IntegerField()
    cost = models.IntegerField()
    order = models.ForeignKey("Order", on_delete=models.CASCADE)


class Order(DomainObject):
    recipient = models.IntegerField(default=0)
    deliver_to = models.ForeignKey(Vertex, on_delete=models.CASCADE,
                                   related_name="+")
    deliver_from = models.ForeignKey(Vertex, on_delete=models.CASCADE,
                                     related_name="+")
    follows = models.ForeignKey(Route, null=True, blank=True,
                                on_delete=models.CASCADE, related_name="+")


class History:
    @staticmethod
    def get_orders(user):
        return Order.objects.filter(recipient=user)


class Navigator:
    @staticmethod
    def get_vertex(adress):
        postcode = re.search("\d{6}", adress).group(0)
        vertex = Vertex.objects.filter(postcodes__contains=postcode)[0]
        return vertex

    @staticmethod
    def build_routes(order):
        objectives = [
            lambda leg: leg.cost,
            lambda leg: leg.time,
            lambda leg: leg.cost if leg.leg_type == "самолет" else False,
        ]
        weight = sum([product.weight for product in order.product_set.all()])
        for objective in objectives:
            def decorated(leg):
                if leg.max_weight < weight:
                    return False
                return objective(leg)
            legs = Navigator._build_route(order.deliver_from,
                                          order.deliver_to,
                                          objective)
            if not legs:
                continue
            route = Route(order=order)
            route.save()
            route.set_legs(legs)
            route.save()

    @staticmethod
    def _build_route(from_vertex, to_vertex, objective):
        came_from = {}
        heap = [(0, from_vertex, None)]
        while len(heap) > 0:
            cost, vertex, incoming = heappop(heap)
            if vertex.id in came_from:
                pass
            came_from[vertex.id] = incoming
            if vertex == to_vertex:
                break
            for leg in Leg.objects.filter(from_vertex=vertex):
                if leg.to_vertex.id in came_from:
                    continue
                leg_cost = objective(leg)
                if leg_cost:
                    heappush(heap, (cost + leg_cost, leg.to_vertex, leg))
        else:
            return None
        legs = []
        cur = to_vertex
        while cur != from_vertex:
            leg = came_from[cur.id]
            legs.append(leg)
            cur = leg.from_vertex
        return reversed(legs)
