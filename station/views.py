from datetime import datetime

from django.db.models import F, Count
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from station.models import (TrainType,
                            Train,
                            Crew,
                            Station,
                            Route,
                            Journey,
                            Order)
from station.permissions import IsAdminOrIfAuthenticatedReadOnly
from station.serializers import (
    TrainTypeSerializer,
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
    OrderDetailSerializer,
    TrainListSerializer,
    CrewImageSerializer,
    JourneyImageSerializer, CrewListSerializer, CrewDetailSerializer,
)


class TrainTypeViewSet(mixins.CreateModelMixin,
                       mixins.ListModelMixin,
                       GenericViewSet,):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class TrainViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet,):
    queryset = Train.objects.select_related("train_type")
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return TrainListSerializer
        return TrainSerializer


class CrewViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet,):
    queryset = Crew.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer
        if self.action == "retrieve":
            return CrewDetailSerializer
        if self.action == "upload_image":
            return CrewImageSerializer
        return CrewSerializer

    @action(methods=["POST"],
            detail=True,
            url_path="upload-image", permission_classes=[IsAdminUser])
    def upload_image(self, request, pk=None):
        crew = self.get_object()
        serializer = self.get_serializer(crew, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StationViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet,):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class RouteViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet,):
    queryset = Route.objects.all().select_related("source", "destination")
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

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
            queryset = queryset.filter(
                destination__name__contains=str(destination_data)
            )
        return queryset

    @extend_schema(
           parameters=[
               OpenApiParameter(
                   "source",
                   type=str,
                   location=OpenApiParameter.QUERY,
                   description="Filter Routers by source.name",
               ),
               OpenApiParameter(
                   "destination",
                   type=str,
                   location=OpenApiParameter.QUERY,
                   description="Filter Routers by destination.name"
               )
           ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of routes."""
        return super().list(request, *args, **kwargs)


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset.select_related(
            "route__source", "route__destination", "train"
        )
        route_param = self.request.query_params.get("route")
        time_param = self.request.query_params.get("departure_time")
        train_param = self.request.query_params.get("train")
        if route_param:
            queryset = queryset.filter(route__id=int(route_param))
        if time_param:
            queryset = queryset.filter(
                departure_time__gte=datetime.strptime(time_param,
                                                      "%Y-%m-%d").date()
            )
        if train_param:
            queryset = queryset.filter(train__id=int(train_param))
        if self.action == "list":
            return (queryset.annotate(
                    tickets_available=F("train__cargo_num")
                    * F("train__place_in_cargo")
                    - Count("tickets"))
                    )
        return queryset.prefetch_related("crew")

    @action(methods=["POST"],
            detail=True,
            url_path="upload-image")
    def upload_image(self, request, pk=None):
        journey = self.get_object()
        serializer = self.get_serializer(journey, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        if self.action == "retrieve":
            return JourneyDetailSerializer
        if self.action == "upload_image":
            return JourneyImageSerializer
        return JourneySerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "route",
                type=int,
                description="Filter Journeys by route.id",
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                "date",
                type=datetime,
                description="Filter Journeys by data (YYYY-MM-DD)",
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                "train",
                type=int,
                description="Filter Journeys by train.id",
                location=OpenApiParameter.QUERY
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of journeys."""
        return super().list(request, *args, **kwargs)


class OrderPagination(PageNumberPagination):
    page_size = 5
    page_query_param = "page_size"
    max_page_size = 3


class OrderViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   GenericViewSet,):
    queryset = Order.objects.all()
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        if self.action in ("list", "retrieve"):
            return queryset.prefetch_related(
                "tickets__journey__route", "tickets__journey__train"
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action == "retrieve":
            return OrderDetailSerializer
        return OrderSerializer
