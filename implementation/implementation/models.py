from django.db import models


class DomainObject(models.Model):
    pass


class Vertex(DomainObject):
    postcodes = models.TextField()
    adress = models.TextField()


class Leg(DomainObject):
    max_weight = models.IntegerField()
    time = models.IntegerField()
    cost = models.IntegerField()
    leg_type = models.TextField()
    from_vertex = models.ForeignKey(Vertex)
    to_vertex = models.ForeignKey(Vertex)
    ends = [from_vertex, to_vertex]


class Route(DomainObject):
    location = models.IntegerField()
    legs = models.ManyToManyField(Leg, through="RouteAux")


class Index(models.Model):
    route = models.ForeignKey(Leg, on_delete=models.CASCADE)
    leg = models.ForeignKey(Route, on_delete=models.CASCADE)
    index = models.IntegerField()


class Product(DomainObject):
    weight = models.IntegerField()
    cost = models.IntegerField()


class Order(DomainObject):
    recipient = models.IntegerField()
    deliver_to = models.ForeignKey(Vertex)
    deliver_from = models.ForeignKey(Vertex)
    follows = models.ForeignKey(Route, null=True, blank=True)
