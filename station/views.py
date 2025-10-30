from datetime import datetime

from django.db.models import F, Count
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from station.models import TrainType, Train, Crew, Station, Route, Journey, Order
from station.serializers import (TrainTypeSerializer,
                                 TrainSerializer,
                                 CrewSerializer,
                                 StationSerializer,
                                 RouteListSerializer,
                                 RouteSerializer,
                                 JourneySerializer,
                                 JourneyListSerializer,
                                 JourneyDetailSerializer,
                                 OrderSerializer,
                                 OrderListSerializer,
                                 OrderDetailSerializer, TrainListSerializer,
                                 )


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer

class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.select_related("train_type")
    serializer_class = TrainSerializer

    def get_serializer_class(self):
        if self.action in ("list", "retrieve") :
            return TrainListSerializer
        return TrainSerializer

class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related(
        "source", "destination")
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteListSerializer
        return RouteSerializer

    def get_queryset(self):
        queryset = self.queryset
        source_data = self.request.query_params.get("source")
        destination_data = self.request.query_params.get("destination")
        if source_data:
            queryset = queryset.filter(source__name__contains=str(source_data))
        if destination_data:
            queryset = queryset.filter(destination__name__contains=str(destination_data))
        return queryset


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer

    def get_queryset(self):
        queryset = self.queryset.select_related("route__source",
                                                "route__destination",
                                                "train")
        route_param = self.request.query_params.get("route")
        time_param = self.request.query_params.get("date")
        train_param = self.request.query_params.get("train")
        if route_param:
            queryset = queryset.filter(route__id=int(route_param))
        if time_param:
            queryset = queryset.filter(departure_time__gte=
                                       datetime.strptime(
                                           time_param,
                                           "%Y-%m-%d").date())
        if train_param:
            queryset = queryset.filter(train__id=int(train_param))
        if self.action == "list":
            return queryset.annotate(
                tickets_available=F("train__cargo_num")
                                  *F("train__place_in_cargo")
                                  -Count("tickets")
            )
        return queryset.prefetch_related("crew")

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        if self.action == "retrieve":
            return JourneyDetailSerializer
        return JourneySerializer

class OrderPagination(PageNumberPagination):
    page_size = 5
    page_query_param = "page_size"
    max_page_size = 3

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    pagination_class = OrderPagination

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        if self.action in ("list", "retrieve"):
            return queryset.prefetch_related(
                "tickets__journey__route",
                "tickets__journey__train")
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action == "retrieve":
            return OrderDetailSerializer
        return OrderSerializer
