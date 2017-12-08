from django.db import models
import re


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
    from_vertex = models.ForeignKey(Vertex, on_delete=models.CASCADE, related_name="+")
    to_vertex = models.ForeignKey(Vertex, on_delete=models.CASCADE, related_name="+")
    ends = [from_vertex, to_vertex]


class Route(DomainObject):
    location = models.IntegerField()
    legs = models.ManyToManyField(Leg, through="Index")
    order = models.ForeignKey("Order", on_delete=models.CASCADE)


class Index(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    leg = models.ForeignKey(Leg, on_delete=models.CASCADE)
    index = models.IntegerField()


class Product(DomainObject):
    weight = models.IntegerField()
    cost = models.IntegerField()
    order = models.ForeignKey("Order", on_delete=models.CASCADE)


class Order(DomainObject):
    recipient = models.IntegerField()
    deliver_to = models.ForeignKey(Vertex, on_delete=models.CASCADE, related_name="+")
    deliver_from = models.ForeignKey(Vertex, on_delete=models.CASCADE, related_name="+")
    follows = models.ForeignKey(Route, null=True, blank=True, on_delete=models.CASCADE,
                                related_name="+")


class History:
    def get_orders(user):
        return Order.objects.filter(recipient=user)


class Navigator:
    def get_vertex(adress):
        postcode = re.search("\d{6}").group(0)
        vertex = Vertex.objects.filter(postcodes__contains=postcode)[0]
        return vertex
    
    def build_routes(order):
        order.save()
