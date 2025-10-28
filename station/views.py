from rest_framework import viewsets

from station.models import TrainType, Train, Crew, Station, Route, Journey, Ticket, Order
from station.serializers import (TrainTypeSerializer,
                                 TrainSerializer,
                                 CrewSerializer,
                                 StationSerializer,
                                 RouteListSerializer, RouteSerializer, JourneySerializer, JourneyListSerializer,
                                 JourneyDetailSerializer, TicketSerializer, OrderSerializer)


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer

class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer

class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related("source", "destination")
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteListSerializer
        return RouteSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer

    def get_queryset(self):
        queryset = self.queryset.prefetch_related("route",
                                                          "route__source",
                                                          "route__destination",
                                                          "train")
        if self.action == "list":
            return queryset
        return queryset.prefetch_related("crew")

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        if self.action == "retrieve":
            return JourneyDetailSerializer
        return JourneySerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        if self.action == "list":
            queryset.prefetch_related(
        "tickets__journey")
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
