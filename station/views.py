from django.shortcuts import render
from rest_framework import viewsets

from station.models import TrainType, Train
from station.serializers import TrainTypeSerializer, TrainSerializer


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer

class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer