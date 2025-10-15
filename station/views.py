from django.shortcuts import render
from rest_framework import viewsets

from station.models import TrainType, Train, Crew, Station
from station.serializers import (TrainTypeSerializer,
                                 TrainSerializer,
                                 CrewSerializer, StationSerializer)


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
