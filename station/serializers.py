from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from station.models import TrainType, Train, Crew, Station, Route, Journey


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = "__all__"


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = "__all__"


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class CrewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "full_name",)


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name",  "latitude", "longitude")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(slug_field="name", read_only=True)
    destination = serializers.SlugRelatedField(slug_field="name", read_only=True)


class JourneySerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(JourneySerializer, self).validate(attrs)
        Journey.validate_departure_time(
            attrs["departure_time"],
            attrs["arrival_time"],
            ValidationError
        )
        return data

    class Meta:
        model = Journey
        fields = "__all__"


class JourneyListSerializer(JourneySerializer):
    route = serializers.SlugRelatedField(slug_field="name", read_only=True)
    train = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Journey
        fields = ("id",
                  "route",
                  "train",
                  "departure_time",
                  "arrival_time")

class JourneyDetailSerializer(JourneySerializer):
    route = serializers.SlugRelatedField(slug_field="name", read_only=True)
    train = TrainSerializer(read_only=True)
    crew = CrewListSerializer(many=True, read_only=True)
