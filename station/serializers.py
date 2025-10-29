from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from station.models import TrainType, Train, Crew, Station, Route, Journey, Ticket, Order


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = "__all__"


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ("id", "name", "cargo_num", "place_in_cargo", "train_type")

class TrainListSerializer(TrainSerializer):
    train_type = serializers.SlugRelatedField(many=False,
                                              read_only=True,
                                              slug_field="name")


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


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_ticket(
            attrs["cargo"],
            attrs["seat"],
            attrs["journey"],
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(read_only=False,
                              many=True,
                              allow_empty=False)
    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order



class TicketListSerializer(TicketSerializer):
    journey = serializers.CharField(source="journey.route.name", read_only=True)
    train = serializers.CharField(source="journey.train", read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "train", "journey")


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)


class TicketDetailSerializer(TicketSerializer):
    journey = JourneyListSerializer(read_only=True, many=False)


class OrderDetailSerializer(OrderSerializer):
    tickets = TicketDetailSerializer(many=True, read_only=True)
